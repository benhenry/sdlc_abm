"""
Type definitions and enums for the SDLC simulation.
"""

from enum import Enum


class ExperienceLevel(Enum):
    """Developer experience levels."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"

    @property
    def multiplier(self) -> float:
        """
        Productivity multiplier for this experience level.

        These are defaults and can be overridden in agent configuration.
        """
        multipliers = {
            ExperienceLevel.JUNIOR: 0.5,
            ExperienceLevel.MID: 1.0,
            ExperienceLevel.SENIOR: 1.3,
            ExperienceLevel.STAFF: 1.5,
            ExperienceLevel.PRINCIPAL: 1.7,
        }
        return multipliers[self]


class PRState(Enum):
    """Pull request states."""
    DRAFT = "draft"
    OPEN = "open"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    MERGED = "merged"
    REVERTED = "reverted"
    CLOSED = "closed"


class CommunicationOverheadModel(Enum):
    """Models for how communication overhead scales with team size."""
    LINEAR = "linear"          # O(n)
    QUADRATIC = "quadratic"    # O(n²) - default, realistic
    HIERARCHICAL = "hierarchical"  # O(log n) - well-structured orgs


class AIModelType(Enum):
    """
    AI model types for agentic development.

    Focus on advanced/specialized models for real-world software development.
    """
    GPT4 = "gpt4"                    # OpenAI GPT-4 - general purpose, high capability
    CLAUDE_SONNET = "claude-sonnet"  # Anthropic Claude Sonnet - balanced speed/quality
    CLAUDE_OPUS = "claude-opus"      # Anthropic Claude Opus - highest quality
    CODELLAMA = "codellama"          # Meta CodeLlama - specialized for code
    CUSTOM = "custom"                # Custom or fine-tuned model

    @property
    def default_productivity_rate(self) -> float:
        """
        Default PRs per week for this AI model type.

        AI agents can work 24/7, so base rates are higher than humans.
        These are defaults and can be overridden in configuration.
        """
        rates = {
            AIModelType.GPT4: 8.0,              # ~1.1 PRs/day
            AIModelType.CLAUDE_SONNET: 10.0,    # ~1.4 PRs/day (faster)
            AIModelType.CLAUDE_OPUS: 6.0,       # ~0.85 PRs/day (more thorough)
            AIModelType.CODELLAMA: 12.0,        # ~1.7 PRs/day (code-specialized)
            AIModelType.CUSTOM: 8.0,            # Default baseline
        }
        return rates[self]

    @property
    def default_code_quality(self) -> float:
        """
        Default code quality (success rate) for this AI model.

        These represent realistic quality levels for advanced AI models.
        Values between 0.75-0.90, lower than top human developers.
        """
        qualities = {
            AIModelType.GPT4: 0.82,
            AIModelType.CLAUDE_SONNET: 0.85,
            AIModelType.CLAUDE_OPUS: 0.88,
            AIModelType.CODELLAMA: 0.80,
            AIModelType.CUSTOM: 0.82,
        }
        return qualities[self]

    @property
    def default_supervision_requirement(self) -> float:
        """
        How much human oversight is needed (0-1).

        Higher values mean more human review time required per PR.
        0.0 = fully autonomous, 1.0 = requires extensive human review.
        """
        supervision = {
            AIModelType.GPT4: 0.3,
            AIModelType.CLAUDE_SONNET: 0.25,
            AIModelType.CLAUDE_OPUS: 0.2,
            AIModelType.CODELLAMA: 0.35,
            AIModelType.CUSTOM: 0.3,
        }
        return supervision[self]

    @property
    def default_cost_per_pr(self) -> float:
        """
        Approximate API cost per PR in USD.

        Based on typical token usage for code generation tasks.
        These are estimates and can vary significantly.
        """
        costs = {
            AIModelType.GPT4: 0.50,
            AIModelType.CLAUDE_SONNET: 0.30,
            AIModelType.CLAUDE_OPUS: 0.80,
            AIModelType.CODELLAMA: 0.10,  # Open source, compute cost
            AIModelType.CUSTOM: 0.30,
        }
        return costs[self]
