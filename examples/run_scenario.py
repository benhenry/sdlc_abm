"""
Run a scenario from a YAML configuration file.

Usage:
    python examples/run_scenario.py data/scenarios/small_team.yaml
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.runner import ScenarioRunner


def main():
    """Run a scenario from command line."""
    if len(sys.argv) < 2:
        print("Usage: python examples/run_scenario.py <scenario_file>")
        print("\nExample scenarios:")
        print("  python examples/run_scenario.py data/scenarios/small_team.yaml")
        print("  python examples/run_scenario.py data/scenarios/distributed_team.yaml")
        print("  python examples/run_scenario.py data/scenarios/rapid_growth.yaml")
        sys.exit(1)

    scenario_path = sys.argv[1]

    # Load and run scenario
    print(f"Loading scenario from: {scenario_path}\n")
    runner = ScenarioRunner.from_yaml(scenario_path)

    # Run simulation
    metrics = runner.run(verbose=True)

    # Show developer stats
    print("\nDeveloper Statistics:")
    print(f"{'Name':<15} {'Level':<10} {'Weeks':<6} {'Onboarded':<12} {'PRs':<6} {'Merged':<8} {'Reverted':<8} {'Reviews':<8}")
    print("-" * 95)

    for stats in runner.get_developer_stats():
        onboarded = "✓" if stats['is_fully_onboarded'] else f"{stats['productivity_multiplier']:.0%}"
        print(
            f"{stats['name'] or 'Unknown':<15} "
            f"{stats['experience_level']:<10} "
            f"{stats['weeks_in_role']:<6} "
            f"{onboarded:<12} "
            f"{stats['total_prs_created']:<6} "
            f"{stats['total_prs_merged']:<8} "
            f"{stats['total_prs_reverted']:<8} "
            f"{stats['total_reviews_completed']:<8}"
        )

    # Optionally export results
    if len(sys.argv) > 2 and sys.argv[2] == '--export':
        output_path = scenario_path.replace('.yaml', '_results.json').replace('.yml', '_results.json')
        runner.export_results(output_path)


if __name__ == "__main__":
    main()
