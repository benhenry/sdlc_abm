"""Simulation execution endpoints

API endpoints for running and monitoring simulations.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db_session
from ..models import Scenario, SimulationRun, SimulationStatus
from ..schemas import (
    SimulationRunCreate,
    SimulationRunListResponse,
    SimulationRunResponse,
)
from ..tasks import run_simulation_task

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("/run", response_model=SimulationRunResponse, status_code=status.HTTP_201_CREATED)
async def run_simulation(
    simulation_data: SimulationRunCreate,
    db: AsyncSession = Depends(get_db_session)
) -> SimulationRun:
    """Start a new simulation

    Creates a simulation run record and enqueues it for background execution.
    """
    # Create simulation run record
    simulation = SimulationRun(
        scenario_id=simulation_data.scenario_id,
        status=SimulationStatus.PENDING,
        progress=0.0,
        config_json=simulation_data.config_json,
    )

    db.add(simulation)
    await db.commit()
    await db.refresh(simulation)

    # Enqueue Celery task
    task = run_simulation_task.apply_async(
        args=[str(simulation.id), simulation_data.config_json],
        task_id=str(simulation.id)
    )

    # Update status to running
    simulation.status = SimulationStatus.RUNNING
    simulation.started_at = datetime.utcnow()
    await db.commit()
    await db.refresh(simulation)

    return simulation


@router.get("", response_model=SimulationRunListResponse)
async def list_simulations(
    skip: int = 0,
    limit: int = 100,
    status_filter: SimulationStatus | None = None,
    db: AsyncSession = Depends(get_db_session)
) -> SimulationRunListResponse:
    """List simulation runs

    Returns paginated list of simulation runs with optional status filter.
    """
    # Build query
    query = select(SimulationRun)

    if status_filter:
        query = query.where(SimulationRun.status == status_filter)

    # Get total count
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(SimulationRun.created_at.desc())
    result = await db.execute(query)
    simulations = result.scalars().all()

    return SimulationRunListResponse(simulations=simulations, total=total)


@router.get("/{simulation_id}", response_model=SimulationRunResponse)
async def get_simulation(
    simulation_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> SimulationRun:
    """Get simulation run by ID

    Returns details and results of a specific simulation run.
    """
    query = select(SimulationRun).where(SimulationRun.id == simulation_id)
    result = await db.execute(query)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found"
        )

    # Check task status if still running
    if simulation.status == SimulationStatus.RUNNING:
        from celery.result import AsyncResult
        task_result = AsyncResult(str(simulation_id))

        # Update from task state
        if task_result.state == "PROGRESS":
            meta = task_result.info or {}
            simulation.progress = meta.get("progress", simulation.progress)
        elif task_result.state == "SUCCESS":
            # Task completed, update database
            result_data = task_result.result
            simulation.status = SimulationStatus.COMPLETED
            simulation.progress = 1.0
            simulation.completed_at = datetime.utcnow()
            simulation.results_json = result_data
            await db.commit()
        elif task_result.state == "FAILURE":
            # Task failed, update database
            simulation.status = SimulationStatus.FAILED
            simulation.completed_at = datetime.utcnow()
            simulation.error_message = str(task_result.info)
            await db.commit()

        await db.refresh(simulation)

    return simulation


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete simulation run

    Cancels running simulation (if possible) and deletes the record.
    """
    query = select(SimulationRun).where(SimulationRun.id == simulation_id)
    result = await db.execute(query)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found"
        )

    # Try to cancel if still running
    if simulation.status in [SimulationStatus.PENDING, SimulationStatus.RUNNING]:
        from celery.result import AsyncResult
        task_result = AsyncResult(str(simulation_id))
        task_result.revoke(terminate=True)

    await db.delete(simulation)
    await db.commit()


@router.post("/{simulation_id}/cancel", response_model=SimulationRunResponse)
async def cancel_simulation(
    simulation_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> SimulationRun:
    """Cancel a running simulation

    Attempts to cancel a pending or running simulation.
    """
    query = select(SimulationRun).where(SimulationRun.id == simulation_id)
    result = await db.execute(query)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found"
        )

    if simulation.status not in [SimulationStatus.PENDING, SimulationStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel simulation with status {simulation.status}"
        )

    # Revoke Celery task
    from celery.result import AsyncResult
    task_result = AsyncResult(str(simulation_id))
    task_result.revoke(terminate=True)

    # Update status
    simulation.status = SimulationStatus.FAILED
    simulation.completed_at = datetime.utcnow()
    simulation.error_message = "Cancelled by user"

    await db.commit()
    await db.refresh(simulation)

    return simulation
