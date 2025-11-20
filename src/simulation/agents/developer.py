"""
Developer agent model.

The Developer is the primary agent in the SDLC simulation, representing
individual software engineers with configurable attributes and behaviors.
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Any, TYPE_CHECKING

from ..base import Agent, SimulationContext
from ..models.types import ExperienceLevel, PRState
from ..models.work import PullRequest, CodeReview

if TYPE_CHECKING:
    from ..engine import SDLCSimulation


@dataclass
class DeveloperConfig:
    """
    Configuration for a Developer agent.

    These attributes define the developer's capabilities and constraints.
    All values from the PRD spec.
    """
    # Identity
    name: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.MID

    # Productivity
    productivity_rate: float = 3.5  # PRs per week baseline
    code_quality: float = 0.85  # PR success rate (0-1)
    review_capacity: float = 5.0  # PRs reviewed per week

    # Learning & Onboarding
    onboarding_time: int = 10  # Weeks to full productivity
    current_productivity_multiplier: float = 1.0  # Adjusted during onboarding

    # Communication
    communication_bandwidth: float = 7.0  # Effective 1:1 connections

    # Availability
    availability: float = 0.70  # % time available for work (0-1)

    # Specialization
    specializations: List[str] = field(default_factory=list)

    # Work preferences
    preferred_pr_size: str = "medium"  # small, medium, large
    meeting_hours_per_week: float = 5.0  # Default meeting load


class Developer(Agent):
    """
    Developer agent that creates PRs, reviews code, and responds to incidents.

    The developer's behavior is governed by their configuration and influenced
    by team communication patterns and organizational structure.
    """

    def __init__(
        self,
        config: Optional[DeveloperConfig] = None,
        agent_id: Optional[str] = None
    ):
        """
        Initialize a Developer agent.

        Args:
            config: Developer configuration. Uses defaults if not provided.
            agent_id: Unique identifier for this agent
        """
        super().__init__(agent_id=agent_id)
        self.config = config or DeveloperConfig()

        # Work state
        self.active_prs: List[PullRequest] = []  # PRs created by this dev
        self.pending_reviews: List[CodeReview] = []  # Reviews to complete
        self.hours_available_this_week: float = 0.0

        # Metrics tracking
        self.total_prs_created: int = 0
        self.total_prs_merged: int = 0
        self.total_prs_reverted: int = 0
        self.total_reviews_completed: int = 0

        # Learning curve
        self.weeks_in_role: int = 0
        self.is_fully_onboarded: bool = False

        # Communication
        self.active_collaborations: List[str] = []  # Other agent IDs

        # Reference to simulation (set when added)
        self._simulation: Optional[Any] = None

    def set_simulation(self, simulation: "SDLCSimulation") -> None:
        """Set reference to the simulation this agent belongs to."""
        self._simulation = simulation

    def on_added_to_simulation(self, timestep: int) -> None:
        """Called when added to simulation."""
        super().on_added_to_simulation(timestep)

        # Initialize weekly hours based on availability
        # 40 hours/week * availability * (1 - meeting time %)
        meeting_fraction = self.config.meeting_hours_per_week / 40.0
        self.hours_available_this_week = (
            40.0 * self.config.availability * (1.0 - meeting_fraction)
        )

    def step(self, context: SimulationContext) -> None:
        """
        Execute one simulation step (typically 1 day).

        The developer will:
        1. Update onboarding progress
        2. Work on creating new PRs
        3. Review pending PRs from others
        4. Respond to incidents (future)

        Args:
            context: Current simulation context
        """
        # Update weekly tracking
        if context.current_day % 7 == 0:
            self._start_new_week()

        # Update onboarding status
        self._update_onboarding(context)

        # Daily work activities
        self._work_on_prs(context)
        self._work_on_reviews(context)

    def _start_new_week(self) -> None:
        """Reset weekly tracking metrics."""
        self.weeks_in_role += 1

        # Recalculate available hours
        meeting_fraction = self.config.meeting_hours_per_week / 40.0
        self.hours_available_this_week = (
            40.0 * self.config.availability * (1.0 - meeting_fraction)
        )

    def _update_onboarding(self, context: SimulationContext) -> None:
        """
        Update productivity based on onboarding curve.

        Developers ramp up from 0% to 100% productivity over onboarding_time weeks.
        """
        if self.is_fully_onboarded:
            return

        if self.weeks_in_role >= self.config.onboarding_time:
            self.is_fully_onboarded = True
            self.config.current_productivity_multiplier = 1.0
        else:
            # Linear ramp-up (could make this non-linear later)
            progress = self.weeks_in_role / self.config.onboarding_time
            self.config.current_productivity_multiplier = progress

    def _work_on_prs(self, context: SimulationContext) -> None:
        """
        Create new PRs based on productivity rate.

        This is a simplified model - in reality, PR creation is more complex.
        """
        # Calculate daily PR creation probability
        # productivity_rate is PRs per week, so divide by 5 working days
        prs_per_day = (
            self.config.productivity_rate / 5.0
            * self.config.current_productivity_multiplier
            * self.config.experience_level.multiplier
        )

        # Probabilistic PR creation
        if random.random() < prs_per_day:
            self.create_pr(context)

    def create_pr(self, context: SimulationContext) -> PullRequest:
        """
        Create a new pull request.

        The PR's success is determined probabilistically based on code_quality.

        Args:
            context: Current simulation context

        Returns:
            The created PR
        """
        # Determine if this PR will succeed or need rework
        will_succeed = random.random() < self.config.code_quality

        pr = PullRequest(
            author_id=self.agent_id,
            created_at=context.current_day,
            will_succeed=will_succeed,
            complexity=1.0,  # Default complexity
            required_approvals=1,  # Default: 1 approval needed
        )

        # Immediately open the PR
        pr.open(context.current_day)

        self.active_prs.append(pr)
        self.total_prs_created += 1

        # Notify simulation if available
        if self._simulation and hasattr(self._simulation, 'on_pr_created'):
            self._simulation.on_pr_created(pr)

        return pr

    def _work_on_reviews(self, context: SimulationContext) -> None:
        """
        Complete pending code reviews.

        This is a simplified model - reviews are completed probabilistically.
        """
        if not self.pending_reviews:
            return

        # Calculate daily review completion probability
        reviews_per_day = self.config.review_capacity / 5.0

        # Try to complete reviews
        completed = []
        for review in self.pending_reviews:
            if random.random() < reviews_per_day:
                review.complete(context.current_day, approved=True)
                completed.append(review)
                self.total_reviews_completed += 1

        # Remove completed reviews
        for review in completed:
            self.pending_reviews.remove(review)

    def assign_review(self, pr: PullRequest, context: SimulationContext) -> CodeReview:
        """
        Assign a code review to this developer.

        Args:
            pr: The PR to review
            context: Current simulation context

        Returns:
            The created CodeReview
        """
        review = CodeReview(
            pr_id=pr.pr_id,
            reviewer_id=self.agent_id,
            started_at=context.current_day
        )

        self.pending_reviews.append(review)
        pr.reviewers.append(self.agent_id)

        return review

    def merge_pr(self, pr: PullRequest, context: SimulationContext) -> None:
        """
        Merge a PR (after approval).

        Args:
            pr: The PR to merge
            context: Current simulation context
        """
        pr.merge(context.current_day)
        self.total_prs_merged += 1

        # Remove from active PRs
        if pr in self.active_prs:
            self.active_prs.remove(pr)

    def revert_pr(self, pr: PullRequest, context: SimulationContext) -> None:
        """
        Revert a PR due to quality issues.

        Args:
            pr: The PR to revert
            context: Current simulation context
        """
        pr.revert(context.current_day)
        self.total_prs_reverted += 1

    def get_stats(self) -> dict:
        """
        Get current statistics for this developer.

        Returns:
            Dictionary of stats
        """
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "experience_level": self.config.experience_level.value,
            "weeks_in_role": self.weeks_in_role,
            "is_fully_onboarded": self.is_fully_onboarded,
            "productivity_multiplier": self.config.current_productivity_multiplier,
            "total_prs_created": self.total_prs_created,
            "total_prs_merged": self.total_prs_merged,
            "total_prs_reverted": self.total_prs_reverted,
            "total_reviews_completed": self.total_reviews_completed,
            "active_prs": len(self.active_prs),
            "pending_reviews": len(self.pending_reviews),
        }

    def __repr__(self) -> str:
        name = self.config.name or self.agent_id[:8]
        level = self.config.experience_level.value
        return f"Developer(name={name}, level={level}, prs={self.total_prs_created})"
