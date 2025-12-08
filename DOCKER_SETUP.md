# Docker Setup Guide for SDLC SimLab

## Quick Reference

**Three helper scripts make everything easy:**

```bash
./start.sh    # Start all services
./status.sh   # Check if everything is running
./stop.sh     # Stop all services
```

## First-Time Setup

### 1. Install Docker Desktop (if not already installed)

**macOS:**
```bash
# Option A: Download from website
# Visit: https://www.docker.com/products/docker-desktop

# Option B: Install via Homebrew
brew install --cask docker
```

**Windows:**
- Download from: https://www.docker.com/products/docker-desktop

### 2. Start Docker Desktop

**macOS:**
```bash
# Open Docker Desktop application
open /Applications/Docker.app

# Wait 10-20 seconds for Docker to start
# You'll see the Docker icon in your menu bar

# Verify it's running
docker ps
```

### 3. Install docker-compose (if needed)

Modern Docker Desktop includes Docker Compose. If you see errors:

```bash
# macOS
brew install docker-compose

# Verify installation
docker-compose --version
```

## Using the Helper Scripts

### Start Everything

```bash
cd sdlc_abm
./start.sh
```

This will:
- ✅ Check Docker is running
- ✅ Start 5 services (Postgres, Redis, API, Celery, Frontend)
- ✅ Run database migrations
- ✅ Show service status
- ✅ Display access URLs

**Expected output:**
```
🚀 Starting SDLC SimLab...
✅ Docker is running
✅ Docker Compose found: docker-compose
📦 Starting services...
⏳ Waiting for services to start...
📊 Service Status:
   ✅ postgres (healthy)
   ✅ redis (healthy)
   ✅ api (healthy)
   ✅ celery (healthy)
   ✅ frontend (healthy)
🗃️  Running database migrations...
✅ SDLC SimLab is ready!

🌐 Access the application:
   Frontend:  http://localhost:3000
   API Docs:  http://localhost:8000/api/docs
```

### Check Status

```bash
./status.sh
```

Shows:
- Docker daemon status
- All service statuses
- API health check
- Frontend availability
- Access URLs

### Stop Everything

```bash
./stop.sh
```

Cleanly stops all services. Your data persists!

## Manual Docker Commands

If you prefer direct Docker control:

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f celery
```

### Check Status
```bash
docker-compose ps
```

### Stop Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Run Database Migrations
```bash
docker-compose exec api alembic upgrade head
```

### Access Container Shell
```bash
# API container
docker-compose exec api bash

# Run Python code
docker-compose exec api python examples/basic_simulation.py
```

## Troubleshooting

### Docker Desktop Won't Start

**macOS:**
1. Quit Docker Desktop completely
2. Open Activity Monitor and kill any "Docker" processes
3. Delete: `~/Library/Containers/com.docker.docker`
4. Restart Docker Desktop

### Port Already in Use

If ports 3000, 5432, 6379, or 8000 are in use:

```bash
# Check what's using the port
lsof -i :3000   # Frontend
lsof -i :8000   # API
lsof -i :5432   # PostgreSQL
lsof -i :6379   # Redis

# Kill the process or change ports in docker-compose.yml
```

### Services Won't Start

```bash
# View detailed logs
docker-compose logs

# Restart specific service
docker-compose restart api

# Rebuild everything
docker-compose down
docker-compose up -d --build
```

### Database Connection Errors

```bash
# Wait for PostgreSQL to be ready
docker-compose logs postgres

# Recreate database (WARNING: Deletes data!)
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### Frontend Can't Connect to API

1. Check API is running: `curl http://localhost:8000/health`
2. Check CORS settings in `src/api/main.py`
3. Check browser console for errors
4. Verify `VITE_API_URL` in `.env`

### Permission Denied Errors

```bash
# Make scripts executable
chmod +x start.sh stop.sh status.sh
```

## Environment Variables

The `.env` file controls configuration:

```bash
# Copy example
cp .env.example .env

# Edit as needed
nano .env
```

**Key variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CELERY_BROKER_URL` - Celery message broker
- `VITE_API_URL` - Frontend API endpoint

## Data Persistence

Data persists between restarts in Docker volumes:

```bash
# View volumes
docker volume ls

# Remove volumes (WARNING: Deletes all data!)
docker-compose down -v
```

**Volumes:**
- `postgres_data` - Database tables and data
- `redis_data` - Redis cache (can be safely deleted)

## Performance Tips

### Allocate More Resources

Docker Desktop → Settings → Resources:
- **CPUs**: 4+ cores recommended
- **Memory**: 8GB+ recommended
- **Disk**: 20GB+ recommended

### Speed Up Builds

```bash
# Use BuildKit (faster builds)
export DOCKER_BUILDKIT=1

# Rebuild with no cache
docker-compose build --no-cache
```

## Cleanup

### Remove Stopped Containers
```bash
docker-compose down
```

### Remove Volumes (Delete Data)
```bash
docker-compose down -v
```

### Remove Images (Free Space)
```bash
docker-compose down --rmi all
```

### Full Cleanup
```bash
# Remove everything (WARNING: Deletes all Docker data)
docker system prune -a --volumes
```

## Next Steps

Once Docker is running:

1. **Access the app**: http://localhost:3000
2. **Read API docs**: http://localhost:8000/api/docs
3. **Run examples**: `docker-compose exec api python examples/basic_simulation.py`
4. **View logs**: `docker-compose logs -f`

## Getting Help

- **Service Status**: `./status.sh`
- **View Logs**: `docker-compose logs -f`
- **Docker Desktop Logs**: Docker Desktop → Troubleshoot → View logs
- **Project Issues**: Check GitHub issues

---

**Happy simulating!** 🚀
