# Getting Started with SDLC SimLab

This guide will help you set up your development environment and start working on SDLC SimLab.

## Quick Start

### Option 1: Web Application (Recommended - Phase 2)

```bash
# 1. Start Docker Desktop (macOS)
open /Applications/Docker.app

# 2. Clone and navigate to project
git clone <repository-url>
cd sdlc_abm

# 3. Start all services with one command
./start.sh

# 4. Access the application
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/api/docs
```

### Option 2: CLI Simulations Only (Phase 1)

```bash
# Clone and setup
git clone <repository-url>
cd sdlc_abm
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run your first simulation!
python examples/mixed_team_simulation.py
```

## Current Status

### ✅ Phase 1: Complete (Simulation Engine)
- Fully functional agent-based simulation engine
- Developer and AI agent models
- Scenario configuration via YAML
- Comparison and analysis tools
- 89 passing tests with 82%+ coverage

### ✅ Phase 2: Complete (Web Application)
- **Backend**: FastAPI with 27 REST endpoints
- **Frontend**: React + TypeScript web interface
- **Database**: PostgreSQL with async SQLAlchemy ORM
- **Background Jobs**: Celery + Redis for async simulations
- **Real-time Updates**: WebSocket support
- **Infrastructure**: Docker Compose orchestration

### ⏳ Phase 3-4: Planned
- Advanced visualizations with D3.js/Plotly
- GitHub/GitLab integration for data import
- Calibration and optimization tools

## Prerequisites

### For Web Application (Phase 2)
- **Docker Desktop**: Required for running all services
  - Download: https://www.docker.com/products/docker-desktop
  - **macOS**: Install and start Docker Desktop
  - **Windows**: Install and start Docker Desktop
- **Git**: Version control
- **8GB+ RAM**: Recommended for Docker services

### For CLI Development (Phase 1 Only)
- **Python 3.11+**: Required for the simulation engine
- **Git**: Version control

## Setup Instructions

### Web Application Setup (Docker)

This is the **recommended** way to run SDLC SimLab as it includes the full web interface.

#### 1. Install Docker Desktop

**macOS:**
```bash
# Option A: Download from website
# Visit: https://www.docker.com/products/docker-desktop

# Option B: Install via Homebrew
brew install --cask docker
```

**Windows:**
- Download from: https://www.docker.com/products/docker-desktop

#### 2. Clone the Repository

```bash
git clone <repository-url>
cd sdlc_abm
```

#### 3. Start Docker Desktop

**macOS:**
```bash
# Open Docker Desktop
open /Applications/Docker.app

# Wait 10-20 seconds for Docker to start
# You'll see the Docker icon in your menu bar

# Verify it's running
docker ps
```

#### 4. Start SDLC SimLab

```bash
# Use the helper script (easiest)
./start.sh

# Or manually with docker-compose
docker-compose up -d
docker-compose exec -T api alembic upgrade head
```

The `start.sh` script will:
- ✅ Check Docker is running
- ✅ Start 5 services (Postgres, Redis, API, Celery, Frontend)
- ✅ Run database migrations
- ✅ Show service status
- ✅ Display access URLs

#### 5. Access the Application

Open your browser to:

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **API Health Check**: http://localhost:8000/health

#### 6. Create Your First Scenario

**Via API:**
```bash
# Create a scenario from a template
curl -X POST "http://localhost:8000/api/scenarios/from-template?template_name=small_team&scenario_name=My%20First%20Scenario"

# List all scenarios
curl http://localhost:8000/api/scenarios
```

**Via Frontend:**
1. Navigate to http://localhost:3000
2. Go to "Scenario Library"
3. Click "Create from Template"
4. Select a template and customize

#### Helper Scripts

```bash
./start.sh   # Start all services
./status.sh  # Check service status
./stop.sh    # Stop all services
```

For more details, see:
- **[QUICKSTART.md](../QUICKSTART.md)**: 5-minute setup guide
- **[DOCKER_SETUP.md](../DOCKER_SETUP.md)**: Comprehensive Docker reference
- **[NEXT_STEPS.md](../NEXT_STEPS.md)**: What to do after setup

### CLI Development Setup (Python)

If you only want to run simulations via Python scripts (no web interface):

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd sdlc_abm
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests to verify everything is working
pytest tests/

# Run an example simulation
python examples/basic_simulation.py
```

## Running the Application

### Web Application (Phase 2)

Once Docker services are running:

```bash
# Check status
./status.sh

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f celery

# Access the frontend
open http://localhost:3000

# Access API documentation
open http://localhost:8000/api/docs
```

**Available Features:**
- ✅ Dashboard with recent simulations
- ✅ Scenario Library (browse and manage scenarios)
- ✅ Create scenarios from 6 built-in templates
- ✅ Full CRUD operations via API
- ⏳ Scenario Builder wizard (placeholder)
- ⏳ Run simulations with real-time progress (backend ready, UI in progress)
- ⏳ Visualizations (backend ready, UI in progress)
- ⏳ Comparison mode (backend ready, UI in progress)

### CLI Simulations (Phase 1)

```bash
# Activate virtual environment
source venv/bin/activate

