"""Scenario management endpoints

CRUD operations for simulation scenarios.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db_session
from ..models import Scenario
from ..schemas import (
    ScenarioCreate,
    ScenarioListResponse,
    ScenarioResponse,
    ScenarioUpdate,
)

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario_data: ScenarioCreate,
    db: AsyncSession = Depends(get_db_session)
) -> Scenario:
    """Create a new scenario

    Saves a simulation scenario configuration to the database.
    """
    scenario = Scenario(
        name=scenario_data.name,
        description=scenario_data.description,
        config_json=scenario_data.config_json,
    )

    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)

    return scenario


@router.get("", response_model=ScenarioListResponse)
async def list_scenarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
) -> ScenarioListResponse:
    """List all scenarios

    Returns paginated list of all saved scenarios.
    """
    # Get total count
    count_query = select(Scenario)
    result = await db.execute(count_query)
    total = len(result.scalars().all())

    # Get paginated scenarios
    query = select(Scenario).offset(skip).limit(limit).order_by(Scenario.created_at.desc())
    result = await db.execute(query)
    scenarios = result.scalars().all()

    return ScenarioListResponse(scenarios=scenarios, total=total)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> Scenario:
    """Get scenario by ID

    Returns details of a specific scenario.
    """
    query = select(Scenario).where(Scenario.id == scenario_id)
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    return scenario


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
    scenario_data: ScenarioUpdate,
    db: AsyncSession = Depends(get_db_session)
) -> Scenario:
    """Update scenario

    Updates an existing scenario's name, description, or configuration.
    """
    query = select(Scenario).where(Scenario.id == scenario_id)
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    # Update fields if provided
    if scenario_data.name is not None:
        scenario.name = scenario_data.name
    if scenario_data.description is not None:
        scenario.description = scenario_data.description
    if scenario_data.config_json is not None:
        scenario.config_json = scenario_data.config_json

    await db.commit()
    await db.refresh(scenario)

    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> None:
    """Delete scenario

    Permanently deletes a scenario from the database.
    """
    query = select(Scenario).where(Scenario.id == scenario_id)
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    await db.delete(scenario)
    await db.commit()


@router.post("/from-template", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_from_template(
    template_name: str,
    scenario_name: str,
    db: AsyncSession = Depends(get_db_session)
) -> Scenario:
    """Create scenario from template

    Creates a new scenario by loading a template YAML file.
    """
    import os
    from pathlib import Path
    import yaml

    # Load template from data/scenarios directory
    project_root = Path(__file__).parent.parent.parent.parent
    template_path = project_root / "data" / "scenarios" / f"{template_name}.yaml"

    if not template_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_name}' not found"
        )

    with open(template_path, 'r') as f:
        config_data = yaml.safe_load(f)

    # Create scenario from template
    scenario = Scenario(
        name=scenario_name,
        description=f"Created from template: {template_name}",
        config_json=config_data,
    )

    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)

    return scenario
