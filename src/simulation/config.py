"""
Scenario configuration system.

Supports loading/saving simulation configurations from YAML/JSON files.
"""

from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from pydantic import BaseModel, Field, field_validator

from .models.types import ExperienceLevel, CommunicationOverheadModel
from .agents.developer import DeveloperConfig


class DeveloperConfigModel(BaseModel):
    """Pydantic model for developer configuration."""

    name: Optional[str] = None
    experience_level: str = Field(default="mid", description="junior, mid, senior, staff, principal")
    productivity_rate: float = Field(default=3.5, ge=0.0, description="PRs per week")
    code_quality: float = Field(default=0.85, ge=0.0, le=1.0, description="PR success rate")
    review_capacity: float = Field(default=5.0, ge=0.0, description="Reviews per week")
    onboarding_time: int = Field(default=10, ge=0, description="Weeks to full productivity")
    communication_bandwidth: float = Field(default=7.0, ge=0.0, description="Effective connections")
    availability: float = Field(default=0.70, ge=0.0, le=1.0, description="% time available")
    specializations: List[str] = Field(default_factory=list)
    meeting_hours_per_week: float = Field(default=5.0, ge=0.0, le=40.0)

    @field_validator('experience_level')
    @classmethod
    def validate_experience(cls, v: str) -> str:
        """Validate experience level."""
        valid = {"junior", "mid", "senior", "staff", "principal"}
        if v.lower() not in valid:
            raise ValueError(f"Experience level must be one of: {valid}")
        return v.lower()

    def to_developer_config(self) -> DeveloperConfig:
        """Convert to DeveloperConfig dataclass."""
        return DeveloperConfig(
            name=self.name,
            experience_level=ExperienceLevel(self.experience_level),
            productivity_rate=self.productivity_rate,
            code_quality=self.code_quality,
            review_capacity=self.review_capacity,
            onboarding_time=self.onboarding_time,
            communication_bandwidth=self.communication_bandwidth,
            availability=self.availability,
            specializations=self.specializations,
            meeting_hours_per_week=self.meeting_hours_per_week,
        )


class TeamConfigModel(BaseModel):
    """Configuration for a team of developers."""

    developers: List[DeveloperConfigModel] = Field(default_factory=list)

    # Quick team generation
    count: Optional[int] = Field(default=None, description="Auto-generate N developers")
    distribution: Optional[Dict[str, int]] = Field(
        default=None,
        description="Auto-generate team by experience: {'senior': 2, 'mid': 3, 'junior': 1}"
    )

    def get_developers(self) -> List[DeveloperConfig]:
        """
        Get list of DeveloperConfig objects.

        Can auto-generate based on count or distribution.
        """
        configs = []

        # Explicit developers
        for dev_model in self.developers:
            configs.append(dev_model.to_developer_config())

        # Auto-generate from count
        if self.count is not None and self.count > 0:
            for i in range(self.count):
                configs.append(DeveloperConfig(name=f"Dev-{i+1}"))

        # Auto-generate from distribution
        if self.distribution:
            for level_str, count in self.distribution.items():
                level = ExperienceLevel(level_str.lower())
                for i in range(count):
                    configs.append(DeveloperConfig(
                        name=f"{level_str.capitalize()}-{i+1}",
                        experience_level=level
                    ))

        return configs


class SimulationConfigModel(BaseModel):
    """Configuration for simulation parameters."""

    duration_weeks: int = Field(default=12, ge=1, description="Simulation duration in weeks")
    timestep_days: int = Field(default=1, ge=1, description="Days per timestep")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    communication_loss_factor: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Information loss in communication (0=perfect, 1=total loss)"
    )
    communication_overhead_model: str = Field(
        default="quadratic",
        description="linear, quadratic, or hierarchical"
    )

    @field_validator('communication_overhead_model')
    @classmethod
    def validate_overhead_model(cls, v: str) -> str:
        """Validate communication overhead model."""
        valid = {"linear", "quadratic", "hierarchical"}
        if v.lower() not in valid:
            raise ValueError(f"Overhead model must be one of: {valid}")
        return v.lower()


class ScenarioConfig(BaseModel):
    """
    Complete scenario configuration.

    Can be loaded from YAML/JSON and used to create a simulation.
    """

    name: str = Field(default="Unnamed Scenario", description="Scenario name")
    description: Optional[str] = Field(default=None, description="Scenario description")

    team: TeamConfigModel = Field(default_factory=TeamConfigModel)
    simulation: SimulationConfigModel = Field(default_factory=SimulationConfigModel)

    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Tags for organization")
    author: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_yaml(cls, file_path: Union[str, Path]) -> "ScenarioConfig":
        """
        Load scenario from YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            ScenarioConfig instance

        Raises:
            ImportError: If PyYAML is not installed
            FileNotFoundError: If file doesn't exist
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. Install with: pip install pyyaml")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "ScenarioConfig":
        """
        Load scenario from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            ScenarioConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        return cls(**data)

    def to_yaml(self, file_path: Union[str, Path]) -> None:
        """
        Save scenario to YAML file.

        Args:
            file_path: Path to save YAML file

        Raises:
            ImportError: If PyYAML is not installed
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. Install with: pip install pyyaml")

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)

    def to_json(self, file_path: Union[str, Path], indent: int = 2) -> None:
        """
        Save scenario to JSON file.

        Args:
            file_path: Path to save JSON file
            indent: JSON indentation
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(self.model_dump(), f, indent=indent)

    def get_communication_overhead_model(self) -> CommunicationOverheadModel:
        """Get the communication overhead model enum."""
        return CommunicationOverheadModel(self.simulation.communication_overhead_model)


# Convenience function for creating scenarios
def create_scenario(
    name: str,
    team_size: int = 5,
    duration_weeks: int = 12,
    **kwargs
) -> ScenarioConfig:
    """
    Quickly create a scenario with sensible defaults.

    Args:
        name: Scenario name
        team_size: Number of developers
        duration_weeks: Simulation duration
        **kwargs: Additional configuration overrides

    Returns:
        ScenarioConfig instance
    """
    config = {
        "name": name,
        "team": {"count": team_size},
        "simulation": {"duration_weeks": duration_weeks}
    }
    config.update(kwargs)

    return ScenarioConfig(**config)
