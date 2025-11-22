"""
Integration tests for mixed human/AI team simulations.

Tests the interaction between human developers and AI agents working together.
"""

import pytest
from src.simulation.engine import SDLCSimulation
from src.simulation.agents.developer import Developer, DeveloperConfig
from src.simulation.agents.ai_agent import AIAgent, AIAgentConfig
from src.simulation.models.types import ExperienceLevel, AIModelType, PRState
from src.simulation.runner import ScenarioRunner


class TestMixedTeamSimulation:
    """Test simulations with both humans and AI agents."""

    def test_add_both_agent_types(self):
        """Test that we can add both human and AI agents to a simulation."""
        sim = SDLCSimulation(name="Mixed Test", random_seed=42)

        # Add human developers
        human = Developer(config=DeveloperConfig(name="Human"))
        sim.add_developer(human)

        # Add AI agents
        ai = AIAgent(config=AIAgentConfig(name="AI"))
        sim.add_ai_agent(ai)

        assert len(sim.developers) == 2
        assert len(sim.human_developers) == 1
        assert len(sim.ai_agents) == 1

    def test_human_only_review_of_ai_prs(self):
        """Test that AI PRs are only assigned to human reviewers."""
        sim = SDLCSimulation(name="Review Test", random_seed=42)

        # Add 2 humans and 1 AI
        human1 = Developer(config=DeveloperConfig(name="Human1"))
        human2 = Developer(config=DeveloperConfig(name="Human2"))
        ai = AIAgent(config=AIAgentConfig(name="AI1"))

        sim.add_developer(human1)
        sim.add_developer(human2)
        sim.add_ai_agent(ai)

        # Run a few steps to generate PRs
        for _ in range(10):
            sim.step()

        # Check that AI PRs only have human reviewers
        ai_prs = [pr for pr in sim.all_prs if pr.metadata.get('created_by_ai', False)]

        for pr in ai_prs:
            if pr.reviewers:
                for reviewer_id in pr.reviewers:
                    # Reviewer should be one of the humans
                    assert reviewer_id in [human1.agent_id, human2.agent_id]
                    assert reviewer_id != ai.agent_id

    def test_mixed_team_produces_both_pr_types(self):
        """Test that mixed teams generate both human and AI PRs."""
        sim = SDLCSimulation(name="PR Types Test", random_seed=42)

        # Add balanced team
        for i in range(2):
            sim.add_developer(Developer(config=DeveloperConfig(name=f"Human{i}")))
            sim.add_ai_agent(AIAgent(config=AIAgentConfig(name=f"AI{i}")))

        # Run simulation
        sim.run(14)  # 2 weeks

        # Should have both types of PRs
        ai_prs = [pr for pr in sim.all_prs if pr.metadata.get('created_by_ai', False)]
        human_prs = [pr for pr in sim.all_prs if not pr.metadata.get('created_by_ai', False)]

        assert len(ai_prs) > 0, "Should have AI-generated PRs"
        assert len(human_prs) > 0, "Should have human-generated PRs"

    def test_ai_cost_tracking(self):
        """Test that AI costs are tracked correctly."""
        sim = SDLCSimulation(name="Cost Test", random_seed=42)

        # Add AI agents with known cost
        ai1 = AIAgent(config=AIAgentConfig(name="AI1", cost_per_pr=0.50))
        ai2 = AIAgent(config=AIAgentConfig(name="AI2", cost_per_pr=1.00))
        human = Developer(config=DeveloperConfig(name="Human"))

        sim.add_ai_agent(ai1)
        sim.add_ai_agent(ai2)
        sim.add_developer(human)

        # Run simulation
        sim.run(7)  # 1 week

        # Check that costs accumulated
        assert ai1.total_cost_incurred > 0
        assert ai2.total_cost_incurred > 0

        # Check metrics
        metrics = sim.get_metrics()
        assert metrics['ai_total_cost'] > 0
        assert metrics['ai_total_cost'] == ai1.total_cost_incurred + ai2.total_cost_incurred

        if metrics['ai_prs_created'] > 0:
            assert metrics['ai_avg_cost_per_pr'] > 0

    def test_metrics_separation(self):
        """Test that metrics correctly separate human and AI contributions."""
        sim = SDLCSimulation(name="Metrics Test", random_seed=42)

        # Add team
        sim.add_developer(Developer(config=DeveloperConfig(name="Human")))
        sim.add_ai_agent(AIAgent(config=AIAgentConfig(name="AI")))

        # Run simulation
        sim.run(14)  # 2 weeks

        metrics = sim.get_metrics()

        # Check composition metrics
        assert metrics['human_developers'] == 1
        assert metrics['ai_agents'] == 1
        assert metrics['total_developers'] == 2

        # Check that metrics add up
        assert metrics['total_prs_created'] == metrics['human_prs_created'] + metrics['ai_prs_created']
        assert metrics['total_prs_merged'] == metrics['human_prs_merged'] + metrics['ai_prs_merged']
        assert metrics['total_prs_reverted'] == metrics['human_prs_reverted'] + metrics['ai_prs_reverted']

        # AI-specific metrics should exist
        assert 'ai_failure_rate' in metrics
        assert 'ai_prs_per_week' in metrics
        assert 'ai_total_cost' in metrics

    def test_ai_agents_have_no_onboarding(self):
        """Test that AI agents are productive immediately."""
        sim = SDLCSimulation(name="Onboarding Test", random_seed=42)

        # Add AI agent (instant) vs human (10-week onboarding)
        ai = AIAgent(config=AIAgentConfig(name="AI"))
        human = Developer(config=DeveloperConfig(
            name="Human",
            onboarding_time=10
        ))

        sim.add_ai_agent(ai)
        sim.add_developer(human)

        # Check initial state
        assert ai.is_fully_onboarded is True
        assert ai.config.current_productivity_multiplier == 1.0

        assert human.is_fully_onboarded is False
        # Human starts at default but will ramp up during simulation

        # Run 1 week
        sim.run(7)

        # AI should still be at full productivity
        assert ai.config.current_productivity_multiplier == 1.0

        # Human should be ramping up (1 week into 10-week onboarding)
        # After 1 week: 1/10 = 0.1 productivity
        assert human.weeks_in_role == 1
        assert 0 < human.config.current_productivity_multiplier <= 0.2

    def test_ai_24_7_availability(self):
        """Test that AI agents have continuous availability."""
        sim = SDLCSimulation(name="Availability Test", random_seed=42)

        ai = AIAgent(config=AIAgentConfig(name="AI"))
        human = Developer(config=DeveloperConfig(name="Human"))

        sim.add_ai_agent(ai)
        sim.add_developer(human)

        # Check availability
        assert ai.config.availability == 1.0  # 24/7
        assert ai.config.meeting_hours_per_week == 0.0

        assert human.config.availability < 1.0  # Not 24/7
        assert human.config.meeting_hours_per_week > 0.0


