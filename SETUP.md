# Legal Case Management System - Setup Guide

## 📋 Prerequisites

1. **Python 3.7+** installed
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Web Browser** (Chrome, Firefox, Edge, etc.)

---

## 🚀 Installation & Setup

### Step 1: Navigate to Project Directory

```bash
cd path/to/dsael
```

Example:
```bash
cd c:\Users\prama\OneDrive\Documents\dsael
```

### Step 2: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- Flask 3.0.0
- Flask-CORS 4.0.0

---

## ▶️ Running the Application

You need **TWO terminal windows** - one for backend, one for frontend.

### Terminal 1: Start Backend Server

```bash
cd backend
python app.py
```

**Expected Output:**
```
Legal Case Management System - Backend
Server starting on http://localhost:5000
 * Serving Flask app 'app'
 * Debug mode: on
```

Server runs at: `http://localhost:5000`

---

### Terminal 2: Start Frontend Server

Open a **NEW terminal window** and run:

```bash
cd frontend
python -m http.server 8000
```

**Expected Output:**
```
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

Server runs at: `http://localhost:8000`

---

## 🌐 Accessing the Application

### Client Portal
Open browser to: **http://localhost:8000/client/login.html**

**Login Credentials (5 sample clients):**
- `john.doe@example.com` / `password123`
- `jane.smith@example.com` / `password123`
- `robert.brown@example.com` / `password123`
- `lisa.anderson@example.com` / `password123`
- `mark.wilson@example.com` / `password123`

### Lawyer Portal
Open browser to: **http://localhost:8000/lawyer/login.html**

**Login Credentials (5 sample lawyers):**
- `sarah.mitchell@lawfirm.com` / `password123`
- `david.chen@lawfirm.com` / `password123`
- `emily.rodriguez@lawfirm.com` / `password123`
- `michael.johnson@lawfirm.com` / `password123`
- `priya.sharma@lawfirm.com` / `password123`

---

## 🎯 Quick Test Flow

### As Client:
1. Login as `john.doe@example.com`
2. Click "Create New Case"
3. Fill form, select "Send to All Lawyers" or pick specific lawyer
4. Check "Mark as Urgent" to test Priority Queue
5. Submit

### As Lawyer:
1. Login as `sarah.mitchell@lawfirm.com`
2. Go to "Available Cases" - see urgent cases at top (Priority Queue)
3. Click "Claim Case"
4. Go to "My Cases" - see claimed case
5. Open case, click "Un-claim" to return to pool

---

## 🛑 Stopping the Servers

Press **Ctrl+C** in each terminal window to stop the servers.

---

## 🔧 Troubleshooting

### Issue: "Port already in use"
**Solution:** Kill the process using that port or use different ports:
```bash
# Backend on different port
python app.py --port 5001

# Frontend on different port
python -m http.server 8001
```
Then update `API_BASE_URL` in `frontend/app.js` accordingly.

### Issue: "Module not found"
**Solution:** Reinstall dependencies:
```bash
cd backend
pip install --upgrade -r requirements.txt
```

### Issue: "CORS errors in browser"
**Solution:** 
1. Make sure both servers are running
2. Clear browser cache
3. Ensure you're accessing via `http://localhost:8000` (not `file://`)

---

## 📁 Project Structure

```
dsael/
├── backend/
│   ├── app.py                  # Flask server
│   ├── core_logic.py           # 10 core logic components
│   ├── data_structures.py      # Queue, PriorityQueue, Stack
│   └── requirements.txt
└── frontend/
    ├── app.js                  # Shared utilities
    ├── styles.css              # Global styles
    ├── client/                 # Client portal (7 pages)
    └── lawyer/                 # Lawyer portal (6 pages)
```

---

## 🎓 Key Features to Test

1. **Priority Queue**: Urgent cases appear first in Available Cases
2. **FIFO Queue**: Normal cases in order
3. **Stack Undo**: Revert case updates
4. **State Machine**: Only valid status transitions allowed
5. **Case Load Limit**: Max 2 cases per lawyer
6. **Direct Assignment**: Request specific lawyer
7. **Un-claim**: Return case to pool

---

## 📝 Notes

- **In-memory storage**: All data is lost when backend restarts
- **No password hashing**: This is for demonstration purposes only
- **Single machine**: Both servers must run on same machine for CORS to work

---

## ✅ Success Indicators

Backend running correctly:
- No error messages in terminal
- Shows "Serving Flask app" message

Frontend running correctly:
- Shows "Serving HTTP on port 8000"
- No 404 errors for main pages

Application working:
- Can login without errors
- Lawyer dropdown populates in "Create Case"
- Available cases load for lawyers

---

**For detailed testing scenarios, see README.md**
