"""
Integration tests for scenario comparison with real YAML files.
"""

import pytest
from pathlib import Path
from src.simulation.comparison import ScenarioComparison


class TestScenarioComparisonIntegration:
    """Integration tests using actual scenario YAML files."""

    def test_load_and_compare_baseline_scenarios(self):
        """Test loading and comparing the baseline comparison scenarios."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
            "data/scenarios/comparison/ai_heavy_team.yaml",
            "data/scenarios/comparison/premium_ai_team.yaml",
        ]

        comparison.add_scenarios(scenarios)

        assert len(comparison.scenarios) == 4

        results = comparison.run_all()

        assert len(results) == 4
        assert all(result.metrics is not None for result in results)
        assert all(result.metrics.get('total_developers', 0) > 0 for result in results)

    def test_baseline_vs_balanced_comparison(self):
        """Test that balanced mixed team shows expected improvements over baseline."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        baseline = results[0]
        balanced = results[1]

        # Balanced team (5 humans + 4 AI) should have higher throughput than baseline (7 humans)
        assert balanced.metrics['prs_per_week'] > baseline.metrics['prs_per_week']

        # Both should have completed some PRs
        assert baseline.metrics['total_prs_merged'] > 0
        assert balanced.metrics['total_prs_merged'] > 0

        # Balanced should have AI costs, baseline should not
        assert balanced.metrics.get('ai_total_cost', 0) > 0
        assert baseline.metrics.get('ai_total_cost', 0) == 0

    def test_ai_heavy_team_scaling(self):
        """Test that AI-heavy team (3 humans + 10 AI) scales throughput significantly."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/ai_heavy_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        baseline = results[0]
        ai_heavy = results[1]

        # AI-heavy team should have much higher throughput
        throughput_increase = (ai_heavy.metrics['prs_per_week'] / baseline.metrics['prs_per_week']) - 1

        # Should see at least 50% improvement with 10 AI agents
        assert throughput_increase > 0.5

        # AI costs should be substantial
        assert ai_heavy.metrics.get('ai_total_cost', 0) > 0

    def test_premium_vs_standard_ai_quality(self):
        """Test quality differences between premium (Opus) and standard (Sonnet) AI models."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/balanced_mixed_team.yaml",
            "data/scenarios/comparison/premium_ai_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        balanced = results[0]  # Sonnet
        premium = results[1]   # Opus

        # Premium model should have comparable or better quality
        # (Opus has higher quality but lower productivity)
        assert premium.metrics['change_failure_rate'] <= balanced.metrics['change_failure_rate'] * 1.2

        # Premium should cost more due to higher per-PR cost
        assert premium.metrics.get('ai_total_cost', 0) > balanced.metrics.get('ai_total_cost', 0)

    def test_comparison_table_generation(self):
        """Test that comparison table generation works with real scenarios."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        comparison.run_all()

        table = comparison.get_comparison_table()

        assert 'scenarios' in table
        assert 'metrics' in table
        assert 'winners' in table
        assert 'insights' in table
        assert len(table['scenarios']) == 2

    def test_insights_generation_with_real_scenarios(self):
        """Test insights generation with real comparison scenarios."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
            "data/scenarios/comparison/ai_heavy_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        comparison.run_all()

        table = comparison.get_comparison_table()
        insights = table['insights']

        assert len(insights) > 0
        # Should have throughput insight
        assert any('throughput' in insight.lower() for insight in insights)

    def test_json_export_with_real_scenarios(self, tmp_path):
        """Test JSON export with real scenarios."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        comparison.run_all()

        output_file = tmp_path / "comparison_results.json"
        comparison.export_to_json(str(output_file))

        assert output_file.exists()

        # Verify JSON content
        import json
        with open(output_file) as f:
            data = json.load(f)

        assert 'comparison' in data
        assert 'full_results' in data
        assert len(data['full_results']) == 2

        # Check that metrics are present
        for scenario_data in data['full_results']:
            assert 'name' in scenario_data
            assert 'metrics' in scenario_data
            assert 'total_prs_merged' in scenario_data['metrics']

    def test_csv_export_with_real_scenarios(self, tmp_path):
        """Test CSV export with real scenarios."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        comparison.run_all()

        output_file = tmp_path / "comparison_results.csv"
        comparison.export_to_csv(str(output_file))

        assert output_file.exists()

        # Verify CSV content
        import csv
        with open(output_file) as f:
            reader = csv.reader(f)
            rows = list(reader)

        # CSV should have header + metric rows
        assert len(rows) > 1
        header = rows[0]
        assert 'Metric' in header
        assert len(header) == 3  # Metric + 2 scenarios

    def test_all_four_scenarios_complete_successfully(self):
        """Test that all four comparison scenarios run to completion."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
            "data/scenarios/comparison/ai_heavy_team.yaml",
            "data/scenarios/comparison/premium_ai_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        # All scenarios should complete
        assert len(results) == 4

        # All should have valid metrics
        for result in results:
            assert result.metrics['total_prs_merged'] >= 0
            assert result.metrics['prs_per_week'] >= 0
            assert result.metrics['avg_cycle_time_days'] >= 0
            assert 0 <= result.metrics['change_failure_rate'] <= 1

    def test_comparison_reproducibility(self):
        """Test that comparison results are reproducible with same seed."""
        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        # Run first comparison
        comparison1 = ScenarioComparison(verbose=False)
        comparison1.add_scenarios(scenarios)
        results1 = comparison1.run_all()

        # Run second comparison
        comparison2 = ScenarioComparison(verbose=False)
        comparison2.add_scenarios(scenarios)
        results2 = comparison2.run_all()

        # Results should be identical (scenarios all use seed=42)
        for r1, r2 in zip(results1, results2):
            assert r1.name == r2.name
            assert r1.metrics['total_prs_merged'] == r2.metrics['total_prs_merged']
            assert r1.metrics['prs_per_week'] == r2.metrics['prs_per_week']

    def test_mixed_team_human_ai_separation(self):
        """Test that mixed teams correctly track human vs AI contributions."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        result = results[0]

        # Should have both human and AI metrics
        assert 'human_prs_merged' in result.metrics
        assert 'ai_prs_merged' in result.metrics

        # Both humans and AI should contribute
        assert result.metrics['human_prs_merged'] > 0
        assert result.metrics['ai_prs_merged'] > 0

        # Total should equal sum
        assert result.metrics['total_prs_merged'] == (
            result.metrics['human_prs_merged'] + result.metrics['ai_prs_merged']
        )

    def test_team_size_calculation_includes_ai(self):
        """Test that team size includes both humans and AI agents."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",   # 7 humans
            "data/scenarios/comparison/balanced_mixed_team.yaml",   # 5 humans + 4 AI = 9
            "data/scenarios/comparison/ai_heavy_team.yaml",         # 3 humans + 10 AI = 13
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        baseline = results[0]
        balanced = results[1]
        ai_heavy = results[2]

        assert baseline.metrics['total_developers'] == 7
        assert balanced.metrics['total_developers'] == 9
        assert ai_heavy.metrics['total_developers'] == 13

    def test_cost_tracking_accuracy(self):
        """Test that AI cost tracking is accurate across scenarios."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
            "data/scenarios/comparison/ai_heavy_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        results = comparison.run_all()

        baseline = results[0]
        balanced = results[1]
        ai_heavy = results[2]

        # Baseline should have zero AI cost
        assert baseline.metrics.get('ai_total_cost', 0) == 0

        # AI-heavy should cost more than balanced (more agents)
        assert ai_heavy.metrics['ai_total_cost'] > balanced.metrics['ai_total_cost']

        # Cost should correlate with AI PRs created
        balanced_cost_per_pr = balanced.metrics['ai_total_cost'] / balanced.metrics['ai_prs_merged']
        ai_heavy_cost_per_pr = ai_heavy.metrics['ai_total_cost'] / ai_heavy.metrics['ai_prs_merged']

        # Should be using same model (Sonnet), so cost per PR should be similar
        assert abs(balanced_cost_per_pr - ai_heavy_cost_per_pr) < 0.01

    def test_invalid_scenario_file(self):
        """Test handling of invalid scenario file."""
        comparison = ScenarioComparison(verbose=False)

        with pytest.raises(FileNotFoundError):
            comparison.add_scenario("data/scenarios/nonexistent_file.yaml")

    def test_print_comparison_does_not_crash(self, capsys):
        """Test that print_comparison produces output without crashing."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            "data/scenarios/comparison/balanced_mixed_team.yaml",
        ]

        comparison.add_scenarios(scenarios)
        comparison.run_all()

        # Should not raise any exceptions
        comparison.print_comparison()

        # Should produce output
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "Baseline" in captured.out
        assert "Balanced" in captured.out
