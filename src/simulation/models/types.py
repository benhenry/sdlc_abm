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
