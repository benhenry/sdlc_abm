# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Product Overview

**SDLC SimLab** is an agent-based modeling platform that simulates software development team dynamics to forecast organizational change outcomes. It represents developers as autonomous agents with configurable communication patterns and success rates, enabling data-driven insights into throughput, quality, and business impacts.

### Core Problem Solved

Organizations struggle with:
- **Scaling Uncertainty**: Adding developers doesn't produce linear output gains due to communication overhead
- **Change Impact Blind Spots**: Scope/schedule shifts create unpredictable ripple effects
- **Resource Allocation**: Limited ability to model tradeoffs between team size, timeline, and quality
- **Risk Assessment**: No quantitative method to evaluate organizational change risks preemptively

### Primary Users

1. **VP/Director of Engineering**: Strategic decisions about team structure, hiring, priorities (50-200+ engineers)
2. **Engineering Manager**: Team composition and sprint planning (8-30 engineers)
3. **Technical Program Manager**: Cross-team coordination, timeline and resource planning

## Tech Stack

### Frontend
- **Framework**: React
- **Visualizations**: D3.js or Plotly
- **Real-time Updates**: WebSockets
- **Responsive Design**: Mobile view-only support

### Backend & Simulation Engine
- **Simulation Core**: Python (Mesa framework or custom ABM)
- **API**: FastAPI or Django (RESTful)
- **Job Queue**: Celery + Redis for long-running simulations
- **Distributed Compute**: Optional GPU acceleration for large-scale Monte Carlo

### Data Layer
- **Primary Database**: PostgreSQL (relational data)
- **Time-series Data**: InfluxDB or TimescaleDB (simulation results)
- **Caching**: Redis (job queue and caching)
- **Object Storage**: S3 or Google Cloud Storage (reports)

### Integrations
- **P0**: GitHub API, GitLab API
- **P1**: Jira, Linear, Slack
- **P2**: Azure DevOps, Bitbucket, Asana

### Infrastructure
- **Hosting**: GCP
- **Containerization**: Docker (learning opportunity)
- **Orchestration**: Kubernetes (learning/over-engineering opportunity)

## Project Structure

```
sdlc_abm/
├── src/
│   ├── simulation/       # Core ABM simulation engine
│   │   ├── agents/       # Developer agent models
│   │   ├── models/       # Team and org models
│   │   ├── metrics/      # Metric calculation logic
│   │   └── engine.py     # Main simulation loop
│   ├── api/              # Backend API (FastAPI/Django)
│   │   ├── routes/       # API endpoints
│   │   ├── schemas/      # Request/response schemas
│   │   └── integrations/ # GitHub, GitLab, etc.
│   ├── frontend/         # React application
│   │   ├── components/   # UI components
│   │   ├── views/        # Main screens (dashboard, scenario builder, results)
│   │   └── utils/        # Visualization helpers
│   └── optimization/     # Optimization engine
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── simulation/       # Simulation validation tests
├── docs/                 # Documentation
└── data/                 # Sample datasets, templates
```

## Core Agent Model

### Developer Agent Attributes

Each agent has configurable attributes:

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| Experience Level | Enum | Junior, Mid, Senior, Staff, Principal | Mid |
| Productivity Rate | Float | PRs per week baseline | 3.5 |
| Code Quality | Float (0-1) | PR success rate | 0.85 |
| Review Capacity | Float | PRs reviewed per week | 5.0 |
| Onboarding Time | Integer | Weeks to full productivity | 10 |
| Communication Bandwidth | Float | Effective 1:1 connections | 7.0 |
| Specialization | List[String] | Technical domains | [] |
| Availability | Float (0-1) | % time available | 0.70 |

### Communication Model

**Communication Loss Factor** (0-1): Information degradation parameter
- 0 = Perfect communication
- 0.3 = Typical in-person team
- 0.5 = Distributed with good practices
- 0.7 = Distributed with poor practices

**Communication Overhead Scaling**:
- Linear: O(n)
- Quadratic: O(n²) - default
- Hierarchical: O(log n) - well-structured orgs

### Agent Interactions

