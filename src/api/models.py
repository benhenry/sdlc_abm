"""SQLAlchemy ORM models

Database models for scenarios, simulation runs, comparisons, and imported datasets.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import ARRAY, Column, DateTime, Enum, Float, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .database import Base


class SimulationStatus(str, enum.Enum):
    """Status of a simulation or comparison run"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportSourceType(str, enum.Enum):
    """Type of data import source"""
    GITHUB = "github"
    GITLAB = "gitlab"
    CSV = "csv"


class Scenario(Base):
    """User-saved simulation configuration

    Stores complete scenario configuration as JSONB for flexibility.
    """
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    config_json = Column(JSONB, nullable=False)  # Complete ScenarioConfig
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Scenario(id={self.id}, name='{self.name}')>"


class SimulationRun(Base):
    """Simulation execution history

    Tracks individual simulation runs with status, progress, and results.
    """
    __tablename__ = "simulation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Nullable for ad-hoc runs
    status = Column(Enum(SimulationStatus), nullable=False, default=SimulationStatus.PENDING, index=True)
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    results_json = Column(JSONB, nullable=True)  # Complete simulation results
    config_json = Column(JSONB, nullable=False)  # Snapshot of config used
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<SimulationRun(id={self.id}, status={self.status})>"


class Comparison(Base):
    """Multi-scenario comparison

    Stores comparison of multiple scenarios with aggregated results.
    """
    __tablename__ = "comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    scenario_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)  # List of scenario IDs
    status = Column(Enum(SimulationStatus), nullable=False, default=SimulationStatus.PENDING)
    results_json = Column(JSONB, nullable=True)  # Comparison results with insights
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Comparison(id={self.id}, name='{self.name}')>"


class ImportedDataset(Base):
    """Historical data imported from external sources

    Stores metrics extracted from GitHub, GitLab, or CSV files.
    """
    __tablename__ = "imported_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(Enum(ImportSourceType), nullable=False, index=True)
    source_name = Column(String(255), nullable=False)  # Repo name or file name
    import_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    metrics_json = Column(JSONB, nullable=False)  # DeveloperMetrics and team stats
    suggested_config_json = Column(JSONB, nullable=True)  # Auto-generated scenario config
    raw_data_json = Column(JSONB, nullable=True)  # Original raw data for reference

    def __repr__(self):
        return f"<ImportedDataset(id={self.id}, source='{self.source_name}')>"
