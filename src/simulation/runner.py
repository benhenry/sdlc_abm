"""
Scenario runner - executes simulations from configuration files.
"""

from pathlib import Path
from typing import Optional, Union

from .config import ScenarioConfig
from .engine import SDLCSimulation
from .agents.developer import Developer
from .agents.ai_agent import AIAgent


class ScenarioRunner:
    """
    Runs simulations from scenario configurations.

    Handles loading scenarios, creating simulations, and collecting results.
    """

    def __init__(self, scenario: ScenarioConfig):
        """
        Initialize scenario runner.

        Args:
            scenario: Scenario configuration
        """
        self.scenario = scenario
        self.simulation: Optional[SDLCSimulation] = None

    @classmethod
    def from_yaml(cls, file_path: Union[str, Path]) -> "ScenarioRunner":
        """
        Create runner from YAML file.

        Args:
            file_path: Path to YAML scenario file

        Returns:
            ScenarioRunner instance
        """
        scenario = ScenarioConfig.from_yaml(file_path)
        return cls(scenario)

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "ScenarioRunner":
        """
        Create runner from JSON file.

        Args:
            file_path: Path to JSON scenario file

        Returns:
            ScenarioRunner instance
        """
        scenario = ScenarioConfig.from_json(file_path)
        return cls(scenario)

    def setup(self) -> SDLCSimulation:
        """
        Create and configure the simulation from the scenario.

        Returns:
            Configured SDLCSimulation instance
        """
        # Create simulation with parameters from config
        sim = SDLCSimulation(
            name=self.scenario.name,
            timestep_days=self.scenario.simulation.timestep_days,
            random_seed=self.scenario.simulation.random_seed,
            communication_loss_factor=self.scenario.simulation.communication_loss_factor,
            communication_overhead_model=self.scenario.get_communication_overhead_model()
        )

        # Add human developers to the simulation
        developer_configs = self.scenario.team.get_developers()
        for dev_config in developer_configs:
            developer = Developer(config=dev_config)
            sim.add_developer(developer)

        # Add AI agents to the simulation
        ai_agent_configs = self.scenario.team.get_ai_agents()
        for ai_config in ai_agent_configs:
            ai_agent = AIAgent(config=ai_config)
            sim.add_ai_agent(ai_agent)

        self.simulation = sim
        return sim

    def run(self, verbose: bool = True) -> dict:
        """
        Run the simulation and return results.

        Args:
            verbose: Whether to print progress

        Returns:
            Dictionary of simulation metrics
        """
        if self.simulation is None:
            self.setup()

        if verbose:
            print(f"\n{'='*80}")
            print(f"Running Scenario: {self.scenario.name}")
            print(f"{'='*80}")
            if self.scenario.description:
                print(f"{self.scenario.description}\n")
            human_count = len(self.simulation.human_developers)
            ai_count = len(self.simulation.ai_agents)
            print(f"Team Size: {len(self.simulation.developers)} total")
            print(f"  - Humans: {human_count}")
            print(f"  - AI Agents: {ai_count}")
            print(f"Duration: {self.scenario.simulation.duration_weeks} weeks")
            print(f"Communication Loss: {self.scenario.simulation.communication_loss_factor:.0%}")
            print(f"Overhead Model: {self.scenario.simulation.communication_overhead_model}")
            print(f"\nRunning simulation...")

        # Run the simulation
        num_days = self.scenario.simulation.duration_weeks * 7
        self.simulation.run(num_days)

        # Get final metrics
        metrics = self.simulation.get_metrics()

        if verbose:
            print("\n" + "="*80)
            print("Simulation Complete")
            print("="*80)
            self.simulation.print_summary()

        return metrics

    def get_developer_stats(self) -> list[dict]:
        """
        Get statistics for all developers.

        Returns:
            List of developer stat dictionaries
        """
        if self.simulation is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        return [dev.get_stats() for dev in self.simulation.developers]

    def export_results(self, output_path: Union[str, Path]) -> None:
        """
        Export simulation results to JSON.

        Args:
            output_path: Path to save results
        """
        import json

        if self.simulation is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        results = {
            "scenario": {
                "name": self.scenario.name,
                "description": self.scenario.description,
                "tags": self.scenario.tags,
            },
            "configuration": self.scenario.model_dump(),
            "metrics": self.simulation.get_metrics(),
            "developers": self.get_developer_stats(),
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "timestep": e.timestep,
                    "agent_id": e.agent_id,
                    "data": e.data
                }
                for e in self.simulation.events
            ]
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults exported to: {output_path}")


def run_scenario_file(file_path: Union[str, Path], verbose: bool = True) -> dict:
    """
    Convenience function to run a scenario from a file.

    Args:
        file_path: Path to YAML or JSON scenario file
        verbose: Whether to print progress

    Returns:
        Dictionary of simulation metrics
    """
    path = Path(file_path)

    if path.suffix in ['.yaml', '.yml']:
        runner = ScenarioRunner.from_yaml(path)
    elif path.suffix == '.json':
        runner = ScenarioRunner.from_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .yaml, .yml, or .json")

    metrics = runner.run(verbose=verbose)
    return metrics
