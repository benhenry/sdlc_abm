#!/bin/bash
# SDLC SimLab - Stop Script

set -e

echo "🛑 Stopping SDLC SimLab..."
echo ""

# Add Docker to PATH
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Check if docker-compose exists
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "⚠️  docker-compose not found!"
    exit 1
fi

# Stop services
$COMPOSE_CMD down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 To start again: ./start.sh"
echo ""
