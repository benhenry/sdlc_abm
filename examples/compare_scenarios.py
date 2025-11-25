"""
Scenario Comparison Example

Demonstrates how to compare multiple scenarios to understand trade-offs
and identify optimal team configurations.

This example compares:
1. Baseline: All human team (7 developers)
2. Balanced: Mixed team (5 humans + 4 AI agents)
3. AI-Heavy: Small human team with many AI (3 humans + 10 AI)
4. Premium: Mixed team with high-quality AI model (5 humans + 4 Opus AI)

Use this to answer questions like:
- Should we add AI agents or hire more humans?
- What's the optimal human/AI ratio?
- Is premium AI worth the extra cost?
- What are the quality/speed/cost trade-offs?
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.comparison import ScenarioComparison


def main():
    """Run scenario comparison with pre-built scenarios."""

    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                     SDLC SIMLAB - SCENARIO COMPARISON                   ║
║                                                                          ║
║  Compare multiple team configurations to find the optimal balance of    ║
║  throughput, quality, and cost for your organization.                   ║
╚════════════════════════════════════════════════════════════════════════╝
    """)

    # Create comparison
    comparison = ScenarioComparison(verbose=True)

    # Add scenarios to compare
    scenarios = [
        "data/scenarios/comparison/baseline_human_only.yaml",
        "data/scenarios/comparison/balanced_mixed_team.yaml",
        "data/scenarios/comparison/ai_heavy_team.yaml",
        "data/scenarios/comparison/premium_ai_team.yaml",
    ]

    print("Loading scenarios...")
    comparison.add_scenarios(scenarios)

    # Run all scenarios
    print("\n" + "="*80)
    print("RUNNING SIMULATIONS")
    print("="*80)
    print("\nThis may take a few minutes...\n")

    results = comparison.run_all(parallel=False)  # Set to True for faster execution

    # Display comparison
    comparison.print_comparison()

    # Export results
    print("\nExporting results...")
    comparison.export_to_json("scenario_comparison_results.json")
    comparison.export_to_csv("scenario_comparison_results.csv")

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80 + "\n")

    # Generate custom recommendations
    baseline = results[0]
    balanced = results[1]
    ai_heavy = results[2]
    premium = results[3]

    baseline_throughput = baseline.metrics['prs_per_week']
    balanced_throughput = balanced.metrics['prs_per_week']

    # Calculate improvements
    balanced_improvement = ((balanced_throughput / baseline_throughput) - 1) * 100
    balanced_cost = balanced.metrics['ai_total_cost']

    print(f"1. Moderate AI Augmentation (Balanced Team):")
    print(f"   • {balanced_improvement:+.0f}% throughput increase vs baseline")
    print(f"   • ${balanced_cost:.2f} total AI cost over 12 weeks (${balanced_cost/12:.2f}/week)")
    print(f"   • Recommended if: You want proven productivity gains at reasonable cost\n")

    ai_heavy_throughput = ai_heavy.metrics['prs_per_week']
    ai_heavy_improvement = ((ai_heavy_throughput / baseline_throughput) - 1) * 100
    ai_heavy_cost = ai_heavy.metrics['ai_total_cost']
    ai_heavy_open_prs = ai_heavy.metrics['open_prs']

    print(f"2. Aggressive AI Augmentation (AI-Heavy Team):")
    print(f"   • {ai_heavy_improvement:+.0f}% throughput increase vs baseline")
    print(f"   • ${ai_heavy_cost:.2f} total AI cost (${ai_heavy_cost/12:.2f}/week)")
    print(f"   • {ai_heavy_open_prs} open PRs (potential review bottleneck)")
    print(f"   • Recommended if: You need maximum throughput and have review capacity\n")

    premium_quality = 1.0 - premium.metrics['change_failure_rate']
    balanced_quality = 1.0 - balanced.metrics['change_failure_rate']
    premium_cost = premium.metrics['ai_total_cost']

    print(f"3. Premium AI Model (Opus):")
    quality_diff = (premium_quality - balanced_quality) * 100
    cost_diff = premium_cost - balanced_cost
    print(f"   • {quality_diff:+.1f}% quality difference vs balanced")
    print(f"   • ${cost_diff:+.2f} additional cost vs balanced Sonnet model")
    print(f"   • Recommended if: Quality is critical and cost is secondary concern\n")

    print("="*80)
    print("\nFor detailed metrics, see:")
    print("  - scenario_comparison_results.json (full data)")
    print("  - scenario_comparison_results.csv (spreadsheet)")
    print("\n")


def compare_custom_scenarios():
    """
    Example of comparing custom scenarios programmatically.

    Use this approach when you want to generate scenarios dynamically
    rather than loading from YAML files.
    """
    from src.simulation.config import ScenarioConfig, TeamConfigModel, SimulationConfigModel

    # Create scenarios programmatically
    scenarios = []

    # Scenario 1: Small team
    scenarios.append(ScenarioConfig(
        name="Small Team: 3 Humans",
        description="Minimal viable team",
        team=TeamConfigModel(count=3),
        simulation=SimulationConfigModel(duration_weeks=4, random_seed=42)
    ))

    # Scenario 2: Medium team
    scenarios.append(ScenarioConfig(
        name="Medium Team: 6 Humans",
        description="Standard team size",
        team=TeamConfigModel(count=6),
        simulation=SimulationConfigModel(duration_weeks=4, random_seed=42)
    ))

    # Scenario 3: Large team
    scenarios.append(ScenarioConfig(
        name="Large Team: 12 Humans",
        description="Large coordinated team",
        team=TeamConfigModel(count=12),
        simulation=SimulationConfigModel(duration_weeks=4, random_seed=42)
    ))

    # Compare
    comparison = ScenarioComparison(verbose=True)
    comparison.add_scenarios(scenarios)
    comparison.run_all()
    comparison.print_comparison()


if __name__ == "__main__":
    # Run the main comparison
    main()

    # Uncomment to run custom comparison example:
    # print("\n\n")
    # compare_custom_scenarios()
