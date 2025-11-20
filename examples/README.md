# SDLC SimLab Examples

This directory contains example scripts demonstrating how to use the SDLC SimLab simulation engine.

## Running Examples

Make sure you've set up your Python environment first:

```bash
# From the project root
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Then run any example:

```bash
# From the project root
python examples/basic_simulation.py
```

## Available Examples

### `basic_simulation.py`

A simple 12-week simulation of a 7-person engineering team with mixed experience levels.

**Features demonstrated:**
- Creating a diverse team (Junior to Principal engineers)
- Configuring developer attributes (productivity, quality, availability)
- Running a multi-week simulation
- Collecting and displaying metrics
- Understanding onboarding progression

**What to observe:**
- How Junior developers improve over time as they onboard
- The relationship between code quality and revert rates
- Communication overhead with team size
- PR throughput and cycle times
- Individual developer statistics

**Example output:**
```
SDLC SimLab - Basic Team Simulation
================================================================================

Building team...
  Added: Alice (principal)
  Added: Bob (senior)
  Added: Carol (senior)
  Added: David (mid)
  Added: Eve (mid)
  Added: Frank (mid)
  Added: Grace (junior)

Team size: 7 developers
Communication overhead: 1.21x

Running simulation for 12 weeks (84 days)...
```

## Understanding the Output

### Metrics Explained

- **PRs Created**: Total pull requests created by all developers
- **PRs Merged**: Successfully merged pull requests
- **PRs Reverted**: Merged PRs that were later reverted due to quality issues
- **Open PRs**: PRs currently awaiting review or merge
- **Avg Cycle Time**: Average time from PR creation to merge (in days)
- **Change Failure Rate**: Percentage of merged PRs that were reverted
- **Throughput**: Average PRs merged per week

### Developer Statistics

- **Weeks**: How many weeks the developer has been in the simulation
- **Onboarded**: Whether developer has reached full productivity
  - `✓` = Fully onboarded
  - Percentage = Current productivity level (during ramp-up)
- **PRs**: Total PRs created by this developer
- **Merged**: PRs successfully merged
- **Reverted**: PRs that were merged but later reverted
- **Reviews**: Number of code reviews completed

## Modifying Examples

### Experiment with Team Composition

Try different team configurations:

```python
# All senior developers
team = [
    Developer(config=DeveloperConfig(
        experience_level=ExperienceLevel.SENIOR,
        code_quality=0.90
    ))
    for _ in range(5)
]

# vs. Mixed team with junior developers
team = [
    Developer(config=DeveloperConfig(
        experience_level=ExperienceLevel.SENIOR,
        code_quality=0.90
    ))
    for _ in range(2)
] + [
    Developer(config=DeveloperConfig(
        experience_level=ExperienceLevel.JUNIOR,
        code_quality=0.70
    ))
    for _ in range(5)
]
```

### Adjust Communication Loss

Compare different communication patterns:

```python
# Perfect communication (co-located, excellent practices)
sim = SDLCSimulation(communication_loss_factor=0.0)

# Typical in-person team
sim = SDLCSimulation(communication_loss_factor=0.3)

# Distributed team with poor practices
sim = SDLCSimulation(communication_loss_factor=0.7)
```

### Change Simulation Duration

```python
# Run for 6 months (26 weeks)
sim.run(26 * 7)

# Run for 1 year (52 weeks)
sim.run(52 * 7)
```

### Modify Developer Attributes

Experiment with different productivity and quality settings:

```python
# High productivity, lower quality (move fast, break things)
config = DeveloperConfig(
    productivity_rate=5.0,  # High output
    code_quality=0.75,       # More bugs
)

# Lower productivity, higher quality (move slow, ship stable)
config = DeveloperConfig(
    productivity_rate=2.5,  # Careful work
    code_quality=0.95,       # Very few bugs
)
```

## Ideas for New Examples

Feel free to create your own examples! Some ideas:

1. **Team Growth**: Simulate adding developers mid-project
2. **Team Split**: Start with a large team, split into smaller teams
3. **Quality vs Speed**: Compare different quality/productivity tradeoffs
4. **Onboarding Impact**: Add many junior devs at once vs. gradual hiring
5. **Meeting Overhead**: Experiment with different meeting loads
6. **Communication Models**: Compare linear, quadratic, and hierarchical overhead

## Troubleshooting

### No PRs Being Created

If you see very few or no PRs being created:
- Check that `productivity_rate` is reasonable (2.0-5.0 range)
- Ensure developers are onboarded (or give them time to onboard)
- Verify `availability` is not too low (0.5-0.8 is typical)

### High Revert Rate

If you see many reverts:
- This is normal for low `code_quality` settings (< 0.80)
- Junior developers will have more reverts during onboarding
- Consider increasing `code_quality` or adding more senior reviewers

### Slow Simulation

For large teams or long durations:
- Progress is printed every 4 weeks
- Be patient with 6+ month simulations
- Consider reducing the number of developers for initial experiments

## Next Steps

After running the basic example:
1. Modify team composition and observe changes
2. Try different communication loss factors
3. Experiment with onboarding times
4. Create your own custom scenarios
5. Compare different team structures side-by-side

Happy simulating! 🚀
