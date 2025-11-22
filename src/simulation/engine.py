"""
SDLC Simulation Engine

Enhanced simulation engine with SDLC-specific orchestration:
- Team management
- PR workflow (creation, review, merge, revert)
- Communication overhead modeling
- Metrics collection
"""

import random
from typing import List, Optional, Dict, Any

from .base import Simulation, SimulationContext
from .agents.developer import Developer
from .agents.ai_agent import AIAgent
from .models.types import PRState, CommunicationOverheadModel
from .models.work import PullRequest, CodeReview, Incident
from .models.technical_debt import TechnicalDebtTracker


class SDLCSimulation(Simulation):
    """
    SDLC-specific simulation engine.

    Extends the base Simulation with:
    - Team management
    - PR workflow orchestration
    - Communication overhead modeling
    - DORA metrics collection
    """

    def __init__(
        self,
        name: str = "SDLC Simulation",
        timestep_days: int = 1,
        random_seed: Optional[int] = None,
        communication_loss_factor: float = 0.3,
        communication_overhead_model: CommunicationOverheadModel = CommunicationOverheadModel.QUADRATIC
    ):
        """
        Initialize SDLC simulation.

        Args:
            name: Simulation name
            timestep_days: Days per timestep (default: 1)
            random_seed: Random seed for reproducibility
            communication_loss_factor: Information loss in team communication (0-1)
            communication_overhead_model: How overhead scales with team size
        """
        super().__init__(name=name, timestep_days=timestep_days, random_seed=random_seed)

        if random_seed is not None:
            random.seed(random_seed)

        # Communication parameters
        self.communication_loss_factor = communication_loss_factor
        self.communication_overhead_model = communication_overhead_model

        # Work tracking
        self.all_prs: List[PullRequest] = []
        self.open_prs: List[PullRequest] = []
        self.merged_prs: List[PullRequest] = []
        self.reverted_prs: List[PullRequest] = []

        self.all_reviews: List[CodeReview] = []

        # Technical debt
        self.tech_debt = TechnicalDebtTracker()

        # Incidents
        self.active_incidents: List[Incident] = []
        self.resolved_incidents: List[Incident] = []
        self.all_incidents: List[Incident] = []

        # Configuration
        self.incident_rate: float = 0.05  # 5% chance per week per developer
        self.tech_debt_accumulation_rate: float = 0.15  # 15% of low-quality PRs create debt

    @property
    def developers(self) -> List[Developer]:
        """Get all Developer agents in the simulation (includes both human and AI)."""
        return [agent for agent in self.agents if isinstance(agent, Developer)]

    @property
    def human_developers(self) -> List[Developer]:
        """Get only human Developer agents (excludes AI agents)."""
        return [agent for agent in self.agents
                if isinstance(agent, Developer) and not isinstance(agent, AIAgent)]

    @property
    def ai_agents(self) -> List[AIAgent]:
        """Get only AI Agent agents."""
        return [agent for agent in self.agents if isinstance(agent, AIAgent)]

    def add_developer(self, developer: Developer) -> None:
        """
        Add a developer to the simulation.

        Works for both human developers and AI agents.

        Args:
            developer: Developer or AIAgent to add
        """
        developer.set_simulation(self)
        self.add_agent(developer)

    def add_ai_agent(self, ai_agent: AIAgent) -> None:
        """
        Add an AI agent to the simulation.

        This is a convenience method, equivalent to add_developer().

        Args:
            ai_agent: AI agent to add
        """
        self.add_developer(ai_agent)

    def step(self) -> None:
        """
        Execute one simulation timestep with SDLC-specific orchestration.

        Order of operations:
        1. Developers create new PRs
        2. Assign reviewers to open PRs
        3. Developers work on reviews
        4. Merge approved PRs
        5. Randomly revert failed PRs (quality issues)
        6. Generate technical debt from low-quality PRs
        7. Generate random incidents
        8. Agents take their steps
        9. Update metrics
        """
        context = self.get_context()

        # 1. Let developers create PRs (happens in their step())
        # 2. Assign reviewers to new PRs
        self._assign_reviewers(context)

        # 3 & 4. Let agents do their work (reviews, etc.)
        for agent in self.agents:
            agent.step(context)

        # 5. Process PR merges
        self._process_pr_merges(context)

        # 6. Simulate quality issues (reverts)
        self._process_quality_issues(context)

        # 7. Generate technical debt
        self._generate_technical_debt(context)

        # 8. Generate incidents
        self._generate_incidents(context)

        self.current_timestep += 1

    def _assign_reviewers(self, context: SimulationContext) -> None:
        """
        Assign reviewers to PRs that need review.

        Special handling for AI-generated PRs:
        - AI PRs require human reviewers only
        - Human PRs can be reviewed by anyone (humans or AI, if AI can review)

        Uses a simple round-robin approach for now.
        Future: Could be weighted by expertise, availability, etc.
        """
        # Find PRs that need reviewers
        prs_needing_review = [
            pr for pr in self.all_prs
            if pr.state == PRState.OPEN and len(pr.reviewers) < pr.required_approvals
        ]

        for pr in prs_needing_review:
            # Find PR author
            author = self._get_developer_by_id(pr.author_id)
            if not author:
                continue

            # Check if this is an AI-generated PR
            is_ai_pr = pr.metadata.get('created_by_ai', False)

            # Find available reviewers (not the author)
            if is_ai_pr:
                # AI PRs can only be reviewed by humans
                available_reviewers = [
                    dev for dev in self.human_developers
                    if dev.agent_id != pr.author_id and dev.agent_id not in pr.reviewers
                ]
            else:
                # Human PRs can be reviewed by anyone capable
                available_reviewers = [
                    dev for dev in self.developers
                    if dev.agent_id != pr.author_id
                    and dev.agent_id not in pr.reviewers
                    and (
                        not isinstance(dev, AIAgent)
                        or dev.can_review_pr(pr)
                    )
                ]

            if not available_reviewers:
                continue

            # Assign a random reviewer
            # TODO: Make this smarter (expertise matching, load balancing, etc.)
            reviewer = random.choice(available_reviewers)
            review = reviewer.assign_review(pr, context)
            self.all_reviews.append(review)

            pr.start_review()

            self.log_event(
                event_type="review_assigned",
                agent_id=reviewer.agent_id,
                data={
                    "pr_id": pr.pr_id,
                    "author_id": pr.author_id,
                    "is_ai_pr": is_ai_pr,
                    "reviewer_is_ai": isinstance(reviewer, AIAgent)
                }
            )

    def _process_pr_merges(self, context: SimulationContext) -> None:
        """
        Merge PRs that have received sufficient approvals.
        """
        # Find completed reviews
        completed_reviews = [r for r in self.all_reviews if r.is_complete and r.approved]

        # Group by PR
        pr_approvals: Dict[str, List[CodeReview]] = {}
        for review in completed_reviews:
            if review.pr_id not in pr_approvals:
                pr_approvals[review.pr_id] = []
            pr_approvals[review.pr_id].append(review)

        # Merge PRs with enough approvals
        for pr in self.open_prs[:]:  # Copy list to avoid modification during iteration
            if pr.pr_id in pr_approvals:
                reviews = pr_approvals[pr.pr_id]

                # Add approvals
                for review in reviews:
                    pr.add_approval(review.reviewer_id)

                # Merge if approved
                if pr.state == PRState.APPROVED:
                    author = self._get_developer_by_id(pr.author_id)
                    if author:
                        author.merge_pr(pr, context)

                        self.open_prs.remove(pr)
                        self.merged_prs.append(pr)

                        self.log_event(
                            event_type="pr_merged",
                            agent_id=author.agent_id,
                            data={"pr_id": pr.pr_id, "cycle_time": pr.cycle_time}
                        )

    def _process_quality_issues(self, context: SimulationContext) -> None:
        """
        Simulate quality issues by reverting PRs that were marked to fail.

        PRs that will fail are determined at creation based on developer code_quality.
        """
        # Check recently merged PRs for quality issues
        # In reality, issues might be discovered days/weeks later
        # For now, we'll check PRs merged in the last 7 days
        recent_cutoff = max(0, context.current_day - 7)

        at_risk_prs = [
            pr for pr in self.merged_prs
            if pr.merged_at and pr.merged_at >= recent_cutoff
            and not pr.will_succeed
            and not pr.was_reverted
        ]

        for pr in at_risk_prs:
            # Random chance of discovering the issue each day
            if random.random() < 0.1:  # 10% chance per day
                author = self._get_developer_by_id(pr.author_id)
                if author:
                    author.revert_pr(pr, context)

                    self.merged_prs.remove(pr)
                    self.reverted_prs.append(pr)

                    self.log_event(
                        event_type="pr_reverted",
                        agent_id=pr.author_id,
                        data={"pr_id": pr.pr_id, "days_after_merge": context.current_day - pr.merged_at}
                    )

    def _get_developer_by_id(self, agent_id: str) -> Optional[Developer]:
        """Find a developer by their agent ID."""
        for dev in self.developers:
            if dev.agent_id == agent_id:
                return dev
        return None

    def _generate_technical_debt(self, context: SimulationContext) -> None:
        """
        Generate technical debt from recently merged low-quality PRs.

        Technical debt accumulates when PRs are merged that:
        - Have low code quality
        - Are merged without sufficient review
        - Are rushed implementations
        """
        # Check recently merged PRs (last 7 days)
        recent_cutoff = max(0, context.current_day - 7)

        recent_prs = [
            pr for pr in self.merged_prs
            if pr.merged_at and pr.merged_at >= recent_cutoff
            and not pr.was_reverted
        ]

        for pr in recent_prs:
            # PRs that won't succeed might create tech debt instead of being reverted
            if not pr.will_succeed and random.random() < self.tech_debt_accumulation_rate:
                # Determine severity based on quality
                # Lower quality = higher severity debt
                author = self._get_developer_by_id(pr.author_id)
                if author:
                    quality = author.config.code_quality
                    severity = 2.0 - quality  # 0.85 quality -> 1.15 severity

                    debt = self.tech_debt.add_debt(
                        created_at=context.current_day,
                        caused_by_pr=pr.pr_id,
                        severity=severity
                    )

                    self.log_event(
                        event_type="tech_debt_created",
                        agent_id=pr.author_id,
                        data={
                            "debt_id": debt.debt_id,
                            "pr_id": pr.pr_id,
                            "severity": severity
                        }
                    )

    def _generate_incidents(self, context: SimulationContext) -> None:
        """
        Generate random production incidents.

        Incident probability is influenced by:
        - Team size (more developers = more chances)
        - Recent PR quality (more reverts = more incidents)
        - Technical debt (more debt = more incidents)
        """
        # Base incident rate: X% chance per week per developer
        daily_incident_rate = self.incident_rate / 7.0

        # Adjust for technical debt (more debt = more incidents)
        debt_multiplier = 1.0 + self.tech_debt.get_total_productivity_impact()

        # Adjust for recent quality issues
        recent_reverts = len([
            pr for pr in self.reverted_prs
            if pr.reverted_at and pr.reverted_at >= context.current_day - 7
        ])
        quality_multiplier = 1.0 + (recent_reverts * 0.1)

        # Calculate final incident probability
        incident_probability = daily_incident_rate * debt_multiplier * quality_multiplier

        # Each developer has a chance to trigger an incident
        for dev in self.developers:
            if random.random() < incident_probability:
                # Create incident
                severity_roll = random.random()
                if severity_roll < 0.1:
                    severity = "critical"
                    estimated_hours = 16.0
                elif severity_roll < 0.3:
                    severity = "high"
                    estimated_hours = 12.0
                elif severity_roll < 0.7:
                    severity = "medium"
                    estimated_hours = 8.0
                else:
                    severity = "low"
                    estimated_hours = 4.0

                incident = Incident(
                    created_at=context.current_day,
                    severity=severity,
                    estimated_hours=estimated_hours
                )

                # Assign to a random developer (or multiple for critical)
                if severity == "critical":
                    # Assign to 2-3 developers for critical incidents
                    num_assignees = min(len(self.developers), random.randint(2, 3))
                    assignees = random.sample(self.developers, num_assignees)
                else:
                    assignees = [random.choice(self.developers)]

                for assignee in assignees:
                    incident.assign(assignee.agent_id)

                self.active_incidents.append(incident)
                self.all_incidents.append(incident)

                self.log_event(
                    event_type="incident_created",
                    data={
                        "incident_id": incident.incident_id,
                        "severity": severity,
                        "assigned_to": incident.assigned_to
                    }
                )

    def calculate_communication_overhead(self, team_size: int) -> float:
        """
        Calculate communication overhead factor based on team size.

        Args:
            team_size: Number of developers

        Returns:
            Overhead multiplier (1.0 = no overhead)
        """
        if team_size <= 1:
            return 1.0

        if self.communication_overhead_model == CommunicationOverheadModel.LINEAR:
            # O(n) - linear growth
            return 1.0 + (team_size - 1) * 0.05

        elif self.communication_overhead_model == CommunicationOverheadModel.QUADRATIC:
            # O(n²) - quadratic growth (realistic default)
            # Brooks' Law: adding people to a late project makes it later
            connections = team_size * (team_size - 1) / 2
            return 1.0 + (connections / 100.0)

        elif self.communication_overhead_model == CommunicationOverheadModel.HIERARCHICAL:
            # O(log n) - well-structured orgs
            import math
            return 1.0 + math.log2(team_size) * 0.1

        return 1.0

    def get_metrics(self) -> Dict[str, Any]:
        """
        Calculate current simulation metrics.

        Includes both aggregate and AI-specific metrics.

        Returns:
            Dictionary of metrics
        """
        total_devs = len(self.developers)
        human_count = len(self.human_developers)
        ai_count = len(self.ai_agents)

        total_prs = len(self.all_prs)
        merged_count = len(self.merged_prs)
        reverted_count = len(self.reverted_prs)

        # Separate AI vs human PRs
        ai_prs = [pr for pr in self.all_prs if pr.metadata.get('created_by_ai', False)]
        human_prs = [pr for pr in self.all_prs if not pr.metadata.get('created_by_ai', False)]

        ai_merged = [pr for pr in self.merged_prs if pr.metadata.get('created_by_ai', False)]
        human_merged = [pr for pr in self.merged_prs if not pr.metadata.get('created_by_ai', False)]

        ai_reverted = [pr for pr in self.reverted_prs if pr.metadata.get('created_by_ai', False)]
        human_reverted = [pr for pr in self.reverted_prs if not pr.metadata.get('created_by_ai', False)]

        # Calculate average cycle time
        cycle_times = [pr.cycle_time for pr in self.merged_prs if pr.cycle_time is not None]
        avg_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0

        ai_cycle_times = [pr.cycle_time for pr in ai_merged if pr.cycle_time is not None]
        avg_ai_cycle_time = sum(ai_cycle_times) / len(ai_cycle_times) if ai_cycle_times else 0

        human_cycle_times = [pr.cycle_time for pr in human_merged if pr.cycle_time is not None]
        avg_human_cycle_time = sum(human_cycle_times) / len(human_cycle_times) if human_cycle_times else 0

        # Calculate change failure rate
        change_failure_rate = reverted_count / merged_count if merged_count > 0 else 0
        ai_failure_rate = len(ai_reverted) / len(ai_merged) if ai_merged else 0
        human_failure_rate = len(human_reverted) / len(human_merged) if human_merged else 0

        # Calculate throughput (PRs per week)
        weeks = max(1, self.current_timestep // 7)
        prs_per_week = merged_count / weeks
        ai_prs_per_week = len(ai_merged) / weeks
        human_prs_per_week = len(human_merged) / weeks

        # Calculate communication overhead
        comm_overhead = self.calculate_communication_overhead(total_devs)

        # Technical debt stats
        debt_stats = self.tech_debt.get_stats()

        # Incident stats
        total_incidents = len(self.all_incidents)
        active_incident_count = len(self.active_incidents)
        resolved_incidents = [i for i in self.all_incidents if i.is_resolved]
        mttr_values = [i.time_to_resolve for i in resolved_incidents if i.time_to_resolve is not None]
        avg_mttr = sum(mttr_values) / len(mttr_values) if mttr_values else 0

        # AI-specific metrics
        total_ai_cost = sum(agent.total_cost_incurred for agent in self.ai_agents)
        avg_ai_cost_per_pr = total_ai_cost / len(ai_prs) if ai_prs else 0

        return {
            "current_day": self.current_timestep,
            "current_week": self.current_timestep // 7,
            # Team composition
            "total_developers": total_devs,
            "human_developers": human_count,
            "ai_agents": ai_count,
            # Overall metrics
            "total_prs_created": total_prs,
            "total_prs_merged": merged_count,
            "total_prs_reverted": reverted_count,
            "open_prs": len(self.open_prs),
            "avg_cycle_time_days": round(avg_cycle_time, 2),
            "change_failure_rate": round(change_failure_rate, 3),
            "prs_per_week": round(prs_per_week, 2),
            "communication_overhead": round(comm_overhead, 2),
            # Human-specific metrics
            "human_prs_created": len(human_prs),
            "human_prs_merged": len(human_merged),
            "human_prs_reverted": len(human_reverted),
            "human_failure_rate": round(human_failure_rate, 3),
            "human_prs_per_week": round(human_prs_per_week, 2),
            "human_avg_cycle_time_days": round(avg_human_cycle_time, 2),
            # AI-specific metrics
            "ai_prs_created": len(ai_prs),
            "ai_prs_merged": len(ai_merged),
            "ai_prs_reverted": len(ai_reverted),
            "ai_failure_rate": round(ai_failure_rate, 3),
            "ai_prs_per_week": round(ai_prs_per_week, 2),
            "ai_avg_cycle_time_days": round(avg_ai_cycle_time, 2),
            "ai_total_cost": round(total_ai_cost, 2),
            "ai_avg_cost_per_pr": round(avg_ai_cost_per_pr, 2),
            # Technical debt metrics
            "tech_debt_count": debt_stats["active_debt_count"],
            "tech_debt_productivity_impact": round(debt_stats["productivity_impact"], 3),
            "tech_debt_total_created": debt_stats["total_debt_created"],
            "tech_debt_total_paid": debt_stats["total_debt_paid"],
            # Incident metrics
            "total_incidents": total_incidents,
            "active_incidents": active_incident_count,
            "resolved_incidents": len(resolved_incidents),
            "avg_mttr_days": round(avg_mttr, 2),
        }

    def print_summary(self) -> None:
        """Print a summary of the simulation state."""
        metrics = self.get_metrics()

        print(f"\n{'='*70}")
        print(f"Simulation: {self.name}")
        print(f"{'='*70}")
        print(f"Day {metrics['current_day']} (Week {metrics['current_week']})")
        print(f"\nTeam Composition:")
        print(f"  Total Developers: {metrics['total_developers']}")
        print(f"  - Humans: {metrics['human_developers']}")
        print(f"  - AI Agents: {metrics['ai_agents']}")
        print(f"  Communication Overhead: {metrics['communication_overhead']}x")

        print(f"\nOverall Delivery:")
        print(f"  PRs Created: {metrics['total_prs_created']}")
        print(f"  PRs Merged: {metrics['total_prs_merged']}")
        print(f"  PRs Reverted: {metrics['total_prs_reverted']}")
        print(f"  Open PRs: {metrics['open_prs']}")
        print(f"  Avg Cycle Time: {metrics['avg_cycle_time_days']} days")
        print(f"  Change Failure Rate: {metrics['change_failure_rate']:.1%}")
        print(f"  Throughput: {metrics['prs_per_week']} PRs/week")

        if metrics['ai_agents'] > 0:
            print(f"\nHuman Developers:")
            print(f"  PRs Created: {metrics['human_prs_created']}")
            print(f"  PRs Merged: {metrics['human_prs_merged']}")
            print(f"  Failure Rate: {metrics['human_failure_rate']:.1%}")
            print(f"  Throughput: {metrics['human_prs_per_week']:.1f} PRs/week")
            print(f"  Avg Cycle Time: {metrics['human_avg_cycle_time_days']:.1f} days")

            print(f"\nAI Agents:")
            print(f"  PRs Created: {metrics['ai_prs_created']}")
            print(f"  PRs Merged: {metrics['ai_prs_merged']}")
            print(f"  Failure Rate: {metrics['ai_failure_rate']:.1%}")
            print(f"  Throughput: {metrics['ai_prs_per_week']:.1f} PRs/week")
            print(f"  Avg Cycle Time: {metrics['ai_avg_cycle_time_days']:.1f} days")
            print(f"  Total Cost: ${metrics['ai_total_cost']:.2f}")
            print(f"  Avg Cost/PR: ${metrics['ai_avg_cost_per_pr']:.2f}")

        print(f"\nTechnical Debt:")
        print(f"  Active Debt Items: {metrics['tech_debt_count']}")
        print(f"  Productivity Impact: {metrics['tech_debt_productivity_impact']:.1%}")
        print(f"  Total Created: {metrics['tech_debt_total_created']}")

        print(f"\nIncidents:")
        print(f"  Total Incidents: {metrics['total_incidents']}")
        print(f"  Active: {metrics['active_incidents']}")
        print(f"  Resolved: {metrics['resolved_incidents']}")
        if metrics['avg_mttr_days'] > 0:
            print(f"  Avg MTTR: {metrics['avg_mttr_days']} days")
        print(f"{'='*70}\n")

    # Event tracking convenience methods

    def on_pr_created(self, pr: PullRequest) -> None:
        """Called when a PR is created."""
        self.all_prs.append(pr)
        self.open_prs.append(pr)

        self.log_event(
            event_type="pr_created",
            agent_id=pr.author_id,
            data={"pr_id": pr.pr_id}
        )
