"""
Import historical data from CSV and generate scenario configuration.

Usage:
    python examples/import_historical_data.py <csv_file> [--output scenario.yaml]

Examples:
    # Import and analyze data
    python examples/import_historical_data.py data/samples/sample_prs.csv

    # Import and generate scenario
    python examples/import_historical_data.py data/samples/sample_prs.csv --output data/scenarios/my_team.yaml

    # Import with custom format (GitLab)
    python examples/import_historical_data.py data/gitlab_mrs.csv --format gitlab

    # Import and run simulation
    python examples/import_historical_data.py data/samples/sample_prs.csv --run
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.data_import import CSVDataImporter
from src.simulation.runner import ScenarioRunner


def main():
    """Import historical data from CSV."""
    parser = argparse.ArgumentParser(
        description='Import historical team data from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'csv_file',
        help='Path to CSV file with PR/MR data'
    )

    parser.add_argument(
        '--format',
        choices=['github', 'gitlab', 'generic'],
        default='github',
        help='CSV format (default: github)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output path for generated scenario YAML file'
    )

    parser.add_argument(
        '--run',
        action='store_true',
        help='Run simulation after generating scenario'
    )

    parser.add_argument(
        '--name',
        default='Imported Team Scenario',
        help='Scenario name (default: Imported Team Scenario)'
    )

    args = parser.parse_args()

    # Import data
    print(f"\nImporting data from: {args.csv_file}")
    print(f"Format: {args.format}\n")

    importer = CSVDataImporter()

    try:
        if args.format == 'github':
            importer.import_github_prs(args.csv_file)
        elif args.format == 'gitlab':
            # GitLab uses similar format
            importer.import_github_prs(args.csv_file)
        else:
            importer.import_generic_csv(args.csv_file)

        print(f"✓ Imported {len(importer.pr_records)} PR records")

        # Analyze data
        print("\nAnalyzing historical data...")
        importer.analyze_developers()

        # Print summary
        importer.print_summary()

        # Generate scenario
        print("\nGenerating scenario configuration...")
        scenario = importer.generate_scenario(name=args.name)

        # Save if output specified
        if args.output:
            output_path = Path(args.output)
            scenario.to_yaml(output_path)
            print(f"\n✓ Scenario saved to: {output_path}")

        # Run simulation if requested
        if args.run:
            print("\n" + "="*80)
            print("Running Simulation from Historical Data")
            print("="*80)

            runner = ScenarioRunner(scenario)
            metrics = runner.run(verbose=True)

            # Show developer stats
            print("\nDeveloper Statistics:")
            print(f"{'Name':<15} {'Level':<10} {'PRs':<6} {'Merged':<8} {'Reverted':<8} {'Reviews':<8}")
            print("-" * 70)

            for stats in runner.get_developer_stats():
                print(
                    f"{stats['name'] or 'Unknown':<15} "
                    f"{stats['experience_level']:<10} "
                    f"{stats['total_prs_created']:<6} "
                    f"{stats['total_prs_merged']:<8} "
                    f"{stats['total_prs_reverted']:<8} "
                    f"{stats['total_reviews_completed']:<8}"
                )

    except FileNotFoundError:
        print(f"Error: File not found: {args.csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error importing data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
