"""
Unit tests for scenario comparison functionality.
"""

import pytest
from pathlib import Path
from src.simulation.comparison import ScenarioComparison, ScenarioResult
from src.simulation.config import ScenarioConfig, TeamConfigModel, SimulationConfigModel


class TestScenarioComparison:
    """Test ScenarioComparison class."""

    def test_initialization(self):
        """Test ScenarioComparison initialization with verbose=False."""
        comparison = ScenarioComparison(verbose=False)
        assert comparison.scenarios == []
        assert comparison.results == []
        assert comparison.verbose is False

    def test_initialization_verbose(self):
        """Test verbose mode initialization."""
        comparison = ScenarioComparison(verbose=True)
        assert comparison.verbose is True

    def test_initialization_default_verbose(self):
        """Test that verbose defaults to True."""
        comparison = ScenarioComparison()
        assert comparison.verbose is True

    def test_add_scenario_from_config(self):
        """Test adding scenario from ScenarioConfig object."""
        comparison = ScenarioComparison(verbose=False)
        config = ScenarioConfig(
            name="Test Scenario",
            description="Test description",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=2, random_seed=42)
        )

        comparison.add_scenario(config)
        assert len(comparison.scenarios) == 1
        assert comparison.scenarios[0].name == "Test Scenario"

    def test_add_scenario_from_yaml(self):
        """Test adding scenario from YAML file."""
        comparison = ScenarioComparison(verbose=False)
        yaml_path = "data/scenarios/comparison/baseline_human_only.yaml"

        comparison.add_scenario(yaml_path)
        assert len(comparison.scenarios) == 1
        assert "Baseline" in comparison.scenarios[0].name

    def test_add_scenarios_multiple(self):
        """Test adding multiple scenarios at once."""
        comparison = ScenarioComparison(verbose=False)
        scenarios = [
            ScenarioConfig(
                name="Scenario 1",
                team=TeamConfigModel(count=3),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
            ScenarioConfig(
                name="Scenario 2",
                team=TeamConfigModel(count=5),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
        ]

        comparison.add_scenarios(scenarios)
        assert len(comparison.scenarios) == 2
        assert comparison.scenarios[0].name == "Scenario 1"
        assert comparison.scenarios[1].name == "Scenario 2"

    def test_add_scenarios_mixed_types(self):
        """Test adding scenarios from mixed sources."""
        comparison = ScenarioComparison(verbose=False)
        scenarios = [
            "data/scenarios/comparison/baseline_human_only.yaml",
            ScenarioConfig(
                name="Custom Scenario",
                team=TeamConfigModel(count=4),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
        ]

        comparison.add_scenarios(scenarios)
        assert len(comparison.scenarios) == 2

    def test_run_all_no_scenarios(self):
        """Test running comparison with no scenarios."""
        comparison = ScenarioComparison(verbose=False)

        with pytest.raises(ValueError, match="No scenarios added"):
            comparison.run_all()

    def test_run_all_single_scenario(self):
        """Test running a single scenario."""
        comparison = ScenarioComparison(verbose=False)
        config = ScenarioConfig(
            name="Single Test",
            team=TeamConfigModel(count=3),
            simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
        )
        comparison.add_scenario(config)

        results = comparison.run_all()

        assert len(results) == 1
        assert len(comparison.results) == 1
        assert results[0].name == "Single Test"
        assert isinstance(results[0].metrics, dict)
        assert 'total_prs_merged' in results[0].metrics

    def test_run_all_multiple_scenarios(self):
        """Test running multiple scenarios."""
        comparison = ScenarioComparison(verbose=False)
        scenarios = [
            ScenarioConfig(
                name=f"Scenario {i}",
                team=TeamConfigModel(count=3 + i),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            )
            for i in range(3)
        ]
        comparison.add_scenarios(scenarios)

        results = comparison.run_all()

        assert len(results) == 3
        assert len(comparison.results) == 3
        for i, result in enumerate(results):
            assert result.name == f"Scenario {i}"

    def test_get_comparison_table_no_results(self):
        """Test getting comparison table with no results."""
        comparison = ScenarioComparison(verbose=False)

        with pytest.raises(ValueError, match="No results available"):
            comparison.get_comparison_table()

    def test_get_comparison_table_with_results(self):
        """Test getting comparison table with results."""
        comparison = ScenarioComparison(verbose=False)
        config = ScenarioConfig(
            name="Test Scenario",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=2, random_seed=42)
        )
        comparison.add_scenario(config)
        comparison.run_all()

        table = comparison.get_comparison_table()

        assert isinstance(table, dict)
        assert 'scenarios' in table
        assert 'metrics' in table
        assert 'winners' in table
        assert 'insights' in table

    def test_generate_insights(self):
        """Test insights generation."""
        comparison = ScenarioComparison(verbose=False)
        scenarios = [
            ScenarioConfig(
                name=f"Scenario {i}",
                team=TeamConfigModel(count=3 + i * 2),
                simulation=SimulationConfigModel(duration_weeks=2, random_seed=42)
            )
            for i in range(3)
        ]
        comparison.add_scenarios(scenarios)
        comparison.run_all()

        insights = comparison._generate_insights()

        assert isinstance(insights, list)
        assert len(insights) > 0
        # Should have throughput insight at minimum
        assert any('throughput' in insight.lower() for insight in insights)

    def test_export_to_json_no_results(self):
        """Test JSON export with no results."""
        comparison = ScenarioComparison(verbose=False)

        with pytest.raises(ValueError, match="No results available"):
            comparison.export_to_json("test.json")

    def test_export_to_json(self, tmp_path):
        """Test JSON export."""
        comparison = ScenarioComparison(verbose=False)
        config = ScenarioConfig(
            name="Export Test",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
        )
        comparison.add_scenario(config)
        comparison.run_all()

        output_file = tmp_path / "test_output.json"
        comparison.export_to_json(str(output_file))

        assert output_file.exists()

        # Verify JSON structure
        import json
        with open(output_file) as f:
            data = json.load(f)

        assert 'comparison' in data
        assert 'full_results' in data
        assert len(data['full_results']) == 1
        assert data['full_results'][0]['name'] == "Export Test"

    def test_export_to_csv_no_results(self):
        """Test CSV export with no results."""
        comparison = ScenarioComparison(verbose=False)

        with pytest.raises(ValueError, match="No results available"):
            comparison.export_to_csv("test.csv")

    def test_export_to_csv(self, tmp_path):
        """Test CSV export."""
        comparison = ScenarioComparison(verbose=False)
        config = ScenarioConfig(
            name="CSV Test",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
        )
        comparison.add_scenario(config)
        comparison.run_all()

        output_file = tmp_path / "test_output.csv"
        comparison.export_to_csv(str(output_file))

        assert output_file.exists()

        # Verify CSV structure
        import csv
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # CSV has metrics as rows, scenarios as columns
        assert len(rows) > 0
        assert 'Metric' in rows[0]

    def test_scenario_result_creation(self):
        """Test ScenarioResult dataclass creation."""
        config = ScenarioConfig(
            name="Test",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
        )
        result = ScenarioResult(
            name="Test",
            description="Test description",
            metrics={'prs_merged': 100},
            config=config
        )

        assert result.name == "Test"
        assert result.description == "Test description"
        assert result.metrics['prs_merged'] == 100
        assert result.config.name == "Test"

    def test_scenario_result_get_metric(self):
        """Test ScenarioResult get_metric method."""
        config = ScenarioConfig(
            name="Test",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
        )
        result = ScenarioResult(
            name="Test",
            description=None,
            metrics={'prs_merged': 100},
            config=config
        )

        assert result.get_metric('prs_merged') == 100
        assert result.get_metric('nonexistent') == 0
        assert result.get_metric('nonexistent', 99) == 99

    def test_comparison_preserves_random_seed(self):
        """Test that scenarios with same seed produce consistent results."""
        config1 = ScenarioConfig(
            name="Run 1",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=2, random_seed=42)
        )
        config2 = ScenarioConfig(
            name="Run 2",
            team=TeamConfigModel(count=5),
            simulation=SimulationConfigModel(duration_weeks=2, random_seed=42)
        )

        comparison1 = ScenarioComparison(verbose=False)
        comparison1.add_scenario(config1)
        results1 = comparison1.run_all()

        comparison2 = ScenarioComparison(verbose=False)
        comparison2.add_scenario(config2)
        results2 = comparison2.run_all()

        # Results should be identical with same seed
        assert results1[0].metrics['total_prs_merged'] == results2[0].metrics['total_prs_merged']
        assert results1[0].metrics['prs_per_week'] == results2[0].metrics['prs_per_week']

    def test_winner_identification_highest_is_better(self):
        """Test that winner identification correctly identifies highest values for throughput metrics."""
        comparison = ScenarioComparison(verbose=False)

        # Create scenarios with known different throughputs
        scenarios = [
            ScenarioConfig(
                name="Small Team",
                team=TeamConfigModel(count=2),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
            ScenarioConfig(
                name="Large Team",
                team=TeamConfigModel(count=8),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
        ]
        comparison.add_scenarios(scenarios)
        comparison.run_all()

        table = comparison.get_comparison_table()

        # Larger team should have higher throughput
        large_team_result = [r for r in comparison.results if r.name == "Large Team"][0]
        small_team_result = [r for r in comparison.results if r.name == "Small Team"][0]

        assert large_team_result.metrics['prs_per_week'] > small_team_result.metrics['prs_per_week']

        # Winner for prs_per_week should be the large team
        assert table['metrics']['prs_per_week']['best_scenario'] == "Large Team"

    def test_print_comparison_no_results(self):
        """Test print_comparison with no results raises error."""
        comparison = ScenarioComparison(verbose=False)

        with pytest.raises(ValueError, match="No results available"):
            comparison.print_comparison()

    def test_print_comparison_does_not_crash(self, capsys):
        """Test that print_comparison produces output without crashing."""
        comparison = ScenarioComparison(verbose=False)

        scenarios = [
            ScenarioConfig(
                name="Scenario A",
                team=TeamConfigModel(count=3),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
            ScenarioConfig(
                name="Scenario B",
                team=TeamConfigModel(count=5),
                simulation=SimulationConfigModel(duration_weeks=1, random_seed=42)
            ),
        ]

        comparison.add_scenarios(scenarios)
        comparison.run_all()

        # Should not raise any exceptions
        comparison.print_comparison()

        # Should produce output
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "Scenario A" in captured.out
        assert "Scenario B" in captured.out
        assert "SCENARIO COMPARISON RESULTS" in captured.out
