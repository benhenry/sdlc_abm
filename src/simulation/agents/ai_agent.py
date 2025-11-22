"""
AI Agent model for agentic software development.

AI Agents extend the Developer class with characteristics specific to
AI-powered code generation and assistance:
- 24/7 availability
- Zero onboarding time
- Higher scalability
- Require human review
- Different cost structure
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from .developer import Developer, DeveloperConfig
from ..base import SimulationContext
from ..models.types import AIModelType, ExperienceLevel
from ..models.work import PullRequest

if TYPE_CHECKING:
    from ..engine import SDLCSimulation


@dataclass
class AIAgentConfig:
    """
    Configuration for an AI Agent.

    AI agents have different characteristics than human developers:
    - 24/7 availability
    - No onboarding time
    - Require human supervision
    - Cost per operation
    """
    # Identity
    name: Optional[str] = None
    model_type: AIModelType = AIModelType.CLAUDE_SONNET

    # Productivity (defaults from model type, but can be overridden)
    productivity_rate: Optional[float] = None  # PRs per week (24/7 operation)
    code_quality: Optional[float] = None  # PR success rate (0-1)

    # AI-specific attributes
    supervision_requirement: Optional[float] = None  # 0-1, human oversight needed
    cost_per_pr: Optional[float] = None  # USD cost per PR

    # Advanced configuration
    requires_human_review: bool = True  # All AI PRs need human approval
    can_review_human_prs: bool = False  # AI can't review human work
    can_review_ai_prs: bool = False  # AI typically shouldn't review AI work

    # Context and specialization
    specializations: list[str] = field(default_factory=list)
    context_window_tokens: int = 100000  # Token limit for context

    def __post_init__(self):
        """Set defaults from model type if not explicitly provided."""
        if self.productivity_rate is None:
            self.productivity_rate = self.model_type.default_productivity_rate
        if self.code_quality is None:
            self.code_quality = self.model_type.default_code_quality
        if self.supervision_requirement is None:
            self.supervision_requirement = self.model_type.default_supervision_requirement
        if self.cost_per_pr is None:
            self.cost_per_pr = self.model_type.default_cost_per_pr

    def to_developer_config(self) -> DeveloperConfig:
        """
        Convert to DeveloperConfig for use with Developer base class.

        AI agents have:
        - 100% availability (24/7)
        - Zero meeting overhead
        - Zero onboarding time
        - High productivity multiplier (already at full capability)
        """
        return DeveloperConfig(
            name=self.name or f"AI-{self.model_type.value}",
            experience_level=ExperienceLevel.SENIOR,  # Treat as senior-equivalent
            productivity_rate=self.productivity_rate,
            code_quality=self.code_quality,
            review_capacity=0.0,  # AI agents don't review by default
            onboarding_time=0,  # Instant onboarding
            current_productivity_multiplier=1.0,  # Already at full capacity
            communication_bandwidth=50.0,  # Very high - can scale easily
            availability=1.0,  # 24/7 operation
            specializations=self.specializations,
            meeting_hours_per_week=0.0,  # No meetings
        )


class AIAgent(Developer):
    """
    AI Agent for agentic software development.

    Extends Developer with AI-specific characteristics:
    - 24/7 availability
    - Zero onboarding time
    - Requires human review
    - Cost tracking
    - Different scalability properties
    """

    def __init__(
        self,
        config: Optional[AIAgentConfig] = None,
        agent_id: Optional[str] = None
    ):
        """
        Initialize an AI Agent.

        Args:
            config: AI agent configuration. Uses defaults if not provided.
            agent_id: Unique identifier for this agent
        """
        # Convert AI config to Developer config
        self.ai_config = config or AIAgentConfig()
        dev_config = self.ai_config.to_developer_config()

        # Initialize as Developer
        super().__init__(config=dev_config, agent_id=agent_id)

        # AI-specific tracking
        self.total_cost_incurred: float = 0.0
        self.total_human_review_hours: float = 0.0

        # Override base developer state
        self.is_fully_onboarded = True  # AI agents are instantly ready
        self.weeks_in_role = 0  # Track for metrics, but doesn't affect productivity

    def _update_onboarding(self, context: SimulationContext) -> None:
        """
        Override onboarding - AI agents don't need onboarding.

        They are instantly at full productivity.
        """
        # AI agents skip onboarding entirely
        self.is_fully_onboarded = True
        self.config.current_productivity_multiplier = 1.0

    def _work_on_prs(self, context: SimulationContext) -> None:
        """
        Create PRs with 24/7 availability.

        AI agents can work continuously without weekly cycling.
        """
        # AI agents work 24/7, so we use a daily rate that accounts for continuous operation
        # productivity_rate is already tuned for 24/7 work (higher than humans)
        import random

        prs_per_day = self.config.productivity_rate / 7.0  # Convert weekly to daily

        # Probabilistic PR creation
        if random.random() < prs_per_day:
            self.create_pr(context)

    def create_pr(self, context: SimulationContext) -> PullRequest:
        """
        Create a PR and track AI-specific costs.

        Overrides Developer.create_pr to add cost tracking.
        """
        # Call parent to create the PR
        pr = super().create_pr(context)

        # Mark as AI-generated for tracking
        pr.metadata = getattr(pr, 'metadata', {})
        pr.metadata['created_by_ai'] = True
        pr.metadata['ai_model'] = self.ai_config.model_type.value
        pr.metadata['requires_human_review'] = self.ai_config.requires_human_review

        # Track cost
        self.total_cost_incurred += self.ai_config.cost_per_pr

        return pr

    def can_review_pr(self, pr: PullRequest) -> bool:
        """
        Determine if this AI agent can review a given PR.

        Args:
            pr: The PR to potentially review

        Returns:
            True if the agent can review this PR
        """
        # Check if PR was created by AI
        is_ai_pr = getattr(pr, 'metadata', {}).get('created_by_ai', False)

        if is_ai_pr:
            # AI reviewing AI work
            return self.ai_config.can_review_ai_prs
        else:
            # AI reviewing human work
            return self.ai_config.can_review_human_prs

    def get_supervision_hours_for_pr(self, pr: PullRequest) -> float:
        """
        Calculate how many human hours are needed to review this AI-generated PR.

        Args:
            pr: The PR to review

        Returns:
            Hours of human review time needed
        """
        # Base review time (could be influenced by PR complexity)
        base_review_hours = 2.0  # Average hours to review a PR

        # Scale by supervision requirement
        return base_review_hours * self.ai_config.supervision_requirement

    def get_stats(self) -> dict:
        """
        Get statistics for this AI agent, including AI-specific metrics.

        Returns:
            Dictionary of stats
        """
        # Get base developer stats
        stats = super().get_stats()

        # Add AI-specific stats
        stats.update({
            "agent_type": "ai",
            "model_type": self.ai_config.model_type.value,
            "total_cost_incurred": round(self.total_cost_incurred, 2),
            "avg_cost_per_pr": round(
                self.total_cost_incurred / max(1, self.total_prs_created), 2
            ),
            "supervision_requirement": self.ai_config.supervision_requirement,
            "requires_human_review": self.ai_config.requires_human_review,
            "can_review_human_prs": self.ai_config.can_review_human_prs,
        })

        return stats

    def __repr__(self) -> str:
        name = self.config.name or self.agent_id[:8]
        model = self.ai_config.model_type.value
        return f"AIAgent(name={name}, model={model}, prs={self.total_prs_created})"
