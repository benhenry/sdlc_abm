# SDLC SimLab

**Agent-Based Modeling Platform for Software Development Team Dynamics**

SDLC SimLab is an agent-based model (ABM) that simulates software development teams to forecast organizational change outcomes. It models developers as autonomous agents with configurable communication patterns and success rates, enabling data-driven insights into throughput, quality, and business impacts.

## What Problem Does This Solve?

Engineering leaders face critical challenges when making team and project decisions:

- **Scaling Uncertainty**: Will adding 5 developers actually speed up delivery, or slow us down?
- **Change Impact Blind Spots**: What happens if we cut scope by 30%? Accelerate the timeline?
- **Resource Allocation**: How do we balance team size, timeline, and quality?
- **Risk Assessment**: What are the risks of this reorganization?

SDLC SimLab provides a simulation environment to explore these questions before making costly organizational changes.

## Key Features (Planned)

### Phase 1: Foundation (Months 1-3)
- ✅ Project initialization and architecture
- ✅ Core simulation engine with agent-based modeling
- ✅ Human developer agents with onboarding and productivity models
- ✅ AI agent system (GPT-4, Claude Sonnet/Opus, CodeLlama)
- ✅ Single scenario simulation with examples
- ✅ YAML/JSON scenario configuration system
- ✅ CSV data import for historical metrics
- ✅ Technical debt and incident tracking

### Phase 2: Web Application (Months 4-6)
- ✅ FastAPI backend with async SQLAlchemy + PostgreSQL
- ✅ Celery + Redis for background simulation execution
- ✅ RESTful API endpoints (scenarios, simulations, comparisons)
- ✅ WebSocket support for real-time progress updates
- ✅ React frontend with TypeScript + Vite
- ✅ Dashboard and scenario library views
- ✅ Docker Compose development environment
- ⏳ GitHub/GitLab integration for automatic data import
- ⏳ Enhanced visualizations (Charts, metrics dashboard)
- ⏳ Scenario builder wizard
- ⏳ Model calibration tools
- ⏳ Alpha release

### Phase 3: Optimization (Months 7-9)
- ⏳ Multi-objective optimization engine
- ⏳ Advanced analytics and insights
- ⏳ Report generation (PDF, PowerPoint)
- ⏳ Beta release

### Phase 4: Scale & Polish (Months 10-12)
- ⏳ Performance optimization
- ⏳ Additional integrations (Jira, Linear, Slack)
- ⏳ Enterprise features (SSO, RBAC)
- ⏳ V1.0 release

## Tech Stack

- **Simulation Engine**: Python, Mesa (or custom ABM)
- **API**: FastAPI, Celery + Redis
- **Frontend**: React, D3.js/Plotly
- **Database**: PostgreSQL, InfluxDB/TimescaleDB
- **Infrastructure**: Docker, Kubernetes, GCP

## Metrics Tracked

### Primary DX Metrics
- Diffs per Engineer
- Developer Experience Index
- Change failure rate
- Percentage of time spent on new capabilities

### Secondary Metrics
- Lead time, deployment frequency, perceived rate of delivery
- Time to 10th PR, ease of delivery
- Regrettable attrition, failed deployment recovery time
- Perceived software quality
- Operational health and security metrics
- Initiative progress and ROI
- Revenue per engineer, R&D as percentage of revenue

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- OR: Python 3.11+, Node.js 18+, PostgreSQL 15+, Redis 7+

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd sdlc_abm

# Start all services (API, Database, Redis, Celery, Frontend)
docker-compose up -d

# Check logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
# Health Check: http://localhost:8000/health

# Run database migrations
docker-compose exec api alembic upgrade head

# Stop all services
docker-compose down
```

### Local Development without Docker

```bash
# Set up Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start PostgreSQL and Redis (via Docker or locally)
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start API server
uvicorn src.api.main:app --reload

# Start Celery worker (in another terminal)
celery -A src.api.tasks worker --loglevel=info

# Start frontend (in another terminal)
cd src/frontend
npm install
npm run dev
```

### Running the Simulation Engine (CLI)

```bash
# Activate virtual environment
source venv/bin/activate

# Run example simulations
python examples/basic_simulation.py
python examples/mixed_team_simulation.py

# Run tests
pytest tests/
```

For detailed setup instructions, see **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**.

## Documentation

- **[CLAUDE.md](CLAUDE.md)**: Comprehensive context for AI-assisted development
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Detailed architecture overview
- **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**: Development setup guide
- **[PRD](https://docs.google.com/document/d/1brYkQe10m2wbiVf9XK2nMCle2-JMb0Bp6Ekv2ZOB5TU/edit)**: Complete product requirements (Google Doc)

## Project Structure

```
sdlc_abm/
├── src/
│   ├── simulation/       # Core ABM simulation engine
│   │   ├── agents/       # Developer agent models
│   │   ├── models/       # Team and organizational models
│   │   ├── metrics/      # Metric calculation logic
│   │   └── engine.py     # Main simulation loop
│   ├── api/              # Backend API (FastAPI)
│   ├── frontend/         # React application
│   └── optimization/     # Optimization engine
├── tests/                # All tests (unit, integration, simulation)
├── docs/                 # Documentation
├── data/                 # Sample datasets and templates
└── README.md            # This file
```

## Learning Goals

This is a learning project with the following objectives:

- 🎓 Learn React development and modern frontend practices
- 🎓 Explore systems design and architecture at scale
- 🎓 Understand agent-based modeling techniques
- 🎓 Gain hands-on experience with Docker and Kubernetes
- 🎓 Practice AI-assisted development with Claude Code

Some aspects may be intentionally over-engineered for educational purposes.

## Development Philosophy

- **Learning-First**: Balance practical delivery with learning objectives
- **AI-Assisted**: Built primarily with Claude Code
- **Well-Documented**: Code clarity and documentation prioritized
- **Test-Driven**: Comprehensive testing strategy
- **Iterative**: Ship early, iterate based on feedback

## Core Simulation Concepts

### Agent Model

Each developer agent has configurable attributes:
- Experience Level (Junior → Principal)
- Productivity Rate (PRs per week)
- Code Quality (success rate)
- Review Capacity
- Onboarding Time
- Communication Bandwidth
- Specializations

### Communication Model

Simulates information loss in team communication:
- **Communication Loss Factor**: 0 (perfect) to 1 (total loss)
- **Overhead Scaling**: Linear, Quadratic (default), or Hierarchical
- **Sync vs Async**: Configurable ratio affecting latency

### Simulation Loop

Daily timestep simulation:
1. Agents create PRs based on productivity
2. Agents review PRs based on capacity
3. Communication occurs (with configurable loss)
4. Meetings consume time
5. Incidents occur probabilistically
6. Metrics calculated and recorded

## Contributing

This is currently a solo learning project, but contributions and suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest tests/ && ruff check src/`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## References & Inspiration

- **"The Mythical Man-Month"** by Fred Brooks - Classic work on software project management
- **"Accelerate"** by Forsgren, Humble, and Kim - Science of DevOps and software delivery
- **DORA Metrics** - DevOps Research and Assessment framework
- **Mesa Framework** - Agent-based modeling in Python
- **Years of experience** working with engineering teams at scale

## License

[To be determined]

## Contact

Built by Ben Henry as a learning project with Claude Code.

---

**Status**: 🚀 Phase 2 In Progress - Core simulation engine complete, web application foundation built, advanced features in development.
