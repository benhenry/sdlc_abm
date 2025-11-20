# Architecture Overview

This document provides a high-level overview of the SDLC SimLab architecture.

## System Components

### 1. Simulation Engine (`src/simulation/`)

The core of SDLC SimLab is a Python-based agent-based model (ABM) that simulates software development team dynamics.

#### Key Concepts

- **Agents** (`agents/`): Individual developers with configurable attributes (experience, productivity, quality, etc.)
- **Models** (`models/`): Team structures, organizational hierarchies, and communication patterns
- **Metrics** (`metrics/`): Calculation of DORA metrics, velocity, quality indices, etc.
- **Engine** (`engine.py`): Main simulation loop that advances time and orchestrates agent interactions

#### Simulation Loop

Each time step (default: 1 day):
1. Agents create PRs based on productivity rates
2. Agents review PRs based on review capacity
3. Communication occurs (with configurable loss factor)
4. Meetings consume time based on team configuration
5. Incidents occur randomly based on quality parameters
6. Metrics are calculated and recorded

### 2. API Layer (`src/api/`)

RESTful API built with FastAPI that provides:

- **Scenario Management**: CRUD operations for simulation configurations
- **Simulation Execution**: Start, pause, cancel simulations
- **Results Retrieval**: Query simulation outcomes and metrics
- **Integrations**: Connect to GitHub, GitLab, Jira, etc.
- **Authentication**: User management and authorization

### 3. Frontend (`src/frontend/`)

React-based web application providing:

- **Scenario Builder**: Wizard-based UI for configuring simulations
- **Dashboard**: Overview of recent simulations and quick actions
- **Results Viewer**: Interactive visualizations (D3.js/Plotly)
- **Comparison Mode**: Side-by-side scenario analysis
- **Optimization Studio**: Multi-objective optimization interface

### 4. Optimization Engine (`src/optimization/`)

Explores parameter space to find optimal configurations:

- **Objective Functions**: User impact, velocity, quality, efficiency
- **Constraints**: Budget, timeline, quality thresholds
- **Algorithms**: Genetic algorithms or Bayesian optimization
- **Recommendations**: Top configurations with tradeoff analysis

### 5. Data Layer

- **PostgreSQL**: Primary database for users, scenarios, configurations
- **InfluxDB/TimescaleDB**: Time-series simulation results
- **Redis**: Caching and Celery task queue
- **S3/GCS**: Report storage (PDFs, exports)

### 6. Integration Layer (`src/api/integrations/`)

Connects to external services:

- **GitHub/GitLab**: Import historical PR data, cycle times, revert rates
- **Jira/Linear**: Import story points, velocity, cycle times
- **Webhooks**: Real-time data sync (future)

## Data Flow

### Typical Simulation Flow

```
User (Frontend) → API → Celery Task Queue → Simulation Engine
                                                    ↓
                                          Simulation Results
                                                    ↓
                                          TimescaleDB/InfluxDB
                                                    ↓
Frontend (Visualizations) ← API ← Query Results
```

### Historical Data Import Flow

```
GitHub/GitLab API → Integration Layer → Data Normalization → PostgreSQL
                                                                   ↓
                                                    Used for Calibration
                                                                   ↓
                                                         Simulation Engine
```

## Communication Patterns

### Real-time Updates

- **WebSockets**: Stream simulation progress to frontend
- **Server-Sent Events**: Alternative for one-way updates

### Background Processing

- **Celery Workers**: Execute long-running simulations asynchronously
- **Redis**: Message broker and result backend

## Scalability Considerations

### Horizontal Scaling

- **API Servers**: Stateless, can run multiple instances behind load balancer
- **Celery Workers**: Add workers to handle more concurrent simulations
- **Database**: Read replicas for query-heavy workloads

### Performance Optimization

- **Vectorization**: Use NumPy for batch operations
- **Caching**: Redis for frequently accessed scenarios and results
- **GPU Acceleration**: Optional for large-scale Monte Carlo simulations
- **Result Sampling**: Store sampled time points instead of every timestep

## Security Architecture

### Authentication & Authorization

- **SSO Integration**: SAML, OAuth (Google, Microsoft, etc.)
- **RBAC**: Role-based access control (Admin, Manager, Viewer)
- **API Keys**: For programmatic access

### Data Protection

- **Encryption at Rest**: Database and object storage encryption
- **Encryption in Transit**: TLS for all API communication
- **No PII**: Agents are anonymous, no individual developer tracking
- **Audit Logs**: All changes tracked with user attribution

## Deployment Architecture

### Development

```
Local Machine
├── Python API (uvicorn --reload)
├── React Dev Server (npm run dev)
├── PostgreSQL (Docker or local)
├── Redis (Docker or local)
└── Celery Worker (local process)
```

### Production (GCP)

```
Cloud Load Balancer
    ↓
Kubernetes Cluster
├── API Pods (FastAPI)
├── Frontend Pods (Nginx serving React build)
├── Celery Worker Pods
├── Redis (Cloud Memorystore)
├── PostgreSQL (Cloud SQL)
└── TimescaleDB (Compute Engine or managed)
```

## Development Workflow

1. **Feature Development**: Work in feature branches
2. **Testing**: Unit, integration, simulation validation tests
3. **PR Review**: Code review and automated checks
4. **Merge to Main**: Continuous deployment to staging
5. **Production Release**: Tagged releases deployed to production

## Technology Decisions

### Why FastAPI?

- Modern, fast, automatic OpenAPI documentation
- Native async support for I/O-bound operations
- Excellent type hints and validation with Pydantic

### Why Mesa (or Custom ABM)?

- Mesa: Established ABM framework with good documentation
- Custom: More control, better performance for specific use case
- Decision pending based on early prototyping

### Why React?

- Large ecosystem and component libraries
- Strong visualization libraries (D3.js integration)
- Developer familiarity and learning goals

### Why PostgreSQL + TimescaleDB?

- PostgreSQL: Robust, feature-rich relational database
- TimescaleDB: Optimized for time-series simulation results
- Good compromise between complexity and performance

## Future Considerations

### Multi-tenancy

- Organization-level data isolation
- Shared infrastructure, separate data
- Tenant-aware queries and indexing

### Real-time Recommendations

- Stream actual metrics from integrations
- Compare against predictions
- Alert on significant deviations

### Machine Learning Integration

- Learn from historical prediction accuracy
- Auto-tune simulation parameters
- Anomaly detection in team dynamics

## References

See CLAUDE.md for complete list of research references and technical documentation.
