# Getting Started with SDLC SimLab

This guide will help you set up your development environment and start working on SDLC SimLab.

## Quick Start

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

That's it! The simulation engine is fully functional. Continue reading for more details.

## Prerequisites

### Required (Phase 1)
- **Python 3.11+**: Required for the simulation engine
- **Git**: Version control

### Optional (Phase 2 - Not Yet Needed)
- **Node.js 18+**: For React frontend (Phase 2)
- **PostgreSQL 14+**: For API database (Phase 2)
- **Redis 7+**: For Celery task queue (Phase 2)
- **Docker**: For running dependencies in containers (Phase 2)

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sdlc_abm
```

### 2. Set Up Python Environment

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

### 3. Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests to verify everything is working
python -m pytest tests/unit/test_ai_agent.py -v

# Run an example simulation
python examples/basic_simulation.py
```

That's it! You're ready to run simulations.

### Phase 2 Setup (Database, Redis, API)

The following setup steps are only needed when working on Phase 2 features:

<details>
<summary>Click to expand Phase 2 setup instructions</summary>

#### Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# For local development, you can use SQLite:
# DATABASE_URL=sqlite:///./sdlc_simlab.db
```

#### Set Up Database (PostgreSQL)

```bash
# Using Docker
docker run --name sdlc-postgres \
  -e POSTGRES_USER=sdlc_user \
  -e POSTGRES_PASSWORD=sdlc_password \
  -e POSTGRES_DB=sdlc_simlab \
  -p 5432:5432 \
  -d postgres:15

# Update .env with:
# DATABASE_URL=postgresql://sdlc_user:sdlc_password@localhost:5432/sdlc_simlab
```

#### Set Up Redis

```bash
# Using Docker
docker run --name sdlc-redis \
  -p 6379:6379 \
  -d redis:7

# Or install locally via package manager:
# macOS: brew install redis && brew services start redis
# Ubuntu: sudo apt install redis-server
```

#### Run Database Migrations

```bash
# When migrations are implemented
alembic upgrade head
```

</details>

## Running the Application

### Current Status (Phase 1 - Complete ✅)

The **simulation engine** is fully functional and can be run via Python scripts and YAML configurations.
The **API server** and **frontend** are planned for Phase 2 and are not yet implemented.

### Running Simulations

```bash
# Activate virtual environment
source venv/bin/activate

# Run basic human-only team simulation
python examples/basic_simulation.py

# Run mixed human/AI team comparison
python examples/mixed_team_simulation.py

# Run diminishing returns analysis
python examples/diminishing_returns_analysis.py

# Compare multiple scenarios side-by-side (NEW!)
python examples/compare_scenarios.py

# Run a scenario from YAML configuration
python examples/run_scenario.py data/scenarios/mixed_team_example.yaml

# Import historical data from CSV
python examples/import_historical_data.py data/samples/sample_metrics.csv
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
```

### Phase 2: API Server & Frontend (Not Yet Implemented)

The following components are planned for Phase 2 (months 4-6):

```bash
# API server (Phase 2 - NOT YET IMPLEMENTED)
# uvicorn src.api.main:app --reload --port 8000

# Celery worker (Phase 2 - NOT YET IMPLEMENTED)
# celery -A src.api.celery_app worker --loglevel=info

# React frontend (Phase 2 - NOT YET IMPLEMENTED)
# cd src/frontend
# npm install
# npm run dev
```

For now, all simulations are run via Python scripts or YAML configuration files.

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/simulation/     # Simulation validation tests

# Run a specific test file
pytest tests/unit/test_agents.py

# Run a specific test
pytest tests/unit/test_agents.py::test_developer_agent_creation
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

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the architecture guidelines in `docs/ARCHITECTURE.md`
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests and Linting

```bash
pytest tests/
ruff check src/
mypy src/
```

### 4. Commit Changes

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

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Project Structure

```
sdlc_abm/
├── src/
│   ├── simulation/       # Core simulation engine
│   │   ├── agents/       # Developer agent models
│   │   ├── models/       # Team and org models
│   │   ├── metrics/      # Metric calculations
│   │   └── engine.py     # Main simulation loop
│   ├── api/              # FastAPI backend
│   ├── frontend/         # React application
│   └── optimization/     # Optimization engine
├── tests/                # All tests
├── docs/                 # Documentation
├── data/                 # Sample data and templates
├── CLAUDE.md            # AI assistant context
├── README.md            # Project overview
└── requirements.txt     # Python dependencies
```

## Key Files to Review

Before starting development, review these files:

1. **CLAUDE.md**: Comprehensive project context and architecture
2. **docs/ARCHITECTURE.md**: Detailed architecture overview
3. **README.md**: Project goals and learning objectives
4. **PRD** (in Google Docs): Complete product requirements

## Common Tasks

### Creating a New Agent Type

1. Create a new file in `src/simulation/agents/`
2. Define agent class with required attributes
3. Implement agent behavior methods
4. Add tests in `tests/unit/agents/`

### Adding a New API Endpoint

1. Create route in `src/api/routes/`
2. Define request/response schemas in `src/api/schemas/`
3. Add business logic
4. Add tests in `tests/integration/api/`

### Adding a New Metric

1. Create metric calculator in `src/simulation/metrics/`
2. Integrate with simulation engine
3. Add tests in `tests/unit/metrics/`
4. Update API to expose the metric

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps  # If using Docker

# Test connection
psql -h localhost -U sdlc_user -d sdlc_simlab
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Or with Docker
docker ps
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## Learning Resources

### Agent-Based Modeling

- [Mesa Documentation](https://mesa.readthedocs.io/)
- [NetLogo User Manual](https://ccl.northwestern.edu/netlogo/docs/)
- "Agent-Based and Individual-Based Modeling" by Railsback & Grimm

### FastAPI

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### React & Visualization

- [React Documentation](https://react.dev/)
- [D3.js Documentation](https://d3js.org/)
- [Plotly Python](https://plotly.com/python/)

### Software Engineering Metrics

- "Accelerate" by Forsgren, Humble, and Kim
- [DORA Metrics](https://dora.dev/)
- "The Mythical Man-Month" by Fred Brooks

## Getting Help

- **Documentation**: Check `docs/` directory
- **CLAUDE.md**: Comprehensive context for AI assistance
- **Issues**: Create a GitHub issue for bugs or questions
- **PRD**: Refer to the full Product Requirements Document for detailed specifications

## Next Steps

Once your environment is set up:

1. Review the PRD and CLAUDE.md to understand the project scope
2. Look at the current implementation status
3. Pick a task from the backlog or issues
4. Start coding!

Happy hacking! 🚀
