"""Pydantic schemas for API request/response validation

Defines schemas for all API endpoints with proper validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .models import ImportSourceType, SimulationStatus


# Scenario schemas
class ScenarioCreate(BaseModel):
    """Request schema for creating a new scenario"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Dict[str, Any] = Field(..., description="Complete ScenarioConfig as dict")


class ScenarioUpdate(BaseModel):
    """Request schema for updating a scenario"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class ScenarioResponse(BaseModel):
    """Response schema for scenario"""
    id: UUID
    name: str
    description: Optional[str]
    config_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScenarioListResponse(BaseModel):
    """Response schema for list of scenarios"""
    scenarios: List[ScenarioResponse]
    total: int


# Simulation run schemas
class SimulationRunCreate(BaseModel):
    """Request schema for starting a new simulation"""
    scenario_id: Optional[UUID] = Field(None, description="Optional existing scenario ID")
    config_json: Dict[str, Any] = Field(..., description="Scenario configuration to run")


class SimulationRunResponse(BaseModel):
    """Response schema for simulation run"""
    id: UUID
    scenario_id: Optional[UUID]
    status: SimulationStatus
    progress: float = Field(..., ge=0.0, le=1.0)
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    results_json: Optional[Dict[str, Any]]
    config_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class SimulationRunListResponse(BaseModel):
    """Response schema for list of simulation runs"""
    simulations: List[SimulationRunResponse]
    total: int


# Comparison schemas
class ComparisonCreate(BaseModel):
    """Request schema for creating a comparison"""
    name: str = Field(..., min_length=1, max_length=255)
    scenario_ids: List[UUID] = Field(..., min_items=2, description="At least 2 scenarios to compare")


class ComparisonResponse(BaseModel):
    """Response schema for comparison"""
    id: UUID
    name: str
    scenario_ids: List[UUID]
    status: SimulationStatus
    results_json: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ComparisonListResponse(BaseModel):
    """Response schema for list of comparisons"""
    comparisons: List[ComparisonResponse]
    total: int


# Import schemas
class CSVImportCreate(BaseModel):
    """Request schema for CSV import"""
    file_name: str
    file_data: str = Field(..., description="Base64 encoded CSV data or raw CSV text")
    column_mapping: Optional[Dict[str, str]] = Field(
        None,
        description="Optional mapping of CSV columns to expected fields"
    )


class GitHubImportCreate(BaseModel):
    """Request schema for GitHub import"""
    repo_url: str = Field(..., description="GitHub repository URL (e.g., owner/repo)")
    token: str = Field(..., description="GitHub personal access token")
    start_date: Optional[str] = Field(None, description="ISO date to start fetching PRs from")
    end_date: Optional[str] = Field(None, description="ISO date to stop fetching PRs")


class GitLabImportCreate(BaseModel):
    """Request schema for GitLab import"""
    repo_url: str = Field(..., description="GitLab repository URL or project ID")
    token: str = Field(..., description="GitLab personal access token")
    start_date: Optional[str] = Field(None, description="ISO date to start fetching MRs from")
    end_date: Optional[str] = Field(None, description="ISO date to stop fetching MRs")


class ImportedDatasetResponse(BaseModel):
    """Response schema for imported dataset"""
    id: UUID
    source_type: ImportSourceType
    source_name: str
    import_date: datetime
    metrics_json: Dict[str, Any]
    suggested_config_json: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ImportedDatasetListResponse(BaseModel):
    """Response schema for list of imported datasets"""
    datasets: List[ImportedDatasetResponse]
    total: int


# Template schemas
class TemplateInfo(BaseModel):
    """Response schema for template information"""
    name: str
    path: str
    description: Optional[str]
    config: Dict[str, Any]


class TemplateListResponse(BaseModel):
    """Response schema for list of templates"""
    templates: List[TemplateInfo]
    total: int


# Calibration schemas
class CalibrationRequest(BaseModel):
    """Request schema for calibration"""
    imported_dataset_id: UUID = Field(..., description="Historical dataset to calibrate against")
    scenario_id: UUID = Field(..., description="Scenario to calibrate")
    auto_adjust: bool = Field(True, description="Automatically suggest parameter adjustments")


class CalibrationResult(BaseModel):
    """Response schema for calibration result"""
    accuracy_score: float = Field(..., description="Overall accuracy (0-1)")
    metrics_comparison: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Comparison of predicted vs actual metrics"
    )
    suggested_adjustments: Optional[Dict[str, Any]] = Field(
        None,
        description="Suggested parameter changes to improve accuracy"
    )
    detailed_report: str = Field(..., description="Human-readable calibration report")


# WebSocket message schemas
class ProgressUpdate(BaseModel):
    """WebSocket message for simulation progress updates"""
    type: str = "progress"
    simulation_id: UUID
    current_step: int
    total_steps: int
    progress: float = Field(..., ge=0.0, le=1.0)
    status: SimulationStatus
    current_metrics: Optional[Dict[str, Any]] = None


class SimulationCompleted(BaseModel):
    """WebSocket message for simulation completion"""
    type: str = "completed"
    simulation_id: UUID
    results: Dict[str, Any]


class SimulationError(BaseModel):
    """WebSocket message for simulation errors"""
    type: str = "error"
    simulation_id: UUID
    error_message: str


# Error schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_type: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
