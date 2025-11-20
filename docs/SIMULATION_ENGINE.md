# Simulation Engine Architecture

This document describes the custom Python simulation engine built for SDLC SimLab.

## Design Philosophy

The engine is built from scratch to provide:
- **Full control** over simulation behavior and performance
- **Clean separation** between agents, models, and orchestration
- **Extensibility** for future features (incidents, meetings, technical debt)
- **Testability** with clear interfaces and abstractions
- **Learning value** - understanding ABM from the ground up

## Core Components

### 1. Base Classes (`src/simulation/base.py`)

#### `Agent`
Abstract base class for all simulation agents.

**Key methods:**
- `step(context)`: Execute one timestep
- `on_added_to_simulation(timestep)`: Initialization hook

**Usage:**
```python
class MyAgent(Agent):
    def step(self, context: SimulationContext):
        # Agent behavior here
        pass
```

#### `Simulation`
Core simulation engine that orchestrates time advancement.

**Key methods:**
- `add_agent(agent)`: Add an agent
- `step()`: Advance one timestep
- `run(num_steps)`: Run for N steps
- `log_event()`: Track events
- `reset()`: Reset to initial state

**Usage:**
```python
sim = Simulation(name="My Sim", timestep_days=1)
sim.add_agent(my_agent)
sim.run(100)  # Run for 100 days
```

#### `SimulationContext`
Immutable context passed to agents during each step.

