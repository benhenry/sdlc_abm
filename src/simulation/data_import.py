"""
Historical data import from CSV files.

Supports importing PR data from GitHub, GitLab, or generic CSV exports
to analyze team metrics and generate calibrated scenario configurations.
"""

import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from collections import defaultdict
import statistics

from .config import ScenarioConfig, DeveloperConfigModel, TeamConfigModel, SimulationConfigModel
from .models.types import ExperienceLevel


@dataclass
class PRImportRecord:
    """
    Imported pull request record.

    Represents a historical PR with key metrics for analysis.
    """
    pr_id: str
    title: str
    author: str
    created_at: datetime
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    reverted: bool = False
    reviewers: List[str] = field(default_factory=list)

    # Derived metrics
    cycle_time_hours: Optional[float] = None
    was_merged: bool = False

    def __post_init__(self):
        """Calculate derived metrics."""
        if self.merged_at and self.created_at:
            delta = self.merged_at - self.created_at
            self.cycle_time_hours = delta.total_seconds() / 3600.0
            self.was_merged = True


@dataclass
class DeveloperMetrics:
    """
    Aggregated metrics for a developer from historical data.
    """
    developer_id: str
    name: str

    # PR metrics
    total_prs: int = 0
    merged_prs: int = 0
    reverted_prs: int = 0

    # Review metrics
    reviews_completed: int = 0

    # Time-based metrics
    avg_cycle_time_hours: float = 0.0
    weeks_active: int = 0

    # Calculated attributes
    prs_per_week: float = 0.0
    code_quality: float = 0.85  # Default
    review_capacity_per_week: float = 0.0

    # Inferred experience level
    experience_level: ExperienceLevel = ExperienceLevel.MID

    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw counts."""
        if self.weeks_active > 0:
            self.prs_per_week = self.total_prs / self.weeks_active
            self.review_capacity_per_week = self.reviews_completed / self.weeks_active

        if self.merged_prs > 0:
            # Code quality = (merged - reverted) / merged
            self.code_quality = (self.merged_prs - self.reverted_prs) / self.merged_prs
            self.code_quality = max(0.5, min(0.98, self.code_quality))  # Clamp

        # Infer experience level from productivity and quality
        self._infer_experience_level()

    def _infer_experience_level(self):
        """Infer experience level from metrics."""
        # Simple heuristic based on productivity and quality
        score = self.prs_per_week * self.code_quality

        if score < 1.5:
            self.experience_level = ExperienceLevel.JUNIOR
        elif score < 3.0:
            self.experience_level = ExperienceLevel.MID
        elif score < 4.5:
            self.experience_level = ExperienceLevel.SENIOR
        elif score < 6.0:
            self.experience_level = ExperienceLevel.STAFF
        else:
            self.experience_level = ExperienceLevel.PRINCIPAL


class CSVDataImporter:
    """
    Imports historical team data from CSV files.

    Supports multiple CSV formats:
    - GitHub PR export
    - GitLab MR export
    - Generic CSV with required columns
    """

    def __init__(self):
        """Initialize importer."""
        self.pr_records: List[PRImportRecord] = []
        self.developer_metrics: Dict[str, DeveloperMetrics] = {}

    def import_github_prs(self, csv_path: Union[str, Path]) -> None:
        """
        Import PRs from GitHub export format.

        Expected columns:
        - number (or id)
        - title
        - author (or user)
        - created_at
        - merged_at (optional)
        - closed_at (optional)
        - state

        Args:
            csv_path: Path to CSV file
        """
        path = Path(csv_path)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                pr_id = row.get('number') or row.get('id') or row.get('pr_id')
                title = row.get('title', '')
                author = row.get('author') or row.get('user') or row.get('creator')

                # Parse dates
                created_at = self._parse_datetime(row.get('created_at'))
                merged_at = self._parse_datetime(row.get('merged_at'))
                closed_at = self._parse_datetime(row.get('closed_at'))

                # Check if reverted
                reverted = row.get('reverted', '').lower() in ('true', '1', 'yes')

                # Parse reviewers (comma-separated)
                reviewers_str = row.get('reviewers', '')
                reviewers = [r.strip() for r in reviewers_str.split(',') if r.strip()]

                if pr_id and author and created_at:
                    record = PRImportRecord(
                        pr_id=str(pr_id),
                        title=title,
                        author=author,
                        created_at=created_at,
                        merged_at=merged_at,
                        closed_at=closed_at,
                        reverted=reverted,
                        reviewers=reviewers
                    )
                    self.pr_records.append(record)

    def import_generic_csv(
        self,
        csv_path: Union[str, Path],
        column_mapping: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Import from generic CSV with custom column mapping.

        Args:
            csv_path: Path to CSV file
            column_mapping: Map standard fields to CSV columns
                Example: {'pr_id': 'pull_request_number', 'author': 'creator_name'}
        """
        default_mapping = {
            'pr_id': 'pr_id',
            'title': 'title',
            'author': 'author',
            'created_at': 'created_at',
            'merged_at': 'merged_at',
            'closed_at': 'closed_at',
            'reverted': 'reverted',
            'reviewers': 'reviewers'
        }

        mapping = column_mapping or default_mapping

        path = Path(csv_path)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                pr_id = row.get(mapping['pr_id'])
                title = row.get(mapping['title'], '')
                author = row.get(mapping['author'])

                created_at = self._parse_datetime(row.get(mapping['created_at']))
                merged_at = self._parse_datetime(row.get(mapping.get('merged_at', '')))
                closed_at = self._parse_datetime(row.get(mapping.get('closed_at', '')))

                reverted = row.get(mapping.get('reverted', ''), '').lower() in ('true', '1', 'yes')

                reviewers_str = row.get(mapping.get('reviewers', ''), '')
                reviewers = [r.strip() for r in reviewers_str.split(',') if r.strip()]

                if pr_id and author and created_at:
                    record = PRImportRecord(
                        pr_id=str(pr_id),
                        title=title,
                        author=author,
                        created_at=created_at,
                        merged_at=merged_at,
                        closed_at=closed_at,
                        reverted=reverted,
                        reviewers=reviewers
                    )
                    self.pr_records.append(record)

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse datetime from various formats.

        Supports:
        - ISO 8601: 2024-01-15T10:30:00Z
        - Simple: 2024-01-15
        - US format: 01/15/2024
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try multiple formats
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def analyze_developers(self) -> Dict[str, DeveloperMetrics]:
        """
        Analyze PR data to calculate developer metrics.

        Returns:
            Dictionary mapping developer name to metrics
        """
        # Initialize metrics for each developer
        dev_metrics: Dict[str, DeveloperMetrics] = {}

        for pr in self.pr_records:
            # Author metrics
            if pr.author not in dev_metrics:
                dev_metrics[pr.author] = DeveloperMetrics(
                    developer_id=pr.author,
                    name=pr.author
                )

            metrics = dev_metrics[pr.author]
            metrics.total_prs += 1

            if pr.was_merged:
                metrics.merged_prs += 1

            if pr.reverted:
                metrics.reverted_prs += 1

            # Reviewer metrics
            for reviewer in pr.reviewers:
                if reviewer not in dev_metrics:
                    dev_metrics[reviewer] = DeveloperMetrics(
                        developer_id=reviewer,
                        name=reviewer
                    )
                dev_metrics[reviewer].reviews_completed += 1

        # Calculate time range and weeks active
        if self.pr_records:
            dates = [pr.created_at for pr in self.pr_records]
            min_date = min(dates)
            max_date = max(dates)
            weeks = max(1, (max_date - min_date).days // 7)

            for metrics in dev_metrics.values():
                metrics.weeks_active = weeks
                metrics.calculate_derived_metrics()

        self.developer_metrics = dev_metrics
        return dev_metrics

    def calculate_team_metrics(self) -> Dict[str, Any]:
        """
        Calculate aggregate team metrics.

        Returns:
            Dictionary of team-level metrics
        """
        if not self.pr_records:
            return {}

        merged_prs = [pr for pr in self.pr_records if pr.was_merged]
        reverted_prs = [pr for pr in self.pr_records if pr.reverted]

        cycle_times = [pr.cycle_time_hours for pr in merged_prs if pr.cycle_time_hours]

        dates = [pr.created_at for pr in self.pr_records]
        min_date = min(dates)
        max_date = max(dates)
        weeks = max(1, (max_date - min_date).days // 7)

        return {
            'total_prs': len(self.pr_records),
            'merged_prs': len(merged_prs),
            'reverted_prs': len(reverted_prs),
            'change_failure_rate': len(reverted_prs) / len(merged_prs) if merged_prs else 0,
            'avg_cycle_time_hours': statistics.mean(cycle_times) if cycle_times else 0,
            'avg_cycle_time_days': statistics.mean(cycle_times) / 24.0 if cycle_times else 0,
            'prs_per_week': len(merged_prs) / weeks,
            'weeks_analyzed': weeks,
            'date_range_start': min_date.strftime('%Y-%m-%d'),
            'date_range_end': max_date.strftime('%Y-%m-%d'),
            'unique_developers': len(set(pr.author for pr in self.pr_records)),
        }

    def generate_scenario(self, name: str = "Imported Scenario") -> ScenarioConfig:
        """
        Generate a scenario configuration from imported data.

        Args:
            name: Scenario name

        Returns:
            ScenarioConfig calibrated from historical data
        """
        if not self.developer_metrics:
            self.analyze_developers()

        team_metrics = self.calculate_team_metrics()

        # Create developer configs from analyzed metrics
        developers = []
        for metrics in self.developer_metrics.values():
            # Only include developers with significant activity
            if metrics.total_prs >= 3:
                dev_config = DeveloperConfigModel(
                    name=metrics.name,
                    experience_level=metrics.experience_level.value,
                    productivity_rate=max(0.5, metrics.prs_per_week),
                    code_quality=metrics.code_quality,
                    review_capacity=max(1.0, metrics.review_capacity_per_week),
                    onboarding_time=0,  # Historical devs are already onboarded
                )
                developers.append(dev_config)

        # Create scenario
        scenario = ScenarioConfig(
            name=name,
            description=f"Generated from historical data ({team_metrics.get('date_range_start')} to {team_metrics.get('date_range_end')})",
            tags=["historical", "imported"],
            team=TeamConfigModel(developers=developers),
            simulation=SimulationConfigModel(
                duration_weeks=team_metrics.get('weeks_analyzed', 12),
                communication_loss_factor=0.3,  # Default, can be tuned
            )
        )

        return scenario

    def print_summary(self):
        """Print a summary of imported data."""
        team_metrics = self.calculate_team_metrics()

        print("\n" + "="*80)
        print("Historical Data Import Summary")
        print("="*80)
        print(f"\nData Range: {team_metrics.get('date_range_start')} to {team_metrics.get('date_range_end')}")
        print(f"Duration: {team_metrics.get('weeks_analyzed')} weeks")
        print(f"\nTeam:")
        print(f"  Unique Developers: {team_metrics.get('unique_developers')}")
        print(f"\nPull Requests:")
        print(f"  Total PRs: {team_metrics.get('total_prs')}")
        print(f"  Merged: {team_metrics.get('merged_prs')}")
        print(f"  Reverted: {team_metrics.get('reverted_prs')}")
        print(f"\nMetrics:")
        print(f"  Change Failure Rate: {team_metrics.get('change_failure_rate', 0):.1%}")
        print(f"  Avg Cycle Time: {team_metrics.get('avg_cycle_time_days', 0):.1f} days")
        print(f"  Throughput: {team_metrics.get('prs_per_week', 0):.1f} PRs/week")
        print("\n" + "="*80)

        # Developer breakdown
        if self.developer_metrics:
            print("\nTop Developers by Activity:")
            print(f"{'Name':<20} {'PRs':<8} {'Merged':<8} {'Quality':<10} {'PRs/week':<12} {'Level':<12}")
            print("-" * 80)

            sorted_devs = sorted(
                self.developer_metrics.values(),
                key=lambda d: d.total_prs,
                reverse=True
            )[:10]  # Top 10

            for dev in sorted_devs:
                print(
                    f"{dev.name:<20} "
                    f"{dev.total_prs:<8} "
                    f"{dev.merged_prs:<8} "
                    f"{dev.code_quality:.0%}{'':4} "
                    f"{dev.prs_per_week:<12.1f} "
                    f"{dev.experience_level.value:<12}"
                )

        print("\n" + "="*80 + "\n")