# Run basic human-only team simulation
python examples/basic_simulation.py

# Run mixed human/AI team comparison
python examples/mixed_team_simulation.py

# Run diminishing returns analysis
python examples/diminishing_returns_analysis.py

# Compare multiple scenarios side-by-side
python examples/compare_scenarios.py

# Run a scenario from YAML configuration
python examples/run_scenario.py data/scenarios/mixed_team_example.yaml

# Import historical data from CSV
python examples/import_historical_data.py data/samples/sample_metrics.csv
```

### CLI Simulations Inside Docker

You can also run CLI simulations inside the Docker API container:

```bash
# Access the API container
docker-compose exec api bash

# Run example simulations
python examples/basic_simulation.py
python examples/mixed_team_simulation.py

# Exit the container
exit
```

### Scenario Comparison Tool

Compare multiple team configurations to find the optimal balance:

```python
from src.simulation.comparison import ScenarioComparison

# Create comparison
comparison = ScenarioComparison()

# Add scenarios
comparison.add_scenario("data/scenarios/comparison/baseline_human_only.yaml")
comparison.add_scenario("data/scenarios/comparison/balanced_mixed_team.yaml")

# Run all and compare
results = comparison.run_all()
comparison.print_comparison()

# Export results
comparison.export_to_json("comparison_results.json")
comparison.export_to_csv("comparison_results.csv")
```

Pre-built comparison scenarios:
- `baseline_human_only.yaml` - 7 humans only
- `balanced_mixed_team.yaml` - 5 humans + 4 AI agents
- `ai_heavy_team.yaml` - 3 humans + 10 AI agents
- `premium_ai_team.yaml` - 5 humans + 4 Opus AI agents

## Running Tests

### All Tests

```bash
# Run all tests (89 tests)
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
```

### Backend API Tests

```bash
# From host machine (requires running Docker services)
docker-compose exec api pytest tests/

# Inside API container
docker-compose exec api bash
pytest tests/
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies (first time only)
npm install

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## Code Quality

### Linting and Formatting

```bash
# Run ruff for linting
ruff check src/

# Auto-fix linting issues
ruff check src/ --fix

# Format code with ruff
ruff format src/

# Type checking with mypy
mypy src/
```

### Pre-commit Checks

Before committing code:

```bash
# Run linting
ruff check src/

# Run tests
pytest tests/

# Check type hints
mypy src/
```

## Development Workflow

### 1. Start Development Environment

```bash
# Start Docker services
./start.sh

# Or for CLI development only
source venv/bin/activate
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

**Backend (API):**
- Edit files in `src/api/`
- Changes auto-reload (no restart needed)
- Add tests in `tests/api/`

**Frontend:**
- Edit files in `src/frontend/src/`
- Browser auto-refreshes
- Add components in `src/frontend/src/components/`
- Add views in `src/frontend/src/views/`

**Simulation Engine:**
- Edit files in `src/simulation/`
- Add tests in `tests/unit/` or `tests/integration/`

### 4. Run Tests and Linting

```bash
pytest tests/
ruff check src/
mypy src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: description of your feature"
```

Follow conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Project Structure

```
sdlc_abm/
├── src/
│   ├── simulation/       # Core simulation engine (Phase 1)
│   │   ├── agents/       # Developer and AI agent models
│   │   ├── models/       # Team and org models
│   │   ├── metrics/      # Metric calculations
│   │   ├── engine.py     # Main simulation loop
│   │   ├── comparison.py # Multi-scenario comparison
│   │   └── data_import.py # CSV import
│   ├── api/              # FastAPI backend (Phase 2)
│   │   ├── routes/       # API endpoints
│   │   ├── models.py     # SQLAlchemy ORM models
│   │   ├── schemas.py    # Pydantic request/response
│   │   ├── tasks.py      # Celery background tasks
│   │   └── websockets.py # WebSocket handlers
│   └── frontend/         # React application (Phase 2)
│       ├── src/
│       │   ├── components/ # Reusable UI components
│       │   ├── views/      # Main screens
│       │   ├── services/   # API client
│       │   └── types.ts    # TypeScript types
│       └── Dockerfile
├── tests/                # All tests
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
│   ├── GETTING_STARTED.md    # This file
│   ├── ARCHITECTURE.md       # System architecture
│   └── SIMULATION_ENGINE.md  # Engine details
├── data/                 # Sample data and templates
│   ├── scenarios/        # YAML scenario templates
│   └── samples/          # Sample CSV data
├── examples/             # Example Python scripts
├── alembic/              # Database migrations
├── docker-compose.yml    # Docker orchestration
├── start.sh, stop.sh, status.sh  # Helper scripts
├── QUICKSTART.md         # 5-minute setup
├── DOCKER_SETUP.md       # Docker reference
├── NEXT_STEPS.md         # Getting started guide
├── CLAUDE.md             # AI assistant context
├── README.md             # Project overview
└── requirements.txt      # Python dependencies
```

## Common Tasks

### Working with Docker Services

```bash
# Start services
./start.sh
# OR
docker-compose up -d

