#!/bin/bash
# SDLC SimLab - Easy Start Script

set -e

echo "🚀 Starting SDLC SimLab..."
echo ""

# Add Docker to PATH
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Unset any conflicting environment variables from shell
unset DATABASE_URL REDIS_URL CELERY_BROKER_URL CELERY_RESULT_BACKEND

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "⚠️  Docker Desktop is not running!"
    echo ""
    echo "Please start Docker Desktop first:"
    echo "  1. Open Docker Desktop: open /Applications/Docker.app"
    echo "  2. Wait for it to start (10-20 seconds)"
    echo "  3. Run this script again: ./start.sh"
    echo ""
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose exists
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "⚠️  docker-compose not found!"
    echo ""
    echo "Install it with:"
    echo "  brew install docker-compose"
    echo ""
    exit 1
fi

echo "✅ Docker Compose found: $COMPOSE_CMD"
echo ""

# Start services
echo "📦 Starting services (Postgres, Redis, API, Celery, Frontend)..."
$COMPOSE_CMD up -d

# Wait a bit for services to start
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check status
echo ""
echo "📊 Service Status:"
$COMPOSE_CMD ps

# Initialize database if needed
echo ""
echo "🗃️  Running database migrations..."
$COMPOSE_CMD exec -T api alembic upgrade head 2>/dev/null || echo "⚠️  Migrations failed - database might already be initialized"

# Show URLs
echo ""
echo "✅ SDLC SimLab is ready!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
