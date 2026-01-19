#!/bin/bash

echo "🐳 Law Firm Portal - Docker Setup"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ Docker Compose is available"
echo ""

# Stop any running containers
echo "📦 Stopping existing containers..."
docker-compose down

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "law-backend.*Up"; then
    echo "✅ Backend is running on http://localhost:5000"
else
    echo "❌ Backend failed to start"
    echo "Check logs with: docker-compose logs backend"
fi

if docker-compose ps | grep -q "law-frontend.*Up"; then
    echo "✅ Frontend is running on http://localhost:8000"
else
    echo "❌ Frontend failed to start"
    echo "Check logs with: docker-compose logs frontend"
fi

echo ""
echo "📋 Container Status:"
docker-compose ps

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Quick Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo ""
echo "🌐 Access the application:"
echo "  Frontend: http://localhost:8000"
echo "  Backend:  http://localhost:5000/api"
