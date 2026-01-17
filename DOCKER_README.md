# Docker Deployment Guide

## Prerequisites

- Docker Desktop installed (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0 or higher
- At least 2GB free disk space

## Quick Start

### 1. Build and Start All Services

```bash
# Build and start in detached mode
docker-compose up -d --build

# Or run in foreground (see logs)
docker-compose up --build
```

### 2. Access the Application

- **Frontend:** http://localhost:8000
- **Backend API:** http://localhost:5000/api

### 3. Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## Docker Services

### Backend (Flask API)
- **Container:** `law-backend`
- **Port:** 5000
- **Technology:** Python 3.12 + Flask
- **Auto-reload:** Yes (development mode)

### Frontend (Static Files)
- **Container:** `law-frontend`
- **Port:** 8000
- **Technology:** Nginx Alpine
- **Serves:** HTML/CSS/JS static files

---

## Commands Reference

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

### Execute Commands Inside Container

```bash
# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Run Python command in backend
docker-compose exec backend python -c "print('Hello')"
```

### Check Container Status

```bash
docker-compose ps
```

---

## Development Workflow

### Making Backend Changes

1. Edit files in `backend/` directory
2. Changes auto-reload (Flask debug mode)
3. No rebuild needed for Python code changes

### Making Frontend Changes

1. Edit files in `frontend/` directory
2. Refresh browser to see changes
3. No rebuild needed for HTML/CSS/JS changes

### Adding Python Dependencies

1. Add package to `requirements.txt`
2. Rebuild backend:
   ```bash
   docker-compose up -d --build backend
   ```

---

## Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution:**
```bash
# Windows - Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "5001:5000"  # Changed from 5000:5000
```

### Backend Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Missing dependencies → Rebuild with `--build`
- Import errors → Check Python files for syntax errors
- Port conflict → Change port in docker-compose.yml

### Frontend Shows 404

**Check:**
1. Files exist in `frontend/` directory
2. Nginx config is correct
3. View logs: `docker-compose logs frontend`

### Cannot Connect to Backend from Frontend

**Check:**
1. Backend is running: `docker-compose ps`
2. Both containers on same network
3. Frontend calls `http://localhost:5000/api` (not container name)

---

## Production Deployment

### Security Checklist

1. **Change SECRET_KEY** in docker-compose.yml
   ```yaml
   environment:
     - SECRET_KEY=your-secure-random-key-here
   ```

2. **Disable Debug Mode**
   ```yaml
   environment:
     - FLASK_ENV=production
   ```

3. **Use Production WSGI Server**
   
   Update `Dockerfile.backend`:
   ```dockerfile
   RUN pip install gunicorn
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
   ```

4. **Add Database** (Replace in-memory storage)
   ```yaml
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: lawfirm
         POSTGRES_USER: admin
         POSTGRES_PASSWORD: secure-password
   ```

5. **Enable HTTPS** with reverse proxy (nginx/traefik)

6. **Add Health Checks**
   ```yaml
   services:
     backend:
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   ```

---

## Architecture

```
┌─────────────────┐
│   Browser       │
│  localhost:8000 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │
│   (Nginx)       │     │    (Flask)      │
│   Port 8000     │     │    Port 5000    │
└─────────────────┘     └─────────────────┘
         │                      │
         └──────────────────────┘
              law-network
```

---

## File Structure

```
law/
├── docker-compose.yml      # Orchestration config
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container
├── nginx.conf              # Nginx configuration
├── requirements.txt        # Python dependencies
├── .dockerignore          # Excluded files
├── backend/               # Flask application
│   ├── app.py
│   ├── core_logic.py
│   └── data_structures.py
└── frontend/              # Static files
    ├── app.js
    ├── styles.css
    └── client/
        ├── dashboard.html
        ├── create-case.html
        └── ...
```

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | development | development/production |
| `SECRET_KEY` | dev-secret-key-change-in-production | Session secret |
| `PORT` | 5000 | Flask port |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | http://localhost:5000/api | Backend API URL |

---

## Monitoring

### View Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything (careful!)
docker system prune -a
```

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify ports: `docker-compose ps`
3. Rebuild: `docker-compose up -d --build`
4. Fresh start: `docker-compose down -v && docker-compose up -d --build`