Daily simulation loop includes:
- **Code Creation**: PR generation based on productivity rate
- **Code Review**: Based on review capacity
- **Communication**: Team size and loss factor affect requirements clarity
- **Meetings**: Based on team configuration
- **Incidents**: Randomized, quality-dependent

**PR Success Model**: Probability-based on:
- Agent code quality attribute
- Communication effectiveness with reviewers
- Work complexity
- Team codebase experience

Failed PRs → reverts, rework, or delays

## Simulation Engine Design

### Time-based Simulation
- **Time Step**: Configurable (default: 1 day)
- **Duration**: 1 week to 2 years
- **Warm-up Period**: Excluded from results
- **Monte Carlo Support**: 100-10,000 runs for confidence intervals

### Key Concepts

**Lossy Communication Impact**:
- Requirements clarity degrades
- Increases rework probability
- Increases coordination delays
- Affects design decision quality

**Dependencies**:
- Blocking dependencies between PRs
- Cross-team dependencies (higher communication loss)
- Technical debt accumulation (increases failure rate)

### Calibration & Validation
- Import historical data (GitHub, GitLab, CSV)
- Run simulation of past period
- Compare predicted vs actual outcomes
- Adjust parameters to minimize error
- Track prediction accuracy over time (target: within 15% of actuals)

## Key Metrics

### Input Metrics (Historical Data)
- Pull requests per week (team and individual)
- PR cycle time (creation to merge)
- Revert rate (% reverted PRs)
- Review cycle time
- Bug discovery rate
- Deployment frequency
- Lead time for changes
- Mean time to recovery (MTTR)

### Derived Metrics (Calculated)
- Velocity (story points or PRs per sprint)
- Quality index (reverts, bugs, MTTR)
- Collaboration index (review patterns)
- Throughput (features per time unit)
- WIP limits effectiveness
- Communication overhead %
- Resource utilization %

### Output Metrics (Simulation Results)
- Total features/PRs delivered
- Average cycle time
- Quality score (composite)
- Projected completion date
- Risk level (variance in outcomes)
- User impact (cumulative end-user value)

## Development Phases

### Phase 1: Foundation (Months 1-3)
- Core simulation engine
- Basic agent model
- Simple UI for configuration
- CSV data import
- Single scenario simulation

### Phase 2: Enhancements (Months 4-6)
- GitHub/GitLab integration
- Comparison mode (multiple scenarios)
- Enhanced visualizations
- Calibration tools
- Alpha release

### Phase 3: Optimization (Months 7-9)
- Optimization engine (genetic algorithm or Bayesian)
- Multi-objective support
- Advanced analytics
- Report generation
- Beta release

### Phase 4: Scale & Polish (Months 10-12)
- Performance optimization
- Additional integrations (Jira, Linear)
- Enterprise features (SSO, RBAC)
- Documentation and training
- V1.0 release

## Development Commands

**Note**: Commands will be added as implementation progresses.

### Python Backend
```bash
# Virtual environment setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/                           # All tests
pytest tests/unit/                      # Unit tests only
pytest tests/simulation/                # Simulation tests
pytest tests/test_file.py::test_name    # Specific test

# Run simulation engine (standalone)
python -m src.simulation.engine --config config.json

# Start API server
uvicorn src.api.main:app --reload      # If using FastAPI
python manage.py runserver             # If using Django

# Linting & formatting
ruff check src/                        # Linting
ruff format src/                       # Formatting
```

### React Frontend
```bash
cd src/frontend

# Install dependencies
npm install

# Development
npm run dev                # Start dev server
npm run build             # Production build
npm test                  # Run tests
npm run lint              # Lint code
```

### Docker & Kubernetes
```bash
# Build images
docker build -t sdlc-simlab-api -f Dockerfile.api .
docker build -t sdlc-simlab-frontend -f Dockerfile.frontend .

# Run locally
docker-compose up

# Kubernetes deployment
kubectl apply -f k8s/
kubectl get pods
kubectl logs <pod-name>
```

## Architecture Principles

### Separation of Concerns

Maintain clear boundaries between:

1. **Simulation Engine** (`src/simulation/`)
   - Pure Python, no API/web dependencies
   - Agent behavior models
   - Metric calculations
   - Simulation loop and state management
   - Should be runnable standalone via CLI