# Stop services
./stop.sh
# OR
docker-compose down

# Restart a specific service
docker-compose restart api
docker-compose restart frontend

# Rebuild after code changes
docker-compose up -d --build

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f celery
docker-compose logs -f frontend

# Access container shell
docker-compose exec api bash
docker-compose exec frontend sh

# Check service status
docker-compose ps
# OR
./status.sh
```

### Database Operations

```bash
# Run migrations
docker-compose exec -T api alembic upgrade head

# Rollback one migration
docker-compose exec -T api alembic downgrade -1

# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Access PostgreSQL directly
docker-compose exec postgres psql -U simlab -d sdlc_simlab

# In psql:
# \dt                    # List tables
# SELECT * FROM scenarios LIMIT 5;
# \q                     # Quit
```

### Creating a New Agent Type

1. Create a new file in `src/simulation/agents/`
2. Define agent class inheriting from `Agent`
3. Implement required methods (`step()`, `on_added_to_simulation()`)
4. Add tests in `tests/unit/`

### Adding a New API Endpoint

1. Create route in `src/api/routes/`
2. Define request/response schemas in `src/api/schemas.py`
3. Add business logic
4. Update router in `src/api/main.py`
5. Add tests in `tests/api/`

### Adding a New Frontend View

1. Create component in `src/frontend/src/views/`
2. Add route in `src/frontend/src/App.tsx`
3. Add navigation link in `src/frontend/src/components/Layout.tsx`
4. Create API service methods in `src/frontend/src/services/`

### Adding a New Metric

1. Add metric to simulation engine in `src/simulation/engine.py`
2. Update `SimulationMetrics` type in `src/frontend/src/types.ts`
3. Update API schema in `src/api/schemas.py`
4. Add tests in `tests/unit/`

## Troubleshooting

### Docker Issues

```bash
# Docker Desktop not running
open /Applications/Docker.app  # macOS
# Wait 10-20 seconds for startup

# Services won't start
docker-compose down
docker-compose up -d --build

# Port already in use
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# View detailed logs
docker-compose logs -f
```

### Database Issues

```bash
# Database connection errors
docker-compose logs postgres

# Reset database (WARNING: Deletes all data!)
docker-compose down -v
docker-compose up -d
docker-compose exec -T api alembic upgrade head

# Create missing simlab database
docker-compose exec -T postgres psql -U simlab -d postgres -c "CREATE DATABASE simlab;"
```

### Frontend Issues

```bash
# Frontend can't connect to API
# Check API is running
curl http://localhost:8000/health

# Check CORS settings in src/api/main.py
# Should include http://localhost:3000

# Rebuild frontend
docker-compose restart frontend
```

### Import Errors (CLI Development)

```bash
# ModuleNotFoundError: No module named 'src'
# This is fixed by pytest.ini for tests

# For running scripts, make sure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or activate virtual environment
source venv/bin/activate
```

## Key Files to Review

Before starting development, review these files:

1. **[CLAUDE.md](../CLAUDE.md)**: Comprehensive project context and architecture
2. **[docs/ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed architecture overview
3. **[README.md](../README.md)**: Project goals and learning objectives
4. **[QUICKSTART.md](../QUICKSTART.md)**: 5-minute setup guide
5. **[DOCKER_SETUP.md](../DOCKER_SETUP.md)**: Docker troubleshooting
6. **[PHASE2_COMPLETE.md](../PHASE2_COMPLETE.md)**: What we built in Phase 2

## Learning Resources

### Agent-Based Modeling

- [Mesa Documentation](https://mesa.readthedocs.io/)
- [NetLogo User Manual](https://ccl.northwestern.edu/netlogo/docs/)
- "Agent-Based and Individual-Based Modeling" by Railsback & Grimm

### FastAPI & Backend

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Celery Documentation](https://docs.celeryq.dev/)

### React & Frontend

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Plotly JavaScript](https://plotly.com/javascript/)

### Docker

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Overview](https://docs.docker.com/compose/)

### Software Engineering Metrics

- "Accelerate" by Forsgren, Humble, and Kim
- [DORA Metrics](https://dora.dev/)
- "The Mythical Man-Month" by Fred Brooks

## Getting Help

- **Documentation**: Check `docs/` directory and root-level MD files
- **CLAUDE.md**: Comprehensive context for AI assistance
- **Issues**: Create a GitHub issue for bugs or questions
- **Logs**: Check `docker-compose logs -f` for errors
- **API Docs**: http://localhost:8000/api/docs (when running)

## Next Steps

Once your environment is set up:

1. **Explore the web application**: http://localhost:3000
2. **Try the API**: http://localhost:8000/api/docs
3. **Run some simulations**: Try the example scripts
4. **Review the code**: Look at `src/simulation/` and `src/api/`
5. **Check current status**: See [PHASE2_COMPLETE.md](../PHASE2_COMPLETE.md)
6. **Pick a task**: Look for placeholder features to implement

Happy hacking! 🚀