class TestMixedTeamFromConfig:
    """Test loading mixed teams from configuration files."""

    def test_load_mixed_team_yaml(self):
        """Test loading a mixed team from YAML configuration."""
        runner = ScenarioRunner.from_yaml('data/scenarios/mixed_team_example.yaml')

        assert runner.scenario.name == "Mixed Team: 5 Humans + 4 AI Agents"

        # Check team composition
        humans = runner.scenario.team.get_developers()
        ai_agents = runner.scenario.team.get_ai_agents()

        assert len(humans) == 5
        assert len(ai_agents) == 4

        # Check AI agent types
        ai_models = [ai.model_type for ai in ai_agents]
        assert AIModelType.CLAUDE_SONNET in ai_models
        assert AIModelType.CODELLAMA in ai_models

    def test_quick_generation_yaml(self):
        """Test quick team generation from YAML."""
        runner = ScenarioRunner.from_yaml('data/scenarios/quick_mixed_team.yaml')

        humans = runner.scenario.team.get_developers()
        ai_agents = runner.scenario.team.get_ai_agents()

        # Quick config specified: 7 humans (2 senior, 4 mid, 1 junior) + 6 AI
        assert len(humans) == 7
        assert len(ai_agents) == 6

        # All AI agents should be claude-sonnet (default)
        assert all(ai.model_type == AIModelType.CLAUDE_SONNET for ai in ai_agents)

    def test_run_mixed_team_scenario(self):
        """Test running a complete mixed team scenario."""
        runner = ScenarioRunner.from_yaml('data/scenarios/quick_mixed_team.yaml')

        # Run simulation (short duration for test)
        metrics = runner.run(verbose=False)

        # Should have metrics for both humans and AI
        assert metrics['human_developers'] > 0
        assert metrics['ai_agents'] > 0
        assert metrics['total_prs_created'] > 0

        # Should have separated metrics
        assert metrics['human_prs_created'] >= 0
        assert metrics['ai_prs_created'] >= 0
        assert metrics['ai_total_cost'] >= 0


class TestDiminishingReturns:
    """Test scenarios to identify diminishing returns with AI agents."""

    def test_increasing_ai_agents(self):
        """Test that adding AI agents shows pattern of returns."""
        results = []

        for ai_count in [0, 2, 4, 6, 8]:
            sim = SDLCSimulation(name=f"AI Count: {ai_count}", random_seed=42)

            # Fixed human team
            for i in range(5):
                sim.add_developer(Developer(config=DeveloperConfig(name=f"Human{i}")))

            # Variable AI team
            for i in range(ai_count):
                sim.add_ai_agent(AIAgent(config=AIAgentConfig(name=f"AI{i}")))

            # Run short simulation
            sim.run(7)  # 1 week

            metrics = sim.get_metrics()
            results.append({
                'ai_count': ai_count,
                'throughput': metrics['prs_per_week'],
                'cost': metrics['ai_total_cost'],
            })

        # Throughput should increase with AI agents
        throughputs = [r['throughput'] for r in results]
        assert throughputs[-1] > throughputs[0], "More AI agents should increase throughput"

        # Costs should increase linearly with AI count
        costs = [r['cost'] for r in results[1:]]  # Skip 0 AI
        assert all(costs[i] > costs[i-1] for i in range(1, len(costs))), "Costs should increase with AI count"

    def test_human_review_bottleneck(self):
        """Test that human review can become a bottleneck with many AI agents."""
        sim = SDLCSimulation(name="Bottleneck Test", random_seed=42)

        # Small human team
        for i in range(2):
            sim.add_developer(Developer(config=DeveloperConfig(name=f"Human{i}")))

        # Large AI team
        for i in range(10):
            sim.add_ai_agent(AIAgent(config=AIAgentConfig(name=f"AI{i}")))

        # Run simulation
        sim.run(14)  # 2 weeks

        # Should have many open PRs (bottleneck indicator)
        metrics = sim.get_metrics()

        # With 10 AI agents producing ~10 PRs/week each and only 2 humans to review,
        # we should see a backlog
        if metrics['ai_prs_created'] > metrics['ai_prs_merged']:
            assert metrics['open_prs'] > 0, "Should have backlog with insufficient reviewers"
