"""
Diminishing Returns Analysis for AI Agents

This tool runs multiple simulations with varying numbers of AI agents
to identify the optimal human/AI ratio based on different optimization criteria:
- Throughput per dollar
- Absolute throughput
- Quality-adjusted throughput
- Human review burden

Use this to answer questions like:
- When do additional AI agents stop delivering value?
- What's the optimal AI/human ratio for our workload?
- Where's the inflection point for human review capacity?
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation.engine import SDLCSimulation
from src.simulation.agents.developer import Developer, DeveloperConfig
from src.simulation.agents.ai_agent import AIAgent, AIAgentConfig
from src.simulation.models.types import ExperienceLevel, AIModelType


def run_simulation_with_config(
    human_count: int,
    ai_count: int,
    ai_model: AIModelType,
    weeks: int = 12,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Run a simulation with specific team configuration.

    Args:
        human_count: Number of human developers
        ai_count: Number of AI agents
        ai_model: AI model type to use
        weeks: Simulation duration
        random_seed: Random seed for reproducibility

    Returns:
        Dictionary with simulation results
    """
    sim = SDLCSimulation(
        name=f"{human_count}H+{ai_count}AI",
        random_seed=random_seed,
        communication_loss_factor=0.3
    )

    # Add humans with realistic distribution
    experience_dist = {
        ExperienceLevel.SENIOR: max(1, human_count // 4),
        ExperienceLevel.MID: max(1, human_count // 2),
        ExperienceLevel.JUNIOR: max(0, human_count - (human_count // 4) - (human_count // 2))
    }

    for level, count in experience_dist.items():
        for i in range(count):
            sim.add_developer(Developer(config=DeveloperConfig(
                name=f"{level.value}-{i+1}",
                experience_level=level
            )))

    # Add AI agents
    for i in range(ai_count):
        sim.add_ai_agent(AIAgent(config=AIAgentConfig(
            name=f"AI-{ai_model.value}-{i+1}",
            model_type=ai_model
        )))

    # Run simulation
    sim.run(weeks * 7)

    # Get metrics
    metrics = sim.get_metrics()

    # Calculate derived metrics
    total_cost = metrics['ai_total_cost']
    throughput = metrics['prs_per_week']
    quality_score = 1.0 - metrics['change_failure_rate']
    quality_adjusted_throughput = throughput * quality_score

    # Cost efficiency (throughput per dollar spent)
    cost_efficiency = throughput / max(0.01, total_cost) if total_cost > 0 else throughput

    # Human review burden (AI PRs / Human developers)
    review_burden = metrics['ai_prs_per_week'] / max(1, metrics['human_developers'])

    return {
        'human_count': human_count,
        'ai_count': ai_count,
        'ai_model': ai_model.value,
        'total_team': human_count + ai_count,
        'throughput': throughput,
        'quality_adjusted_throughput': quality_adjusted_throughput,
        'change_failure_rate': metrics['change_failure_rate'],
        'total_cost': total_cost,
        'cost_per_week': total_cost / weeks,
        'cost_efficiency': cost_efficiency,
        'review_burden': review_burden,
        'open_prs': metrics['open_prs'],
        'human_prs_per_week': metrics['human_prs_per_week'],
        'ai_prs_per_week': metrics['ai_prs_per_week'],
    }


def analyze_diminishing_returns(
    human_count: int,
    ai_range: List[int],
    ai_model: AIModelType = AIModelType.CLAUDE_SONNET,
    weeks: int = 12
) -> List[Dict[str, Any]]:
    """
    Analyze diminishing returns across a range of AI agent counts.

    Args:
        human_count: Fixed number of human developers
        ai_range: List of AI agent counts to test
        ai_model: AI model type
        weeks: Simulation duration

    Returns:
        List of results for each configuration
    """
    print(f"\n{'='*80}")
    print(f"DIMINISHING RETURNS ANALYSIS")
    print(f"{'='*80}")
    print(f"Fixed team: {human_count} humans")
    print(f"Variable AI: {min(ai_range)} to {max(ai_range)} agents ({ai_model.value})")
    print(f"Duration: {weeks} weeks per simulation")
    print(f"{'='*80}\n")

    results = []

    for ai_count in ai_range:
        print(f"Running: {human_count} humans + {ai_count} AI agents... ", end='', flush=True)
        result = run_simulation_with_config(human_count, ai_count, ai_model, weeks)
        results.append(result)
        print(f"Done ({result['throughput']:.1f} PRs/week, ${result['total_cost']:.2f})")

    return results


def print_analysis(results: List[Dict[str, Any]]):
    """Print analysis results with recommendations."""
    print(f"\n{'='*80}")
    print("RESULTS TABLE")
    print(f"{'='*80}")
    print(f"{'AI':<4} {'Total':<6} {'PR/Wk':<8} {'Quality':<8} {'Cost/Wk':<10} {'Eff':<10} {'Burden':<8} {'Open':<6}")
    print(f"{'Cnt':<4} {'Team':<6} {'':<8} {'Adj':<8} {'':<10} {'(PR/$)':<10} {'(PR/H)':<8} {'PRs':<6}")
    print("-" * 80)

    for r in results:
        print(
            f"{r['ai_count']:<4} "
            f"{r['total_team']:<6} "
            f"{r['throughput']:<8.1f} "
            f"{r['quality_adjusted_throughput']:<8.1f} "
            f"${r['cost_per_week']:<9.2f} "
            f"{r['cost_efficiency']:<10.1f} "
            f"{r['review_burden']:<8.1f} "
            f"{r['open_prs']:<6}"
        )

    print(f"{'='*80}\n")

    # Calculate insights
    print("KEY INSIGHTS")
    print("-" * 80)

    # Find optimal configurations
    best_throughput = max(results, key=lambda x: x['throughput'])
    best_efficiency = max(results, key=lambda x: x['cost_efficiency'])
    best_quality = max(results, key=lambda x: x['quality_adjusted_throughput'])

    print(f"\n1. Maximum Throughput:")
    print(f"   {best_throughput['ai_count']} AI agents → {best_throughput['throughput']:.1f} PRs/week")
    print(f"   Cost: ${best_throughput['cost_per_week']:.2f}/week")

    print(f"\n2. Best Cost Efficiency:")
    print(f"   {best_efficiency['ai_count']} AI agents → {best_efficiency['cost_efficiency']:.1f} PRs per $")
    print(f"   Throughput: {best_efficiency['throughput']:.1f} PRs/week at ${best_efficiency['cost_per_week']:.2f}/week")

    print(f"\n3. Best Quality-Adjusted Throughput:")
    print(f"   {best_quality['ai_count']} AI agents → {best_quality['quality_adjusted_throughput']:.1f} quality PRs/week")
    print(f"   Failure rate: {best_quality['change_failure_rate']:.1%}")

    # Detect diminishing returns
    print(f"\n4. Diminishing Returns Analysis:")
    marginal_returns = []
    for i in range(1, len(results)):
        prev = results[i-1]
        curr = results[i]
        marginal_throughput = curr['throughput'] - prev['throughput']
        marginal_cost = curr['cost_per_week'] - prev['cost_per_week']
        marginal_returns.append({
            'ai_added': curr['ai_count'] - prev['ai_count'],
            'throughput_gain': marginal_throughput,
            'cost_increase': marginal_cost,
            'marginal_efficiency': marginal_throughput / max(0.01, marginal_cost) if marginal_cost > 0 else marginal_throughput
        })

    for i, mr in enumerate(marginal_returns):
        ai_from = results[i]['ai_count']
        ai_to = results[i+1]['ai_count']
        print(f"   {ai_from} → {ai_to} AI: +{mr['throughput_gain']:.1f} PRs/week for +${mr['cost_increase']:.2f}/week "
              f"(efficiency: {mr['marginal_efficiency']:.1f} PRs/$)")

    # Find inflection point (where marginal efficiency drops significantly)
    if len(marginal_returns) > 1:
        efficiencies = [mr['marginal_efficiency'] for mr in marginal_returns]
        for i in range(1, len(efficiencies)):
            if efficiencies[i] < efficiencies[i-1] * 0.5:  # 50% drop
                print(f"\n   ⚠️  Inflection point detected after {results[i]['ai_count']} AI agents")
                print(f"      Marginal efficiency dropped significantly")
                break

    # Review burden warning
    high_burden = [r for r in results if r['review_burden'] > 15]  # 15 AI PRs per human per week
    if high_burden:
        print(f"\n5. Human Review Bottleneck Warning:")
        print(f"   With {high_burden[0]['ai_count']}+ AI agents, review burden exceeds 15 PRs/human/week")
        print(f"   Consider adding more human reviewers or reducing AI agent count")
        print(f"   Open PRs at {high_burden[-1]['ai_count']} AI: {high_burden[-1]['open_prs']}")

    print(f"\n{'='*80}\n")


def main():
    """Run diminishing returns analysis with default parameters."""
    # Configuration
    HUMAN_COUNT = 5
    AI_RANGE = [0, 2, 4, 6, 8, 10, 12, 15, 20]
    AI_MODEL = AIModelType.CLAUDE_SONNET
    WEEKS = 12

    # Run analysis
    results = analyze_diminishing_returns(
        human_count=HUMAN_COUNT,
        ai_range=AI_RANGE,
        ai_model=AI_MODEL,
        weeks=WEEKS
    )

    # Print results
    print_analysis(results)

    # Optional: Save to JSON
    output_file = "diminishing_returns_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_file}\n")


if __name__ == "__main__":
    main()
