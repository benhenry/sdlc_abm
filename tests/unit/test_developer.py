"""
Unit tests for the Developer agent.
"""

import pytest

from src.simulation.agents.developer import Developer, DeveloperConfig
from src.simulation.models.types import ExperienceLevel
from src.simulation.base import SimulationContext


class TestDeveloperConfig:
    """Test DeveloperConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DeveloperConfig()

        assert config.experience_level == ExperienceLevel.MID
        assert config.productivity_rate == 3.5
        assert config.code_quality == 0.85
        assert config.review_capacity == 5.0
        assert config.onboarding_time == 10
        assert config.availability == 0.70

    def test_custom_config(self):
        """Test custom configuration."""
        config = DeveloperConfig(
            name="Alice",
            experience_level=ExperienceLevel.SENIOR,
            productivity_rate=4.0,
            code_quality=0.90
        )

        assert config.name == "Alice"
        assert config.experience_level == ExperienceLevel.SENIOR
        assert config.productivity_rate == 4.0
        assert config.code_quality == 0.90


class TestDeveloper:
    """Test Developer agent."""

    def test_developer_creation(self):
        """Test creating a developer agent."""
        dev = Developer()

        assert dev.agent_id is not None
        assert dev.config is not None
        assert dev.total_prs_created == 0
        assert dev.total_prs_merged == 0
        assert dev.weeks_in_role == 0

    def test_developer_with_config(self):
        """Test creating a developer with custom config."""
        config = DeveloperConfig(
            name="Bob",
            experience_level=ExperienceLevel.PRINCIPAL
        )
        dev = Developer(config=config)

        assert dev.config.name == "Bob"
        assert dev.config.experience_level == ExperienceLevel.PRINCIPAL

    def test_on_added_to_simulation(self):
        """Test developer initialization when added to simulation."""
        dev = Developer()
        dev.on_added_to_simulation(timestep=0)

        assert dev.created_at == 0
        assert dev.hours_available_this_week > 0

    def test_onboarding_progress(self):
        """Test onboarding progression."""
        config = DeveloperConfig(onboarding_time=4)  # 4 weeks
        dev = Developer(config=config)
        dev.on_added_to_simulation(timestep=0)

        context = SimulationContext(current_day=0, current_week=0)

        # Initially not onboarded
        assert not dev.is_fully_onboarded
        assert dev.config.current_productivity_multiplier == 0.0

        # After 2 weeks (50% through onboarding)
        dev.weeks_in_role = 2
        dev._update_onboarding(context)
        assert not dev.is_fully_onboarded
        assert dev.config.current_productivity_multiplier == 0.5

        # After 4 weeks (fully onboarded)
        dev.weeks_in_role = 4
        dev._update_onboarding(context)
        assert dev.is_fully_onboarded
        assert dev.config.current_productivity_multiplier == 1.0

    def test_create_pr(self):
        """Test PR creation."""
        dev = Developer()
        dev.on_added_to_simulation(timestep=0)

        context = SimulationContext(current_day=5, current_week=0)
        pr = dev.create_pr(context)

        assert pr is not None
        assert pr.author_id == dev.agent_id
        assert pr.created_at == 5
        assert dev.total_prs_created == 1
        assert len(dev.active_prs) == 1

    def test_merge_pr(self):
        """Test PR merging."""
        dev = Developer()
        dev.on_added_to_simulation(timestep=0)

        context = SimulationContext(current_day=5, current_week=0)
        pr = dev.create_pr(context)

        # Merge the PR
        merge_context = SimulationContext(current_day=8, current_week=1)
        dev.merge_pr(pr, merge_context)

        assert pr.is_merged
        assert pr.merged_at == 8
        assert dev.total_prs_merged == 1
        assert len(dev.active_prs) == 0

    def test_revert_pr(self):
        """Test PR reversion."""
        dev = Developer()
        dev.on_added_to_simulation(timestep=0)

        context = SimulationContext(current_day=5, current_week=0)
        pr = dev.create_pr(context)
        pr.merge(context.current_day)

        # Revert the PR
        revert_context = SimulationContext(current_day=10, current_week=1)
        dev.revert_pr(pr, revert_context)

        assert pr.was_reverted
        assert pr.reverted_at == 10
        assert dev.total_prs_reverted == 1

    def test_get_stats(self):
        """Test getting developer statistics."""
        config = DeveloperConfig(name="Charlie")
        dev = Developer(config=config)
        dev.on_added_to_simulation(timestep=0)

        stats = dev.get_stats()

        assert stats["name"] == "Charlie"
        assert stats["weeks_in_role"] == 0
        assert stats["total_prs_created"] == 0
        assert "agent_id" in stats
        assert "experience_level" in stats


class TestExperienceLevel:
    """Test ExperienceLevel enum."""

    def test_experience_multipliers(self):
        """Test that each experience level has a multiplier."""
        assert ExperienceLevel.JUNIOR.multiplier == 0.5
        assert ExperienceLevel.MID.multiplier == 1.0
        assert ExperienceLevel.SENIOR.multiplier == 1.3
        assert ExperienceLevel.STAFF.multiplier == 1.5
        assert ExperienceLevel.PRINCIPAL.multiplier == 1.7
