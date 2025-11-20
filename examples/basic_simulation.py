"""
Basic SDLC Simulation Example

This script demonstrates how to create and run a simple SDLC simulation
with a small team of developers.
"""

import sys
from pathlib import Path

# Add src to path so we can import simulation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.engine import SDLCSimulation
from src.simulation.agents.developer import Developer, DeveloperConfig
from src.simulation.models.types import ExperienceLevel


def create_team() -> list[Developer]:
    """
    Create a diverse team of developers.

    Returns:
        List of Developer agents
    """
    team = []

    # Principal Engineer - Tech lead
    team.append(Developer(
        config=DeveloperConfig(
            name="Alice",
            experience_level=ExperienceLevel.PRINCIPAL,
            productivity_rate=4.5,
            code_quality=0.95,
            review_capacity=7.0,
            onboarding_time=4,  # Onboards faster
            availability=0.65,  # More meetings
            meeting_hours_per_week=8.0,
        )
    ))

    # Senior Engineers - 2x
    for i, name in enumerate(["Bob", "Carol"]):
        team.append(Developer(
            config=DeveloperConfig(
                name=name,
                experience_level=ExperienceLevel.SENIOR,
                productivity_rate=4.0,
                code_quality=0.88,
                review_capacity=6.0,
                onboarding_time=6,
                availability=0.70,
                meeting_hours_per_week=6.0,
            )
        ))

    # Mid-level Engineers - 3x
    for i, name in enumerate(["David", "Eve", "Frank"]):
        team.append(Developer(
            config=DeveloperConfig(
                name=name,
                experience_level=ExperienceLevel.MID,
                productivity_rate=3.5,
                code_quality=0.85,
                review_capacity=5.0,
                onboarding_time=10,
                availability=0.75,
                meeting_hours_per_week=5.0,
            )
        ))

    # Junior Engineer - Learning
    team.append(Developer(
        config=DeveloperConfig(
            name="Grace",
            experience_level=ExperienceLevel.JUNIOR,
            productivity_rate=2.0,
            code_quality=0.75,
            review_capacity=3.0,
            onboarding_time=16,
            availability=0.70,
            meeting_hours_per_week=5.0,
        )
    ))

    return team


def run_basic_simulation():
    """Run a basic 12-week simulation."""
    print("\n" + "="*80)
    print("SDLC SimLab - Basic Team Simulation")
    print("="*80)

    # Create simulation
    sim = SDLCSimulation(
        name="Small Team Simulation",
        timestep_days=1,
        random_seed=42,  # For reproducibility
        communication_loss_factor=0.3,  # 30% information loss (typical in-person)
    )

    # Add team
    print("\nBuilding team...")
    team = create_team()
    for developer in team:
        sim.add_developer(developer)
        print(f"  Added: {developer.config.name} ({developer.config.experience_level.value})")

    print(f"\nTeam size: {len(team)} developers")
    print(f"Communication overhead: {sim.calculate_communication_overhead(len(team)):.2f}x")

    # Run simulation for 12 weeks (84 days)
    num_weeks = 12
    num_days = num_weeks * 7

    print(f"\nRunning simulation for {num_weeks} weeks ({num_days} days)...")
    print("This may take a moment...\n")

    # Print weekly summaries
    for week in range(num_weeks):
        # Run one week
        sim.run(7)

        # Print summary every 4 weeks
        if (week + 1) % 4 == 0:
            print(f"\n--- Week {week + 1} Summary ---")
            metrics = sim.get_metrics()
            print(f"  PRs Created: {metrics['total_prs_created']}")
            print(f"  PRs Merged: {metrics['total_prs_merged']}")
            print(f"  PRs Reverted: {metrics['total_prs_reverted']}")
            print(f"  Open PRs: {metrics['open_prs']}")
            print(f"  Avg Cycle Time: {metrics['avg_cycle_time_days']} days")
            print(f"  Change Failure Rate: {metrics['change_failure_rate']:.1%}")
            print(f"  Throughput: {metrics['prs_per_week']:.1f} PRs/week")

    # Final summary
    sim.print_summary()

    # Developer statistics
    print("\nDeveloper Statistics:")
    print(f"{'Name':<12} {'Level':<10} {'Weeks':<6} {'Onboarded':<10} {'PRs':<6} {'Merged':<8} {'Reverted':<8} {'Reviews':<8}")
    print("-" * 80)

    for dev in team:
        stats = dev.get_stats()
        onboarded = "✓" if stats['is_fully_onboarded'] else f"{stats['productivity_multiplier']:.0%}"
        print(
            f"{stats['name'] or 'Unknown':<12} "
            f"{stats['experience_level']:<10} "
            f"{stats['weeks_in_role']:<6} "
            f"{onboarded:<10} "
            f"{stats['total_prs_created']:<6} "
            f"{stats['total_prs_merged']:<8} "
            f"{stats['total_prs_reverted']:<8} "
            f"{stats['total_reviews_completed']:<8}"
        )

    print("\n" + "="*80)
    print("Simulation complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_basic_simulation()
