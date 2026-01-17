@echo off
echo.
echo 🐳 Law Firm Portal - Docker Setup
echo ==================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed!
    pause
    exit /b 1
)

echo ✅ Docker is installed
echo ✅ Docker Compose is available
echo.

REM Stop any running containers
echo 📦 Stopping existing containers...
docker-compose down

REM Build and start services
echo.
echo 🔨 Building Docker images...
docker-compose build

echo.
echo 🚀 Starting services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Check container status
echo.
echo 📋 Container Status:
docker-compose ps

echo.
echo 🎉 Setup complete!
echo.
echo 📖 Quick Commands:
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart:          docker-compose restart
echo.
echo 🌐 Access the application:
echo   Frontend: http://localhost:8000
echo   Backend:  http://localhost:5000/api
echo.

pause
