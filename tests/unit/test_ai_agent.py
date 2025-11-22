"""
Unit tests for AI Agent functionality.

Tests AI-specific behaviors including:
- Zero onboarding time
- 24/7 availability
- Cost tracking
- Human review requirements
- Model-specific defaults
"""

import pytest
from src.simulation.agents.ai_agent import AIAgent, AIAgentConfig
from src.simulation.models.types import AIModelType
from src.simulation.base import SimulationContext


class TestAIAgentConfig:
    """Test AIAgentConfig configuration and defaults."""

    def test_default_config(self):
        """Test default AI agent configuration uses model defaults."""
        config = AIAgentConfig()

        assert config.model_type == AIModelType.CLAUDE_SONNET
        assert config.productivity_rate == AIModelType.CLAUDE_SONNET.default_productivity_rate
        assert config.code_quality == AIModelType.CLAUDE_SONNET.default_code_quality
        assert config.supervision_requirement == AIModelType.CLAUDE_SONNET.default_supervision_requirement
        assert config.cost_per_pr == AIModelType.CLAUDE_SONNET.default_cost_per_pr
        assert config.requires_human_review is True
        assert config.can_review_human_prs is False

    def test_custom_config_overrides(self):
        """Test that custom values override model defaults."""
        config = AIAgentConfig(
            model_type=AIModelType.GPT4,
            productivity_rate=15.0,
            code_quality=0.90,
            cost_per_pr=1.0,
        )

        assert config.model_type == AIModelType.GPT4
        assert config.productivity_rate == 15.0  # Custom, not default
        assert config.code_quality == 0.90  # Custom, not default
        assert config.cost_per_pr == 1.0  # Custom, not default

    def test_model_specific_defaults(self):
        """Test that different models have appropriate defaults."""
        opus_config = AIAgentConfig(model_type=AIModelType.CLAUDE_OPUS)
        codellama_config = AIAgentConfig(model_type=AIModelType.CODELLAMA)

        # Opus is slower but higher quality
        assert opus_config.productivity_rate < codellama_config.productivity_rate
        assert opus_config.code_quality > codellama_config.code_quality
        assert opus_config.cost_per_pr > codellama_config.cost_per_pr

    def test_to_developer_config_conversion(self):
        """Test conversion to DeveloperConfig."""
        ai_config = AIAgentConfig(name="TestAI")
        dev_config = ai_config.to_developer_config()

        # AI agents have specific developer config characteristics
        assert dev_config.availability == 1.0  # 24/7
        assert dev_config.meeting_hours_per_week == 0.0  # No meetings
        assert dev_config.onboarding_time == 0  # Instant
        assert dev_config.current_productivity_multiplier == 1.0  # Full capacity
        assert dev_config.communication_bandwidth == 50.0  # High scalability


