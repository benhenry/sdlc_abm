# Getting Started with SDLC SimLab

This guide will help you set up your development environment and start working on SDLC SimLab.

## Prerequisites

- **Python 3.11+**: Required for the simulation engine and API
- **Node.js 18+**: Required for the React frontend (when implemented)
- **PostgreSQL 14+**: Primary database (or use SQLite for local dev)
- **Redis 7+**: For Celery task queue and caching
- **Docker** (optional): For running dependencies in containers
- **Git**: Version control

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

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# For local development, you can use SQLite:
# DATABASE_URL=sqlite:///./sdlc_simlab.db
```

### 4. Set Up Database (PostgreSQL)

If using PostgreSQL instead of SQLite:

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

### 5. Set Up Redis

```bash
# Using Docker
docker run --name sdlc-redis \
  -p 6379:6379 \
  -d redis:7

# Or install locally via package manager:
# macOS: brew install redis && brew services start redis
# Ubuntu: sudo apt install redis-server
```

### 6. Run Database Migrations

```bash
# When migrations are implemented
alembic upgrade head
```

## Running the Application

### Development Mode

#### Option 1: Run Components Separately

```bash
# Terminal 1: Start Redis (if not running)
redis-server

# Terminal 2: Start API server
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8000

# Terminal 3: Start Celery worker
source venv/bin/activate
celery -A src.api.celery_app worker --loglevel=info

# Terminal 4: Start React frontend (when implemented)
cd src/frontend
npm install
npm run dev
```

#### Option 2: Use Docker Compose (when implemented)

```bash
docker-compose up
```

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
