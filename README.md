# Legal Case Management System

A web-based legal case management platform with client and lawyer portals.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
docker-compose up --build
```

Then open: **http://localhost:8000/client/login.html**

### Manual Setup

```bash
# Terminal 1 - Start Backend
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2 - Start Frontend
cd frontend
python -m http.server 8000
```

---

## 🔑 Login Credentials

**All passwords:** `password123`

### Client Accounts
- `a@gmail.com` - John Doe
- `b@gmail.com` - Jane Smith
- `c@gmail.com` - Robert Brown
- `d@gmail.com` - Lisa Anderson
- `e@gmail.com` - Mark Wilson

### Lawyer Accounts
- `a@lawfirm.com` - Sarah Mitchell (Civil & Criminal Law) - $5,000/hearing
- `b@lawfirm.com` - David Chen (Civil & Criminal Law) - $5,500/hearing
- `c@lawfirm.com` - Emily Rodriguez (Family Law) - $3,500/hearing
- `d@lawfirm.com` - Michael Johnson (Corporate Law) - $4,500/hearing
- `e@lawfirm.com` - Priya Sharma (Property Law) - $6,000/hearing

---

## 🌐 Access Links

**Client Portal:** http://localhost:8000/client/login.html  
**Lawyer Portal:** http://localhost:8000/lawyer/login.html

After login:
- Client Dashboard: http://localhost:8000/client/dashboard.html
- Lawyer Dashboard: http://localhost:8000/lawyer/dashboard.html

---

## 📋 Features

**Clients Can:**
- Create legal cases and select lawyers by specialization
- Request consultations
- Track case progress
- Upload documents and send messages
- View hearing calendar
- Edit profile

**Lawyers Can:**
- View assigned cases
- Manage consultation requests
- Update case status (with undo feature)
- Schedule hearings and follow-ups
- Communicate with clients
- View weekly calendar
- Edit profile and specializations

---

## 🔧 Common Issues

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

**Docker not working:**
- Make sure Docker Desktop is running
- Try: `docker-compose down` then `docker-compose up --build`

**Can't connect to backend:**
- Verify backend is running at http://localhost:5000
- Check frontend is at http://localhost:8000 (not file://)

**Changes not showing:**
- Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

---

## 🐳 Docker Commands

```bash
# Start
docker-compose up --build

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Environment Variables (Optional)

Create a `.env` file to customize ports and settings:

```bash
# Copy example file
cp .env.example .env

# Edit as needed
BACKEND_PORT=5000
FRONTEND_PORT=8000
SECRET_KEY=your-secret-key-here
```

Default values work fine for local development.

---

## 📁 Project Structure

```
law/
├── backend/
│   ├── app.py              # Flask API server
│   ├── core_logic.py       # Business logic
│   ├── data_structures.py  # Queue, Stack, Priority Queue
│   └── requirements.txt
├── frontend/
│   ├── client/             # Client portal pages
│   └── lawyer/             # Lawyer portal pages
├── docker-compose.yml
└── README.md
```

---

## 🎯 Core Features

This system demonstrates:
- **Queue (FIFO):** Appointment requests, messages
- **Priority Queue:** Urgent cases sorted by deadline
- **Stack (LIFO):** Undo case updates
- **Hash Tables:** Fast user/case lookups

---

## ⚠️ Note

This is a demonstration project using in-memory storage. Data is lost when the server restarts.

---

**Need help?** Check browser console (F12) for errors or backend terminal for Python errors.
