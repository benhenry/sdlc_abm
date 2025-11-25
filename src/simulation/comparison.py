"""
Scenario Comparison Tool

Compare multiple simulation scenarios to understand trade-offs and
identify optimal configurations.

Usage:
    comparison = ScenarioComparison()
    comparison.add_scenario("data/scenarios/scenario1.yaml")
    comparison.add_scenario("data/scenarios/scenario2.yaml")
    results = comparison.run_all()
    comparison.print_comparison()
    comparison.export_to_csv("comparison.csv")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed

from .config import ScenarioConfig
from .runner import ScenarioRunner


@dataclass
class ScenarioResult:
    """Results from running a single scenario."""
    name: str
    description: Optional[str]
    metrics: Dict[str, Any]
    config: ScenarioConfig

    def get_metric(self, key: str, default: Any = 0) -> Any:
        """Get a metric value with fallback to default."""
        return self.metrics.get(key, default)


class ScenarioComparison:
    """
    Compare multiple simulation scenarios.

    Enables "what-if" analysis by running multiple scenarios and
    comparing their outcomes across various metrics.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize scenario comparison.

        Args:
            verbose: Print progress information
        """
        self.scenarios: List[ScenarioConfig] = []
        self.results: List[ScenarioResult] = []
        self.verbose = verbose

    def add_scenario(self, scenario: Union[str, Path, ScenarioConfig]) -> None:
        """
        Add a scenario to compare.

        Args:
            scenario: Path to YAML/JSON file or ScenarioConfig object
        """
        if isinstance(scenario, (str, Path)):
            path = Path(scenario)
            if path.suffix in ['.yaml', '.yml']:
                config = ScenarioConfig.from_yaml(path)
            elif path.suffix == '.json':
                config = ScenarioConfig.from_json(path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        else:
            config = scenario

        self.scenarios.append(config)

        if self.verbose:
            print(f"Added scenario: {config.name}")

    def add_scenarios(self, scenarios: List[Union[str, Path, ScenarioConfig]]) -> None:
        """
        Add multiple scenarios at once.

        Args:
            scenarios: List of scenario paths or configs
        """
        for scenario in scenarios:
            self.add_scenario(scenario)

    def run_all(self, parallel: bool = False) -> List[ScenarioResult]:
        """
        Run all scenarios and collect results.

        Args:
            parallel: Run scenarios in parallel (faster but uses more resources)

        Returns:
            List of scenario results
        """
        if not self.scenarios:
            raise ValueError("No scenarios added. Use add_scenario() first.")

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"SCENARIO COMPARISON - Running {len(self.scenarios)} scenarios")
            print(f"{'='*80}\n")

        if parallel:
            self.results = self._run_parallel()
        else:
            self.results = self._run_sequential()

        if self.verbose:
            print(f"\n{'='*80}")
            print("All scenarios complete!")
            print(f"{'='*80}\n")

        return self.results

    def _run_sequential(self) -> List[ScenarioResult]:
        """Run scenarios one at a time."""
        results = []

        for i, config in enumerate(self.scenarios, 1):
            if self.verbose:
                print(f"\n[{i}/{len(self.scenarios)}] Running: {config.name}")
                print("-" * 80)

            runner = ScenarioRunner(config)
            metrics = runner.run(verbose=self.verbose)

            results.append(ScenarioResult(
                name=config.name,
                description=config.description,
                metrics=metrics,
                config=config
            ))

        return results

    def _run_parallel(self) -> List[ScenarioResult]:
        """Run scenarios in parallel using ProcessPoolExecutor."""
        results = []

        if self.verbose:
            print(f"Running {len(self.scenarios)} scenarios in parallel...\n")

        def run_scenario(config: ScenarioConfig) -> ScenarioResult:
            """Helper function for parallel execution."""
            runner = ScenarioRunner(config)
            metrics = runner.run(verbose=False)  # Disable verbose in parallel mode
            return ScenarioResult(
                name=config.name,
                description=config.description,
                metrics=metrics,
                config=config
            )

        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(run_scenario, config): config
                      for config in self.scenarios}

            for future in as_completed(futures):
                config = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    if self.verbose:
                        print(f"✓ Completed: {config.name}")
                except Exception as e:
                    print(f"✗ Failed: {config.name} - {e}")

        # Sort results to match original order
        results.sort(key=lambda r: [s.name for s in self.scenarios].index(r.name))

        return results

    def get_comparison_table(self) -> Dict[str, Any]:
        """
        Generate comparison table data.

        Returns:
            Dictionary with comparison data and analysis
        """
        if not self.results:
            raise ValueError("No results available. Run run_all() first.")

        # Define metrics to compare
        metrics_to_compare = [
            ('total_developers', 'Team Size', False),
            ('human_developers', 'Humans', False),
            ('ai_agents', 'AI Agents', False),
            ('prs_per_week', 'PRs/Week', True),
            ('change_failure_rate', 'Failure Rate', False),
            ('avg_cycle_time_days', 'Avg Cycle Time', False),
            ('ai_total_cost', 'AI Cost', False),
            ('human_prs_per_week', 'Human PRs/Week', True),
            ('ai_prs_per_week', 'AI PRs/Week', True),
        ]

        # Build comparison data
        comparison = {
            'scenarios': [r.name for r in self.results],
            'metrics': {},
            'winners': {},
            'insights': []
        }

        for metric_key, metric_name, higher_is_better in metrics_to_compare:
            values = [r.get_metric(metric_key) for r in self.results]

            # Find best scenario for this metric
            if all(v == 0 for v in values):
                best_idx = None
            elif higher_is_better:
                best_idx = values.index(max(values))
            else:
                non_zero_values = [v if v > 0 else float('inf') for v in values]
                best_idx = non_zero_values.index(min(non_zero_values))

            comparison['metrics'][metric_key] = {
                'name': metric_name,
                'values': values,
                'best_scenario': self.results[best_idx].name if best_idx is not None else None,
                'higher_is_better': higher_is_better
            }

            if best_idx is not None:
                if metric_key not in comparison['winners']:
                    comparison['winners'][metric_key] = []
                comparison['winners'][metric_key] = self.results[best_idx].name

        # Generate insights
        comparison['insights'] = self._generate_insights()

        return comparison

    def _generate_insights(self) -> List[str]:
        """Generate insights from comparison."""
        insights = []

        if not self.results:
            return insights

        # Throughput leader
        throughputs = [(r.name, r.get_metric('prs_per_week')) for r in self.results]
        best_throughput = max(throughputs, key=lambda x: x[1])
        insights.append(
            f"Highest throughput: {best_throughput[0]} with {best_throughput[1]:.1f} PRs/week"
        )

        # Quality leader (lowest failure rate)
        failure_rates = [(r.name, r.get_metric('change_failure_rate'))
                        for r in self.results if r.get_metric('change_failure_rate') > 0]
        if failure_rates:
            best_quality = min(failure_rates, key=lambda x: x[1])
            insights.append(
                f"Best quality: {best_quality[0]} with {best_quality[1]:.1%} failure rate"
            )

        # Cost efficiency (if AI agents present)
        ai_costs = [(r.name, r.get_metric('ai_total_cost'), r.get_metric('prs_per_week'))
                   for r in self.results if r.get_metric('ai_agents', 0) > 0]
        if ai_costs:
            # Calculate PRs per dollar
            efficiencies = [(name, prs/max(cost, 0.01)) for name, cost, prs in ai_costs]
            best_efficiency = max(efficiencies, key=lambda x: x[1])
            insights.append(
                f"Most cost-efficient: {best_efficiency[0]} with {best_efficiency[1]:.1f} PRs/$"
            )

        # Team composition insights
        all_human = [r for r in self.results if r.get_metric('ai_agents', 0) == 0]
        mixed_teams = [r for r in self.results if r.get_metric('ai_agents', 0) > 0]

        if all_human and mixed_teams:
            avg_human_throughput = sum(r.get_metric('prs_per_week') for r in all_human) / len(all_human)
            avg_mixed_throughput = sum(r.get_metric('prs_per_week') for r in mixed_teams) / len(mixed_teams)

            if avg_mixed_throughput > avg_human_throughput:
                improvement = ((avg_mixed_throughput / avg_human_throughput) - 1) * 100
                insights.append(
                    f"Mixed teams avg {improvement:.0f}% higher throughput than human-only teams"
                )

        return insights

    def print_comparison(self) -> None:
        """Print formatted comparison table to console."""
        if not self.results:
            raise ValueError("No results available. Run run_all() first.")

        comparison = self.get_comparison_table()

        print(f"\n{'='*100}")
        print("SCENARIO COMPARISON RESULTS")
        print(f"{'='*100}\n")

        # Print scenario names
        print("Scenarios:")
        for i, name in enumerate(comparison['scenarios'], 1):
            result = self.results[i-1]
            print(f"  [{i}] {name}")
            if result.description:
                print(f"      {result.description}")

        print(f"\n{'-'*100}")
        print("METRICS COMPARISON")
        print(f"{'-'*100}\n")

        # Print metrics table
        header = f"{'Metric':<30}"
        for i in range(len(self.results)):
            header += f" | Scenario {i+1:>2}"
        header += " | Winner"
        print(header)
        print("-" * 100)

        for metric_key, metric_data in comparison['metrics'].items():
            row = f"{metric_data['name']:<30}"

            for i, value in enumerate(metric_data['values']):
                is_best = (self.results[i].name == metric_data['best_scenario'])

                # Format value
                if isinstance(value, float):
                    if metric_key.endswith('_rate'):
                        formatted = f"{value:.1%}"
                    else:
                        formatted = f"{value:.1f}"
                else:
                    formatted = str(value)

                # Add marker for best
                if is_best:
                    formatted += " ★"

                row += f" | {formatted:>12}"

            # Add winner column
            winner_idx = comparison['scenarios'].index(metric_data['best_scenario']) + 1 if metric_data['best_scenario'] else 0
            row += f" | Scenario {winner_idx}" if winner_idx > 0 else " | -"

            print(row)

        # Print insights
        if comparison['insights']:
            print(f"\n{'-'*100}")
            print("KEY INSIGHTS")
            print(f"{'-'*100}\n")

            for insight in comparison['insights']:
                print(f"  • {insight}")

        print(f"\n{'='*100}\n")

    def export_to_json(self, filepath: Union[str, Path]) -> None:
        """
        Export comparison results to JSON.

        Args:
            filepath: Path to save JSON file
        """
        if not self.results:
            raise ValueError("No results available. Run run_all() first.")

        comparison = self.get_comparison_table()

        # Add full results for reference
        export_data = {
            'comparison': comparison,
            'full_results': [
                {
                    'name': r.name,
                    'description': r.description,
                    'metrics': r.metrics,
                }
                for r in self.results
            ]
        }

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2)

        if self.verbose:
            print(f"Comparison exported to: {filepath}")

    def export_to_csv(self, filepath: Union[str, Path]) -> None:
        """
        Export comparison results to CSV.

        Args:
            filepath: Path to save CSV file
        """
        if not self.results:
            raise ValueError("No results available. Run run_all() first.")

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            header = ['Metric'] + [r.name for r in self.results]
            writer.writerow(header)

            # Write metrics
            comparison = self.get_comparison_table()
            for metric_key, metric_data in comparison['metrics'].items():
                row = [metric_data['name']] + metric_data['values']
                writer.writerow(row)

        if self.verbose:
            print(f"Comparison exported to: {filepath}")
