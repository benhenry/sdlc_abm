"""
Mixed Human and AI Team Simulation Example

This script demonstrates how to create and run a simulation with both
human developers and AI agents working together. It compares different
team compositions to understand the trade-offs.
"""

import sys
from pathlib import Path

# Add src to path so we can import simulation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.engine import SDLCSimulation
from src.simulation.agents.developer import Developer, DeveloperConfig
from src.simulation.agents.ai_agent import AIAgent, AIAgentConfig
from src.simulation.models.types import ExperienceLevel, AIModelType


def create_human_team(size: int = 5) -> list[Developer]:
    """
    Create a team of human developers with realistic distribution.

    Args:
        size: Team size (default: 5)

    Returns:
        List of Developer agents
    """
    team = []

    # Realistic distribution: 1 senior, 3 mid, 1 junior
    if size >= 1:
        team.append(Developer(
            config=DeveloperConfig(
                name="Senior Dev",
                experience_level=ExperienceLevel.SENIOR,
                productivity_rate=4.0,
                code_quality=0.88,
                review_capacity=6.0,
                onboarding_time=6,
                availability=0.70,
                meeting_hours_per_week=6.0,
            )
        ))

    mid_count = max(0, min(size - 2, 3)) if size > 2 else max(0, size - 1)
    for i in range(mid_count):
        team.append(Developer(
            config=DeveloperConfig(
                name=f"Mid Dev {i+1}",
                experience_level=ExperienceLevel.MID,
                productivity_rate=3.5,
                code_quality=0.85,
                review_capacity=5.0,
                onboarding_time=10,
                availability=0.75,
                meeting_hours_per_week=5.0,
            )
        ))

    # Add junior if team is large enough
    if size > 4:
        team.append(Developer(
            config=DeveloperConfig(
                name="Junior Dev",
                experience_level=ExperienceLevel.JUNIOR,
                productivity_rate=2.0,
                code_quality=0.75,
                review_capacity=3.0,
                onboarding_time=16,
                availability=0.70,
                meeting_hours_per_week=5.0,
            )
        ))

    # Fill remaining slots with mid-level
    while len(team) < size:
        team.append(Developer(
            config=DeveloperConfig(
                name=f"Mid Dev {len(team)}",
                experience_level=ExperienceLevel.MID,
                productivity_rate=3.5,
                code_quality=0.85,
                review_capacity=5.0,
                onboarding_time=10,
                availability=0.75,
                meeting_hours_per_week=5.0,
            )
        ))

    return team


def create_ai_agents(count: int = 2, model_type: AIModelType = AIModelType.CLAUDE_SONNET) -> list[AIAgent]:
    """
    Create AI agents with specified model type.

    Args:
        count: Number of AI agents
        model_type: AI model type to use

    Returns:
        List of AIAgent instances
    """
    agents = []
    for i in range(count):
        agents.append(AIAgent(
            config=AIAgentConfig(
                name=f"AI-{model_type.value}-{i+1}",
                model_type=model_type,
                # Use defaults from model type
            )
        ))
    return agents


def run_scenario(
    name: str,
    human_count: int,
    ai_count: int,
    ai_model: AIModelType = AIModelType.CLAUDE_SONNET,
    weeks: int = 12,
    random_seed: int = 42
) -> dict:
    """
    Run a simulation scenario with specified team composition.

    Args:
        name: Scenario name
        human_count: Number of human developers
        ai_count: Number of AI agents
        ai_model: AI model type
        weeks: Simulation duration in weeks
        random_seed: Random seed for reproducibility

    Returns:
        Dictionary of final metrics
    """
    print(f"\n{'='*80}")
    print(f"Scenario: {name}")
    print(f"{'='*80}")
    print(f"Team: {human_count} humans + {ai_count} AI agents ({ai_model.value})")
    print(f"Duration: {weeks} weeks\n")

    # Create simulation
    sim = SDLCSimulation(
        name=name,
        timestep_days=1,
        random_seed=random_seed,
        communication_loss_factor=0.3,
    )

    # Add human developers
    humans = create_human_team(human_count)
    for dev in humans:
        sim.add_developer(dev)

    # Add AI agents
    ai_agents = create_ai_agents(ai_count, ai_model)
    for agent in ai_agents:
        sim.add_ai_agent(agent)

    print(f"Human developers added: {len(humans)}")
    print(f"AI agents added: {len(ai_agents)}")
    print(f"Total team size: {len(sim.developers)}")

    # Run simulation
    print(f"\nRunning simulation for {weeks} weeks...")
    sim.run(weeks * 7)

    # Print results
    sim.print_summary()

    # Return metrics for comparison
    return sim.get_metrics()


