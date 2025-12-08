# SDLC SimLab - Quick Start Guide

Get the web application running in 5 minutes!

## Prerequisites

- **Docker Desktop** installed and running (on macOS/Windows)
  - Download from: https://www.docker.com/products/docker-desktop
  - **Important**: Start Docker Desktop before running commands!
- **Git** for cloning the repository
- 8GB+ RAM recommended

### macOS Users: Docker Desktop Setup

If you see "docker: command not found" or "Docker daemon not running":

```bash
# 1. Start Docker Desktop
open /Applications/Docker.app

# 2. Wait 10-20 seconds for Docker to fully start

# 3. Verify it's running
docker ps

# Should show: CONTAINER ID   IMAGE   ...
```

## Step 1: Easy Start (Recommended)

Use the provided helper scripts:

```bash
# Navigate to project directory
cd sdlc_abm

# Start everything (will check Docker, start services, run migrations)
./start.sh

# Stop everything when done
./stop.sh
```

## Step 1 Alternative: Manual Start

```bash
# Navigate to project directory
cd sdlc_abm

# Copy environment file (already configured for local development)
cp .env.example .env

# Start all services (this will build containers on first run)
docker-compose up -d

# This starts 5 services:
# - PostgreSQL (database)
# - Redis (cache + message broker)
# - FastAPI (backend API)
# - Celery (background workers)
# - React (frontend)
```

**First time?** Building containers takes 3-5 minutes. Subsequent starts are instant.

## Step 2: Initialize Database

```bash
# Run database migrations to create tables
docker-compose exec api alembic upgrade head

# You should see output like:
# INFO  [alembic.runtime.migration] Running upgrade -> 001, Initial schema
```

## Step 3: Verify Everything Works

```bash
# Check all services are running
docker-compose ps

# Should show 5 services with "Up" status

# Test the API
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"0.2.0","service":"sdlc-simlab-api"}

# Test the database connection
curl http://localhost:8000/api/scenarios

# Should return:
# {"scenarios":[],"total":0}
```

## Step 4: Access the Application

Open your browser to:

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **API Health Check**: http://localhost:8000/health

You should see the SDLC SimLab dashboard!

## Step 5: Create Your First Scenario

### Option A: Via Frontend (Placeholder)
The scenario builder wizard is under development. For now, use the API or CLI.

### Option B: Via API

```bash
# Create a scenario from a template
curl -X POST "http://localhost:8000/api/scenarios/from-template?template_name=baseline_human_only&scenario_name=My First Scenario" | json_pp

# Copy the "id" from the response

# View the scenario
curl http://localhost:8000/api/scenarios/<scenario-id> | json_pp
```

### Option C: Via Python CLI

```bash
# Access the API container
docker-compose exec api bash

# Run an example simulation
python examples/basic_simulation.py

# Or run a mixed team simulation
python examples/mixed_team_simulation.py

# Exit the container
exit
```

## Step 6: Run a Simulation

```bash
# Create and run a simulation from a template
# 1. First, create a scenario (if you haven't already)
SCENARIO_ID=$(curl -s -X POST "http://localhost:8000/api/scenarios/from-template?template_name=baseline_human_only&scenario_name=Test Simulation" | jq -r '.id')

echo "Created scenario: $SCENARIO_ID"

# 2. Get the scenario config
CONFIG=$(curl -s http://localhost:8000/api/scenarios/$SCENARIO_ID | jq '.config_json')

# 3. Start the simulation
SIM_ID=$(curl -s -X POST http://localhost:8000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d "{\"scenario_id\":\"$SCENARIO_ID\",\"config_json\":$CONFIG}" | jq -r '.id')

echo "Started simulation: $SIM_ID"

# 4. Monitor progress
watch -n 2 "curl -s http://localhost:8000/api/simulations/$SIM_ID | jq '.status, .progress'"

# Press Ctrl+C to stop watching

# 5. View results once completed
curl -s http://localhost:8000/api/simulations/$SIM_ID | jq '.results_json.metrics'
```

Or simply navigate to the Dashboard at http://localhost:3000 to see it running!

## Common Commands

### Managing Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f celery

# Restart a service
docker-compose restart api

# Rebuild after code changes
docker-compose up -d --build
```

### Database Operations

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Rollback one migration
docker-compose exec api alembic downgrade -1

# Access PostgreSQL directly
docker-compose exec postgres psql -U simlab -d sdlc_simlab

# In psql:
# \dt                    # List tables
# SELECT * FROM scenarios LIMIT 5;
# \q                     # Quit
```

### Development Workflow

```bash
# Edit backend code
# Changes auto-reload (no restart needed)

# Edit frontend code
cd src/frontend
# Edit files in src/
# Browser auto-refreshes

# Install new Python package
docker-compose exec api pip install <package>
# Add to requirements.txt

# Install new npm package
docker-compose exec frontend npm install <package>
# Updates package.json automatically
```

## Troubleshooting

### Services won't start?

```bash
# Check if ports are already in use
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Stop conflicting services or change ports in docker-compose.yml
```

### Database connection errors?

```bash
# Wait for PostgreSQL to be ready
docker-compose logs postgres

# Recreate database
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### Frontend can't connect to API?

```bash
# Check API is running
curl http://localhost:8000/health

# Check CORS settings in src/api/main.py
# Should include http://localhost:3000

# Check browser console for errors
```

### Celery tasks not running?

```bash
# Check Celery worker logs
docker-compose logs celery

# Restart Celery worker
docker-compose restart celery

# Verify Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## Next Steps

1. **Explore the Dashboard** - View recent simulations and scenarios
2. **Try the CLI Examples** - Run `python examples/basic_simulation.py`
3. **Read the API Docs** - http://localhost:8000/api/docs
4. **Check the Architecture** - See `docs/ARCHITECTURE.md`
5. **Build Features** - Scenario builder, visualizations, etc.

## Useful Links

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **API Health**: http://localhost:8000/health
- **API OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Getting Help

- **API Documentation**: Auto-generated at http://localhost:8000/api/docs
- **Project README**: See `README.md` for detailed information
- **Architecture Docs**: See `docs/ARCHITECTURE.md`
- **Phase 2 Summary**: See `PHASE2_COMPLETE.md`

---

**Enjoy building with SDLC SimLab!** 🚀

If you encounter issues, check the logs with `docker-compose logs -f`