class TestAIAgent:
    """Test AIAgent behavior and functionality."""

    def test_agent_initialization(self):
        """Test AI agent initializes correctly."""
        config = AIAgentConfig(name="TestAgent", model_type=AIModelType.GPT4)
        agent = AIAgent(config=config)

        assert agent.config.name == "TestAgent"
        assert agent.ai_config.model_type == AIModelType.GPT4
        assert agent.is_fully_onboarded is True  # AI agents start fully onboarded
        assert agent.total_cost_incurred == 0.0

    def test_no_onboarding_required(self):
        """Test that AI agents don't need onboarding."""
        agent = AIAgent()
        context = SimulationContext(current_day=0, current_week=0)

        # Should be ready immediately
        assert agent.is_fully_onboarded is True
        assert agent.config.current_productivity_multiplier == 1.0

        # Onboarding update should not change anything
        agent._update_onboarding(context)
        assert agent.is_fully_onboarded is True
        assert agent.config.current_productivity_multiplier == 1.0

    def test_pr_creation_tracks_cost(self):
        """Test that creating PRs tracks costs."""
        config = AIAgentConfig(model_type=AIModelType.CLAUDE_SONNET)
        agent = AIAgent(config=config)
        context = SimulationContext(current_day=1, current_week=0)

        initial_cost = agent.total_cost_incurred
        pr = agent.create_pr(context)

        # Cost should have increased
        assert agent.total_cost_incurred > initial_cost
        assert agent.total_cost_incurred == config.cost_per_pr

        # PR should be marked as AI-generated
        assert pr.metadata.get('created_by_ai') is True
        assert pr.metadata.get('ai_model') == AIModelType.CLAUDE_SONNET.value
        assert pr.metadata.get('requires_human_review') is True

    def test_multiple_prs_accumulate_cost(self):
        """Test that costs accumulate across multiple PRs."""
        config = AIAgentConfig(cost_per_pr=0.50)
        agent = AIAgent(config=config)
        context = SimulationContext(current_day=1, current_week=0)

        # Create 3 PRs
        for _ in range(3):
            agent.create_pr(context)

        assert agent.total_cost_incurred == 1.50  # 3 * $0.50
        assert agent.total_prs_created == 3

    def test_can_review_pr_rules(self):
        """Test AI agent review permission logic."""
        agent = AIAgent(config=AIAgentConfig(
            can_review_human_prs=False,
            can_review_ai_prs=False
        ))

        # Create a human PR (no metadata)
        from src.simulation.models.work import PullRequest
        human_pr = PullRequest(author_id="human-1")
        assert agent.can_review_pr(human_pr) is False

        # Create an AI PR
        ai_pr = PullRequest(author_id="ai-1")
        ai_pr.metadata = {'created_by_ai': True}
        assert agent.can_review_pr(ai_pr) is False

        # Update config to allow AI reviews
        agent.ai_config.can_review_ai_prs = True
        assert agent.can_review_pr(ai_pr) is True
        assert agent.can_review_pr(human_pr) is False  # Still can't review human

    def test_supervision_hours_calculation(self):
        """Test calculation of human review hours needed."""
        config = AIAgentConfig(supervision_requirement=0.25)
        agent = AIAgent(config=config)
        context = SimulationContext(current_day=1, current_week=0)

        pr = agent.create_pr(context)
        hours = agent.get_supervision_hours_for_pr(pr)

        # Base review time (2 hrs) * supervision requirement (0.25) = 0.5 hrs
        assert hours == 0.5

    def test_get_stats_includes_ai_metrics(self):
        """Test that stats include AI-specific metrics."""
        config = AIAgentConfig(
            name="StatTest",
            model_type=AIModelType.CLAUDE_OPUS,
            cost_per_pr=0.80
        )
        agent = AIAgent(config=config)
        context = SimulationContext(current_day=1, current_week=0)

        # Create a PR to accumulate some cost
        agent.create_pr(context)

        stats = agent.get_stats()

        # Check base stats
        assert stats['agent_id'] == agent.agent_id
        assert stats['name'] == "StatTest"

        # Check AI-specific stats
        assert stats['agent_type'] == "ai"
        assert stats['model_type'] == "claude-opus"
        assert stats['total_cost_incurred'] == 0.80
        assert stats['avg_cost_per_pr'] == 0.80
        assert stats['supervision_requirement'] == config.supervision_requirement
        assert stats['requires_human_review'] is True
        assert stats['can_review_human_prs'] is False

    def test_repr_format(self):
        """Test string representation of AI agent."""
        config = AIAgentConfig(name="ReprTest", model_type=AIModelType.GPT4)
        agent = AIAgent(config=config)

        repr_str = repr(agent)
        assert "ReprTest" in repr_str
        assert "gpt4" in repr_str
        assert "AIAgent" in repr_str


class TestAIModelTypes:
    """Test AI model type enum and its properties."""

    def test_all_models_have_defaults(self):
        """Test that all model types have complete defaults."""
        for model in AIModelType:
            assert model.default_productivity_rate > 0
            assert 0 < model.default_code_quality <= 1.0
            assert 0 <= model.default_supervision_requirement <= 1.0
            assert model.default_cost_per_pr >= 0

    def test_productivity_rates_realistic(self):
        """Test that productivity rates are in realistic ranges."""
        for model in AIModelType:
            # AI agents work 24/7, so rates should be higher than humans (3.5 baseline)
            # but not absurdly high
            assert 5.0 <= model.default_productivity_rate <= 15.0

    def test_code_quality_realistic(self):
        """Test that code quality is in realistic ranges."""
        for model in AIModelType:
            # AI quality should be good but not perfect
            # Lower than top human developers (0.95)
            assert 0.75 <= model.default_code_quality <= 0.90

    def test_cost_variations(self):
        """Test that different models have different costs."""
        costs = [model.default_cost_per_pr for model in AIModelType]

        # Should have variation
        assert min(costs) < max(costs)

        # CodeLlama should be cheapest (open source)
        assert AIModelType.CODELLAMA.default_cost_per_pr == min(costs)

        # Opus should be most expensive (highest quality)
        assert AIModelType.CLAUDE_OPUS.default_cost_per_pr == max(costs)
