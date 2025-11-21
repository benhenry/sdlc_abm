"""
Technical debt model.

Technical debt accumulates from low-quality PRs and slows down future development.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class TechnicalDebtItem:
    """
    Represents a unit of technical debt.

    Technical debt can come from:
    - PRs merged without sufficient review
    - PRs with quality issues (hasty implementations)
    - Skipped tests or documentation
    - Workarounds and shortcuts
    """
    debt_id: str = ""
    created_at: int = 0
    caused_by_pr: Optional[str] = None
    severity: float = 1.0  # 0.5 = minor, 1.0 = moderate, 2.0 = severe

    # Impact on productivity
    productivity_impact: float = 0.01  # Reduces team productivity by 1% per debt item

    # Repayment
    is_paid_off: bool = False
    paid_off_at: Optional[int] = None
    effort_to_fix: float = 8.0  # Hours to resolve

    def __post_init__(self):
        """Initialize debt ID if not provided."""
        if not self.debt_id:
            self.debt_id = str(uuid4())

    def pay_off(self, timestep: int) -> None:
        """Mark the debt as paid off."""
        self.is_paid_off = True
        self.paid_off_at = timestep


class TechnicalDebtTracker:
    """
    Tracks technical debt across the codebase.

    Technical debt accumulates from low-quality PRs and reduces team velocity.
    """

    def __init__(self):
        """Initialize debt tracker."""
        self.debt_items: list[TechnicalDebtItem] = []
        self.total_debt_created: int = 0
        self.total_debt_paid: int = 0

    def add_debt(
        self,
        created_at: int,
        caused_by_pr: Optional[str] = None,
        severity: float = 1.0
    ) -> TechnicalDebtItem:
        """
        Add a new technical debt item.

        Args:
            created_at: When the debt was created
            caused_by_pr: PR that caused this debt
            severity: Severity multiplier (0.5 to 2.0)

        Returns:
            The created debt item
        """
        debt = TechnicalDebtItem(
            created_at=created_at,
            caused_by_pr=caused_by_pr,
            severity=severity,
            productivity_impact=0.01 * severity,
            effort_to_fix=8.0 * severity
        )

        self.debt_items.append(debt)
        self.total_debt_created += 1

        return debt

    def pay_off_debt(self, debt: TechnicalDebtItem, timestep: int) -> None:
        """
        Pay off a debt item.

        Args:
            debt: The debt to pay off
            timestep: Current timestep
        """
        if not debt.is_paid_off:
            debt.pay_off(timestep)
            self.total_debt_paid += 1

    def get_active_debt(self) -> list[TechnicalDebtItem]:
        """
        Get all unpaid debt items.

        Returns:
            List of active debt items
        """
        return [d for d in self.debt_items if not d.is_paid_off]

    def get_total_productivity_impact(self) -> float:
        """
        Calculate total productivity impact from active debt.

        Returns:
            Cumulative productivity reduction (0.0 to 1.0)
            e.g., 0.15 = 15% reduction in productivity
        """
        active_debt = self.get_active_debt()
        total_impact = sum(d.productivity_impact for d in active_debt)

        # Cap at 50% max impact (can't go below 50% productivity)
        return min(total_impact, 0.50)

    def get_debt_count(self) -> int:
        """Get count of active debt items."""
        return len(self.get_active_debt())

    def get_stats(self) -> dict:
        """
        Get technical debt statistics.

        Returns:
            Dictionary of debt stats
        """
        active_debt = self.get_active_debt()

        return {
            "total_debt_created": self.total_debt_created,
            "total_debt_paid": self.total_debt_paid,
            "active_debt_count": len(active_debt),
            "productivity_impact": self.get_total_productivity_impact(),
            "total_effort_to_fix": sum(d.effort_to_fix for d in active_debt),
        }
