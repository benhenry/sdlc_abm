#!/bin/bash
# SDLC SimLab - Status Check Script

set -e

echo "📊 SDLC SimLab Status Check"
echo ""

# Add Docker to PATH
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Check Docker
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is NOT running"
    echo "   Start Docker Desktop: open /Applications/Docker.app"
    exit 1
fi

echo "✅ Docker is running"

# Check docker-compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ docker-compose not found"
    echo "   Install: brew install docker-compose"
    exit 1
fi

echo "✅ Docker Compose is available"
echo ""

# Show service status
echo "📦 Services:"
$COMPOSE_CMD ps

echo ""

# Test API endpoint
echo "🔍 Testing API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is responding"
    echo "   Health: $(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo 'OK')"
else
    echo "⚠️  API is not responding (may still be starting)"
fi

echo ""

# Test Frontend
echo "🔍 Testing Frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend is not responding (may still be starting)"
fi

echo ""
echo "🌐 Access URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