2. **API Layer** (`src/api/`)
   - RESTful endpoints for simulation control
   - Job queue management (Celery)
   - Integration with external APIs (GitHub, GitLab)
   - Authentication and authorization
   - Data persistence

3. **Frontend** (`src/frontend/`)
   - React components for scenario configuration
   - Visualization components (D3.js/Plotly)
   - Real-time simulation progress (WebSockets)
   - Export functionality

4. **Optimization Engine** (`src/optimization/`)
   - Multi-objective optimization
   - Parameter space exploration
   - Recommendation generation
   - Can call simulation engine directly

### Performance Considerations

- **Target**: 50-developer, 26-week simulation in < 5 minutes
- **Monte Carlo**: 1000-run simulation in < 10 minutes
- **UI Responsiveness**: < 200ms for interactions
- **Scalability**: Support orgs up to 500 developers, simulations up to 2 years

**Optimization Strategies**:
- Vectorized operations where possible (NumPy)
- Caching of intermediate results
- Distributed computation for Monte Carlo (Celery workers)
- Optional GPU acceleration for large-scale runs

### Security & Compliance

- **SOC 2 Type II** compliance required
- Data encryption at rest and in transit
- Role-based access control (RBAC)
- Audit logging of all changes
- **No PII storage** - agents are anonymous
- SSO support (SAML, OAuth)

## Testing Strategy

### Unit Tests
- Agent behavior verification
- Metric calculation accuracy
- Communication model correctness
- API endpoint validation

### Integration Tests
- GitHub/GitLab API integration
- End-to-end scenario runs
- Database operations
- Job queue functionality

### Simulation Validation Tests
- Historical data calibration
- Prediction accuracy (target: within 15% of actuals)
- Edge case handling (0 developers, 1000 developers)
- Sensitivity analysis

### Performance Tests
- Simulation execution time benchmarks
- API response time under load
- Concurrent user simulation

## Key User Flows

### 1. Scenario Builder Wizard
1. Import historical data (GitHub/GitLab or CSV)
2. Configure team structure (agent count, experience distribution)
3. Set communication parameters (loss factor, overhead model)
4. Define scope and timeline
5. Run simulation (single or Monte Carlo)
6. View results and comparisons

### 2. Optimization Flow
1. Define objective function (user impact, velocity, quality)
2. Set constraints (budget, timeline, quality thresholds)
3. Run optimization (explore parameter space)
4. Review top 5 configurations with tradeoffs
5. Select and simulate chosen configuration

### 3. Calibration Flow
1. Import historical metrics
2. Configure simulation to match historical period
3. Run simulation
4. Compare predicted vs actual outcomes
5. Adjust parameters iteratively
6. Save calibrated baseline model

## Development Philosophy

This is a **learning project** for the developer (Henry) with goals to gain hands-on experience in:
- React development
- Systems design and architecture
- Agent-Based Modeling techniques
- Docker and Kubernetes orchestration
- Working with Claude Code for development

**Key Principles**:
- Some aspects may be intentionally over-engineered for learning
- Balance practical delivery with learning objectives
- Prioritize code clarity and documentation for educational value
- Experiment with different architectural patterns

## Critical Non-Goals

These are **explicitly out of scope** - do not implement:
- Individual developer performance management
- Real-time project tracking or monitoring
- Source code analysis or technical debt assessment
- Automated decision-making without human oversight
- Team morale or culture measurement
- Using the tool for performance reviews (ethical concern)

## References & Research

- "The Mythical Man-Month" by Fred Brooks
- Mesa framework for agent-based modeling in Python
- DORA (DevOps Research and Assessment) metrics
- "Accelerate: The Science of Lean Software and DevOps"
- NetLogo (agent-based modeling reference)

## Success Metrics

### V1.0 Release Criteria
- All P0 and 80% of P1 features complete
- Model accuracy within 15% of actuals
- 100+ active users
- 99% uptime for 30 days
- Customer satisfaction score > 4/5

### Long-term Success (12 months)
- 500+ organizations using tool
- Demonstrable ROI (reduced planning risk)
- 85% retention rate
- Model accuracy within 10% of actuals
