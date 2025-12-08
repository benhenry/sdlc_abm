"""Celery tasks for asynchronous simulation execution

Defines Celery app and background tasks for running simulations and comparisons.
"""

import os
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from celery import Celery
from pydantic import ValidationError

# Import simulation engine
from src.simulation.config import ScenarioConfig
from src.simulation.runner import ScenarioRunner
from src.simulation.comparison import ScenarioComparison

# Configure Celery
celery_app = Celery(
    "sdlc_simlab",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name="tasks.run_simulation")
def run_simulation_task(
    self,
    simulation_id: str,
    config_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Run a single simulation

    Args:
        self: Celery task instance (for progress updates)
        simulation_id: UUID of the simulation run
        config_dict: Scenario configuration as dictionary

    Returns:
        Dict with simulation results including metrics and developer stats
    """
    try:
        # Update task state to STARTED
        self.update_state(
            state="STARTED",
            meta={"status": "Initializing simulation", "progress": 0.0}
        )

        # Parse configuration
        try:
            config = ScenarioConfig(**config_dict)
        except ValidationError as e:
            return {
                "status": "failed",
                "error": f"Invalid configuration: {str(e)}"
            }

        # Create scenario runner
        runner = ScenarioRunner(config)

        # Setup simulation
        self.update_state(
            state="PROGRESS",
            meta={"status": "Setting up simulation", "progress": 0.05}
        )

        simulation = runner.setup_simulation()
        total_steps = simulation.duration_weeks * 5  # 5 working days per week

        # Run simulation with progress updates
        for step in range(total_steps):
            simulation.step()

            # Update progress every 10 steps or on last step
            if step % 10 == 0 or step == total_steps - 1:
                progress = (step + 1) / total_steps
                current_metrics = simulation.get_metrics()

                self.update_state(
                    state="PROGRESS",
                    meta={
                        "status": "running",
                        "progress": progress,
                        "current_step": step + 1,
                        "total_steps": total_steps,
                        "current_metrics": current_metrics
                    }
                )

                # Publish to Redis for WebSocket (optional)
                # This allows real-time updates to connected clients
                publish_simulation_update(
                    simulation_id,
                    progress,
                    current_metrics,
                    step + 1,
                    total_steps
                )

        # Get final results
        results = simulation.get_metrics()
        developer_stats = runner.get_developer_stats()

        return {
            "status": "completed",
            "metrics": results,
            "developer_stats": developer_stats,
            "completed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        # Log error and return failure status
        print(f"Simulation error: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__
        }


@celery_app.task(bind=True, name="tasks.run_comparison")
def run_comparison_task(
    self,
    comparison_id: str,
    scenario_configs: list[Dict[str, Any]]
) -> Dict[str, Any]:
    """Run a comparison of multiple scenarios

    Args:
        self: Celery task instance
        comparison_id: UUID of the comparison
        scenario_configs: List of scenario configurations

    Returns:
        Dict with comparison results and insights
    """
    try:
        self.update_state(
            state="STARTED",
            meta={"status": "Initializing comparison", "progress": 0.0}
        )

        # Parse configurations
        configs = []
        for i, config_dict in enumerate(scenario_configs):
            try:
                config = ScenarioConfig(**config_dict)
                configs.append(config)
            except ValidationError as e:
                return {
                    "status": "failed",
                    "error": f"Invalid configuration {i}: {str(e)}"
                }

        # Create comparison
        comparison = ScenarioComparison()

        # Run each scenario
        total = len(configs)
        for i, config in enumerate(configs):
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": f"Running scenario {i+1}/{total}",
                    "progress": i / total
                }
            )

            scenario_name = config.name or f"Scenario {i+1}"
            comparison.add_scenario(scenario_name, config)

        # Run comparison
        self.update_state(
            state="PROGRESS",
            meta={"status": "Analyzing results", "progress": 0.9}
        )

        results = comparison.run()

        # Generate insights
        insights = comparison.generate_insights()

        return {
            "status": "completed",
            "results": results,
            "insights": insights,
            "completed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"Comparison error: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__
        }


def publish_simulation_update(
    simulation_id: str,
    progress: float,
    metrics: Dict[str, Any],
    current_step: int,
    total_steps: int
) -> None:
    """Publish simulation progress update to Redis for WebSocket broadcasting

    Args:
        simulation_id: UUID of the simulation
        progress: Progress value (0.0 to 1.0)
        metrics: Current simulation metrics
        current_step: Current step number
        total_steps: Total number of steps
    """
    try:
        import redis
        import json

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)

        # Publish to Redis channel
        channel = f"simulation:{simulation_id}:progress"
        message = json.dumps({
            "type": "progress",
            "simulation_id": simulation_id,
            "progress": progress,
            "current_step": current_step,
            "total_steps": total_steps,
            "current_metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })

        r.publish(channel, message)

    except Exception as e:
        # Don't fail the task if Redis pub/sub fails
        print(f"Warning: Could not publish update to Redis: {e}")