**Contains:**
- `current_day`: Current simulation day
- `current_week`: Current week (day // 7)
- `random_seed`: For reproducibility
- `metadata`: Additional context data

#### `SimulationEvent`
Events logged during simulation for analysis.

**Event types:**
- `agent_added`, `agent_removed`
- `pr_created`, `pr_merged`, `pr_reverted`
- `review_assigned`
- Custom events

### 2. Developer Agent (`src/simulation/agents/developer.py`)

The primary agent representing a software engineer.

#### `DeveloperConfig`
Configuration dataclass with all attributes from the PRD:

```python
@dataclass
class DeveloperConfig:
    name: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.MID
    productivity_rate: float = 3.5        # PRs/week
    code_quality: float = 0.85            # Success rate (0-1)
    review_capacity: float = 5.0          # Reviews/week
    onboarding_time: int = 10             # Weeks to full productivity
    communication_bandwidth: float = 7.0  # Effective connections
    availability: float = 0.70            # % time available
    specializations: List[str] = []
    meeting_hours_per_week: float = 5.0
```

#### `Developer`
Agent implementation with:

**Behaviors:**
- Creates PRs based on productivity rate
- Reviews PRs from other developers
- Ramps up during onboarding
- Tracks personal metrics

**Lifecycle:**
```python
dev = Developer(config=DeveloperConfig(
    name="Alice",
    experience_level=ExperienceLevel.SENIOR,
    productivity_rate=4.0
))
sim.add_developer(dev)
sim.run(84)  # 12 weeks
stats = dev.get_stats()
```

### 3. Work Models (`src/simulation/models/work.py`)

#### `PullRequest`
Represents a unit of work with:
- Author and creation time
- Reviewers and approvals
- State (open, in_review, approved, merged, reverted)
- Success prediction (based on code quality)
- Cycle time tracking

#### `CodeReview`
Represents a review action with:
- PR being reviewed
- Reviewer and time invested
- Completion status and approval

#### `Incident`
Production incidents (for future use):
- Severity levels
- Assignees
- Time to resolve (MTTR)
- Root cause tracking

### 4. SDLC Simulation Engine (`src/simulation/engine.py`)

#### `SDLCSimulation`
Enhanced simulation with SDLC-specific orchestration.

**Features:**
- Team management
- PR workflow (creation → review → merge/revert)
- Communication overhead modeling
- Automatic metrics collection

**Configuration:**
```python
sim = SDLCSimulation(
    name="Team Simulation",
    timestep_days=1,
    random_seed=42,
    communication_loss_factor=0.3,  # 30% information loss
    communication_overhead_model=CommunicationOverheadModel.QUADRATIC
)
```

**PR Workflow:**
1. Developers create PRs (probabilistic, based on productivity)
2. Simulation assigns reviewers
3. Reviewers complete reviews (probabilistic, based on capacity)
4. PRs merge when approved
5. Failed PRs are reverted (based on code quality)

**Communication Models:**
- **Linear O(n)**: Minimal overhead, scales linearly
- **Quadratic O(n²)**: Realistic default (Brooks' Law)
- **Hierarchical O(log n)**: Well-structured organizations

**Metrics:**
```python
metrics = sim.get_metrics()
# Returns:
# - total_developers, total_prs_created, total_prs_merged
# - avg_cycle_time_days, change_failure_rate
# - prs_per_week, communication_overhead
```

## Simulation Loop

Each timestep (default: 1 day):

```
1. Update weekly tracking (if new week)
2. Developers create PRs (probabilistic)
3. Assign reviewers to open PRs
4. Developers work on reviews
5. Merge approved PRs
6. Discover and revert failed PRs
7. Advance timestep
8. Calculate metrics
```

## Key Design Decisions

### Probabilistic Behavior

Rather than deterministic schedules, agents use probabilities:

```python
# Daily PR creation probability
prs_per_day = productivity_rate / 5.0  # 5 working days
if random.random() < prs_per_day:
    create_pr()
```

**Why?** More realistic simulation of variability in developer output.

### Quality as Success Rate

Code quality (0-1) determines PR success probability at creation:

```python
will_succeed = random.random() < code_quality
```

**Why?** Models that some PRs will have issues despite review.

### Onboarding Curve

Developers ramp from 0% to 100% productivity over onboarding_time:

```python
progress = weeks_in_role / onboarding_time
productivity_multiplier = min(1.0, progress)
```

**Why?** Captures the reality that new hires take time to become productive.

### Event-Driven Metrics

Events are logged throughout simulation and analyzed later:

```python
sim.log_event("pr_merged", agent_id=dev.agent_id, data={"pr_id": pr.pr_id})
```

**Why?** Enables flexible post-hoc analysis and debugging.

## Extensibility Points

The engine is designed for easy extension:

### Adding New Agent Types

```python
class ProductManager(Agent):
    def step(self, context: SimulationContext):
        # PM behavior
        pass
```

### Adding New Metrics

```python
def calculate_lead_time(sim: SDLCSimulation) -> float:
    # Analyze events to compute lead time
    pass
```

### Adding New Work Types

```python
@dataclass
class DesignDoc:
    author_id: str
    reviewers: List[str]
    # ...
```

### Custom Event Handlers

```python
class MySimulation(SDLCSimulation):
    def on_pr_merged(self, pr: PullRequest):
        # Custom logic
        super().on_pr_merged(pr)
```

## Testing

Unit tests cover:
- Base simulation mechanics (`tests/unit/test_simulation.py`)
- Developer agent behavior (`tests/unit/test_developer.py`)
- Work models (PRs, reviews)
- Metrics calculation

Run tests:
```bash
pytest tests/unit/ -v
```

## Example Usage

See `examples/basic_simulation.py` for a complete example:

```python
from src.simulation.engine import SDLCSimulation
from src.simulation.agents.developer import Developer, DeveloperConfig
from src.simulation.models.types import ExperienceLevel

# Create simulation
sim = SDLCSimulation(communication_loss_factor=0.3)

# Add developers
sim.add_developer(Developer(config=DeveloperConfig(
    name="Alice",
    experience_level=ExperienceLevel.SENIOR,
    productivity_rate=4.0,
    code_quality=0.90
)))

# Run for 12 weeks
sim.run(12 * 7)

# Get results
sim.print_summary()
```

## Performance Characteristics

Current implementation (single-threaded):
- **Small team (7 devs)**: 12 weeks in ~1 second
- **Medium team (20 devs)**: 26 weeks in ~3 seconds
- **Large team (50 devs)**: 52 weeks in ~15 seconds

Future optimizations:
- Vectorized operations with NumPy
- Parallel Monte Carlo runs
- JIT compilation with Numba
- GPU acceleration for large-scale runs

## Future Enhancements

### Phase 2
- [ ] Team structures and hierarchies
- [ ] Technical debt accumulation
- [ ] Incident response workflow
- [ ] Meeting time simulation
- [ ] Cross-team dependencies

### Phase 3
- [ ] Machine learning for parameter tuning
- [ ] Historical data calibration
- [ ] Sensitivity analysis
- [ ] Optimization algorithms
- [ ] Confidence intervals (Monte Carlo)

## References

- **Brooks' Law**: "Adding people to a late project makes it later" - modeled via quadratic communication overhead
- **DORA Metrics**: Change failure rate, cycle time, throughput
- **Agent-Based Modeling**: Emergent behavior from individual agent interactions

See `CLAUDE.md` and PRD for complete requirements and architecture context.