def compare_scenarios():
    """
    Compare multiple team compositions to understand trade-offs.
    """
    print("\n" + "="*80)
    print("MIXED TEAM SIMULATION - Comparing Team Compositions")
    print("="*80)
    print("\nComparing different combinations of humans and AI agents")
    print("Goal: Understand productivity, quality, and cost trade-offs\n")

    scenarios = []

    # Baseline: All humans
    print("\n" + "─"*80)
    print("BASELINE: All Human Team")
    print("─"*80)
    metrics_baseline = run_scenario(
        name="Baseline: 7 Humans",
        human_count=7,
        ai_count=0,
        weeks=12,
        random_seed=42
    )
    scenarios.append(("7 Humans, 0 AI", metrics_baseline))

    # Scenario 1: Add some AI agents
    print("\n" + "─"*80)
    print("SCENARIO 1: Humans + AI Assistance")
    print("─"*80)
    metrics_s1 = run_scenario(
        name="Scenario 1: 5 Humans + 4 AI",
        human_count=5,
        ai_count=4,
        ai_model=AIModelType.CLAUDE_SONNET,
        weeks=12,
        random_seed=42
    )
    scenarios.append(("5 Humans, 4 AI (Sonnet)", metrics_s1))

    # Scenario 2: Fewer humans, more AI
    print("\n" + "─"*80)
    print("SCENARIO 2: AI-Heavy Team")
    print("─"*80)
    metrics_s2 = run_scenario(
        name="Scenario 2: 3 Humans + 8 AI",
        human_count=3,
        ai_count=8,
        ai_model=AIModelType.CLAUDE_SONNET,
        weeks=12,
        random_seed=42
    )
    scenarios.append(("3 Humans, 8 AI (Sonnet)", metrics_s2))

    # Scenario 3: High-quality AI model
    print("\n" + "─"*80)
    print("SCENARIO 3: Premium AI Model")
    print("─"*80)
    metrics_s3 = run_scenario(
        name="Scenario 3: 4 Humans + 4 AI (Opus)",
        human_count=4,
        ai_count=4,
        ai_model=AIModelType.CLAUDE_OPUS,
        weeks=12,
        random_seed=42
    )
    scenarios.append(("4 Humans, 4 AI (Opus)", metrics_s3))

    # Print comparison table
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    print(f"\n{'Scenario':<30} {'PRs/Week':<12} {'Failure':<10} {'AI Cost':<12} {'Total PRs':<10}")
    print("─"*80)

    for scenario_name, metrics in scenarios:
        print(
            f"{scenario_name:<30} "
            f"{metrics['prs_per_week']:<12.1f} "
            f"{metrics['change_failure_rate']*100:<10.1f}% "
            f"${metrics.get('ai_total_cost', 0):<11.2f} "
            f"{metrics['total_prs_merged']:<10}"
        )

    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)

    # Calculate some insights
    baseline_throughput = scenarios[0][1]['prs_per_week']
    baseline_failure = scenarios[0][1]['change_failure_rate']

    print(f"\nBaseline (All Humans): {baseline_throughput:.1f} PRs/week, {baseline_failure:.1%} failure rate")

    for i, (scenario_name, metrics) in enumerate(scenarios[1:], 1):
        throughput_change = ((metrics['prs_per_week'] / baseline_throughput) - 1) * 100
        failure_change = ((metrics['change_failure_rate'] / baseline_failure) - 1) * 100 if baseline_failure > 0 else 0
        cost = metrics.get('ai_total_cost', 0)
        cost_per_pr = metrics.get('ai_avg_cost_per_pr', 0)

        print(f"\nScenario {i} ({scenario_name}):")
        print(f"  Throughput: {throughput_change:+.1f}% vs baseline")
        print(f"  Failure Rate: {failure_change:+.1f}% vs baseline")
        if cost > 0:
            print(f"  AI Cost: ${cost:.2f} total (${cost_per_pr:.2f}/PR)")
            print(f"  Cost/Week: ${cost/12:.2f}")

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("""
1. AI agents can significantly boost throughput when combined with humans
2. Human review is critical - quality may degrade without sufficient oversight
3. Cost-benefit depends on PR value vs AI API costs
4. Optimal mix likely requires experimentation with your specific workload
5. Consider using faster AI models (Sonnet) for routine work, premium (Opus) for critical paths
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    compare_scenarios()
