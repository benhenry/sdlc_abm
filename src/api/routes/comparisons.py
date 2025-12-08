"""Comparison endpoints

API endpoints for comparing multiple scenarios.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db_session
from ..models import Comparison, Scenario, SimulationStatus
from ..schemas import (
    ComparisonCreate,
    ComparisonListResponse,
    ComparisonResponse,
)
from ..tasks import run_comparison_task

router = APIRouter(prefix="/api/comparisons", tags=["comparisons"])


@router.post("", response_model=ComparisonResponse, status_code=status.HTTP_201_CREATED)
async def create_comparison(
    comparison_data: ComparisonCreate,
    db: AsyncSession = Depends(get_db_session)
) -> Comparison:
    """Create and run a new comparison

    Compares multiple scenarios and provides insights on differences.
    """
    # Verify all scenarios exist
    scenario_configs = []
    for scenario_id in comparison_data.scenario_ids:
        query = select(Scenario).where(Scenario.id == scenario_id)
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found"
            )

        scenario_configs.append(scenario.config_json)

    # Create comparison record
    comparison = Comparison(
        name=comparison_data.name,
        scenario_ids=comparison_data.scenario_ids,
        status=SimulationStatus.PENDING,
    )

    db.add(comparison)
    await db.commit()
    await db.refresh(comparison)

    # Enqueue Celery task
    task = run_comparison_task.apply_async(
        args=[str(comparison.id), scenario_configs],
        task_id=str(comparison.id)
    )

    # Update status to running
    comparison.status = SimulationStatus.RUNNING
    await db.commit()
    await db.refresh(comparison)

    return comparison


@router.get("", response_model=ComparisonListResponse)
async def list_comparisons(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
) -> ComparisonListResponse:
    """List all comparisons

    Returns paginated list of comparison runs.
    """
    # Get total count
    count_query = select(Comparison)
    result = await db.execute(count_query)
    total = len(result.scalars().all())

    # Get paginated comparisons
    query = select(Comparison).offset(skip).limit(limit).order_by(Comparison.created_at.desc())
    result = await db.execute(query)
    comparisons = result.scalars().all()

    return ComparisonListResponse(comparisons=comparisons, total=total)


@router.get("/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison(
    comparison_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> Comparison:
    """Get comparison by ID

    Returns results and insights for a specific comparison.
    """
    query = select(Comparison).where(Comparison.id == comparison_id)
    result = await db.execute(query)
    comparison = result.scalar_one_or_none()

    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison {comparison_id} not found"
        )

    # Check task status if still running
    if comparison.status == SimulationStatus.RUNNING:
        from celery.result import AsyncResult
        task_result = AsyncResult(str(comparison_id))

        if task_result.state == "SUCCESS":
            # Task completed, update database
            result_data = task_result.result
            comparison.status = SimulationStatus.COMPLETED
            comparison.completed_at = datetime.utcnow()
            comparison.results_json = result_data
            await db.commit()
        elif task_result.state == "FAILURE":
            # Task failed, update database
            comparison.status = SimulationStatus.FAILED
            comparison.completed_at = datetime.utcnow()
            await db.commit()

        await db.refresh(comparison)

    return comparison


@router.delete("/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comparison(
    comparison_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete comparison

    Permanently deletes a comparison from the database.
    """
    query = select(Comparison).where(Comparison.id == comparison_id)
    result = await db.execute(query)
    comparison = result.scalar_one_or_none()

    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison {comparison_id} not found"
        )

    # Try to cancel if still running
    if comparison.status in [SimulationStatus.PENDING, SimulationStatus.RUNNING]:
        from celery.result import AsyncResult
        task_result = AsyncResult(str(comparison_id))
        task_result.revoke(terminate=True)

    await db.delete(comparison)
    await db.commit()
