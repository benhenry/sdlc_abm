"""
Work-related models: Pull Requests, Reviews, Incidents, etc.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from uuid import uuid4

from .types import PRState


@dataclass
class PullRequest:
    """
    Represents a pull request in the simulation.

    PRs are the primary unit of work output in the SDLC simulation.
    """
    pr_id: str = field(default_factory=lambda: str(uuid4()))
    author_id: str = ""
    created_at: int = 0
    complexity: float = 1.0  # Relative complexity (1.0 = average)

    # State
    state: PRState = PRState.DRAFT

    # Review process
    reviewers: List[str] = field(default_factory=list)
    approvals: List[str] = field(default_factory=list)
    required_approvals: int = 1

    # Lifecycle timestamps
    opened_at: Optional[int] = None
    merged_at: Optional[int] = None
    reverted_at: Optional[int] = None
    closed_at: Optional[int] = None

    # Quality
    will_succeed: bool = True  # Determined at creation based on agent quality
    was_reverted: bool = False

    # Communication loss impact
    requirements_clarity: float = 1.0  # 0-1, affected by communication loss

    def open(self, timestep: int) -> None:
        """Mark PR as open for review."""
        self.state = PRState.OPEN
        self.opened_at = timestep

    def start_review(self) -> None:
        """Mark PR as in review."""
        self.state = PRState.IN_REVIEW

    def add_approval(self, reviewer_id: str) -> None:
        """Add an approval from a reviewer."""
        if reviewer_id not in self.approvals:
            self.approvals.append(reviewer_id)

        if len(self.approvals) >= self.required_approvals:
            self.state = PRState.APPROVED

    def merge(self, timestep: int) -> None:
        """Merge the PR."""
        self.state = PRState.MERGED
        self.merged_at = timestep

    def revert(self, timestep: int) -> None:
        """Revert the PR (quality issue found)."""
        self.state = PRState.REVERTED
        self.reverted_at = timestep
        self.was_reverted = True

    def close(self, timestep: int) -> None:
        """Close the PR without merging."""
        self.state = PRState.CLOSED
        self.closed_at = timestep

    @property
    def is_merged(self) -> bool:
        """Check if PR is merged."""
        return self.state == PRState.MERGED

    @property
    def cycle_time(self) -> Optional[int]:
        """
        Calculate cycle time (days from open to merge).

        Returns:
            Cycle time in days, or None if not merged
        """
        if self.opened_at is not None and self.merged_at is not None:
            return self.merged_at - self.opened_at
        return None

    def __repr__(self) -> str:
        return f"PR(id={self.pr_id[:8]}..., author={self.author_id[:8]}..., state={self.state.value})"


@dataclass
class CodeReview:
    """
    Represents a code review action.

    Reviews are performed by developers on PRs created by others.
    """
    review_id: str = field(default_factory=lambda: str(uuid4()))
    pr_id: str = ""
    reviewer_id: str = ""
    started_at: int = 0
    completed_at: Optional[int] = None
    approved: bool = False
    time_invested: float = 0.0  # Hours spent reviewing

    def complete(self, timestep: int, approved: bool = True) -> None:
        """Mark the review as complete."""
        self.completed_at = timestep
        self.approved = approved

    @property
    def is_complete(self) -> bool:
        """Check if review is complete."""
        return self.completed_at is not None

    def __repr__(self) -> str:
        return f"Review(pr={self.pr_id[:8]}..., reviewer={self.reviewer_id[:8]}..., approved={self.approved})"


@dataclass
class Incident:
    """
    Represents a production incident requiring developer attention.

    Incidents are random events that occur based on code quality and
    consume developer capacity.
    """
    incident_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: int = 0
    resolved_at: Optional[int] = None
    severity: str = "medium"  # low, medium, high, critical

    # Assignees
    assigned_to: List[str] = field(default_factory=list)

    # Time investment
    estimated_hours: float = 8.0  # Default: 1 day
    hours_invested: float = 0.0

    # Root cause (if known)
    caused_by_pr: Optional[str] = None

    def assign(self, developer_id: str) -> None:
        """Assign the incident to a developer."""
        if developer_id not in self.assigned_to:
            self.assigned_to.append(developer_id)

    def add_work(self, hours: float) -> None:
        """Add work hours to the incident."""
        self.hours_invested += hours

    def resolve(self, timestep: int) -> None:
        """Mark the incident as resolved."""
        self.resolved_at = timestep

    @property
    def is_resolved(self) -> bool:
        """Check if incident is resolved."""
        return self.resolved_at is not None

    @property
    def time_to_resolve(self) -> Optional[int]:
        """
        Calculate MTTR (Mean Time To Resolve) for this incident.

        Returns:
            Days to resolution, or None if not resolved
        """
        if self.resolved_at is not None:
            return self.resolved_at - self.created_at
        return None

    def __repr__(self) -> str:
        status = "resolved" if self.is_resolved else "open"
        return f"Incident(id={self.incident_id[:8]}..., severity={self.severity}, status={status})"
