# Legal Consultation & Case Management System

A data structures-focused legal case management system demonstrating practical application of Queue, Priority Queue, Stack, and Hash Table in workflow control.

## 🎯 Project Overview

This system implements a complete legal case management platform with **logic-driven workflow control** using fundamental data structures, rather than typical CRUD operations.

### Tech Stack
- **Backend:** Python 3.x + Flask
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Data Storage:** In-memory data structures
- **Architecture:** RESTful API

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Start the backend server:**
```bash
python app.py
```

The server will start at `http://localhost:5000`

3. **Open the frontend:**
- For clients: Open `frontend/client/login.html` in your browser
- For lawyers: Open `frontend/lawyer/login.html` in your browser

### Demo Accounts

**Client:**
- Email: `client@example.com`
- Password: `password123`

**Lawyer:**
- Email: `lawyer@example.com`
- Password: `password123`

## 📊 Core Data Structures Used

### 1. Queue (FIFO)
- **Normal appointment requests**: First-come, first-served processing
- **Messages**: Preserve chronological order
- **Follow-ups**: Sequential scheduling
- **Notifications**: Time-ordered display

### 2. Priority Queue
- **Urgent cases**: Processed before normal cases
- **Urgent appointments**: Jump ahead in queue
- **Priority-based workflow**: System decides order, not manual sorting

### 3. Stack (LIFO)
- **Case update undo**: Rollback last status change
- **State preservation**: Push before update, pop on undo
- **Legal data safety**: Mistakes can be reversed

### 4. Hash Tables
- **User lookup**: O(1) email → user data
- **Case retrieval**: O(1) caseID → case details
- **Appointments**: O(1) appointmentID → metadata
- **Documents**: O(1) docID → file information

## 🔥 Key Differentiators

### 1. Priority Queue Urgency Handling ⚡
- Urgent cases automatically enter priority queue
- Algorithmic enforcement, not manual sorting
- Demonstrates real-world application of priority queues

### 2. Queue-Based Appointment Processing 📅
- Requests ≠ Confirmations
- FIFO for normal, priority for urgent
- Prevents conflicts automatically

### 3. Stack-Based Undo 🔄
- Rollback case updates safely
- Direct LIFO application
- Rare in student projects

### 4. State Machine Validation ✅
- Valid transitions: `Created → In Review → Active → Closed`
- Invalid jumps blocked
- Workflow correctness enforcement

### 5. Case-Scoped Architecture 🔒
- All messages/documents tied to specific cases
- No global mixing
- Clean access control

## 🧪 Testing the Core Logic

### 1. Test FIFO Queue Behavior
1. Login as client
2. Create 3 normal cases
3. Request appointments for all
4. Login as lawyer
5. Check consultation requests - should be in request order

### 2. Test Priority Queue
1. Create an urgent case (check the "urgent" box)
2. Request appointment
3. Lawyer should see urgent request first, regardless of creation order

### 3. Test Stack Undo
1. Login as lawyer
2. Update a case status
3. Click "Undo Last Update"
4. Verify status reverted to previous state

### 4. Test State Validation
1. Try invalid transition (e.g., Created → Closed)
2. System should reject and show error

### 5. Test Case Ownership
1. Try accessing another user's case URL
2. Should be blocked with "Unauthorized"

### 6. Test Appointment Conflict
1. Approve an appointment for specific time
2. Try approving another for same time
3. Should reject with conflict message

## 📁 Project Structure

```
dsael/
├── backend/
│   ├── data_structures.py    # Custom Queue, PriorityQueue, Stack, Hash Tables
│   ├── core_logic.py          # 10 core logic implementations
│   ├── app.py                 # Flask API server
│   └── requirements.txt
├── frontend/
│   ├── app.js                 # Shared utilities
│   ├── styles.css             # Global styles
│   ├── client/                # Client interface
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── my-cases.html
│   │   ├── create-case.html
│   │   ├── case-details.html
│   │   └── profile.html
│   └── lawyer/                # Lawyer interface
│       ├── login.html
│       ├── dashboard.html
│       ├── consultation-requests.html
│       ├── cases.html
│       ├── case-details.html
│       └── profile.html
└── README.md
```

## 🎓 Data Structures Justification

### Why Queue?
- Appointment requests need fair FIFO processing
- Messages must preserve order
- Follow-ups scheduled chronologically

### Why Priority Queue?
- Urgent cases need immediate attention
- System should automatically prioritize, not rely on manual sorting
- Real-world legal workflows have urgency levels

### Why Stack?
- Legal data is sensitive - mistakes need reversibility
- Undo functionality requires LIFO behavior
- State preservation before updates

### Why Hash Tables?
- O(1) lookups critical for performance
- User authentication requires fast email lookup
- Case access by ID must be instant

## 🔧 Analytics Endpoints

### Queue Statistics
- Endpoint: `/api/analytics/queue-stats`
- Shows: Normal queue length, urgent queue length, total pending

### Urgency Distribution
- Endpoint: `/api/analytics/urgency-distribution`
- Shows: % urgent vs normal cases, validates priority queue logic

## 🎯 10 Core Logic Components

1. ✅ Case Ownership & Access Control
2. ✅ Appointment Request Handling (Queue + Priority Queue)
3. ✅ Appointment Conflict Detection
4. ✅ Urgency-Based Case Handling
5. ✅ Case Update with Undo (Stack)
6. ✅ Case State Validation
7. ✅ Case-Bound Messaging
8. ✅ Document Access Control
9. ✅ Follow-Up Scheduling
10. ✅ Notification System

## 🚧 Known Limitations

- In-memory storage (data lost on restart)
- Passwords not hashed (demo only)
- File uploads simulated (no actual file storage)
- Single server instance (no scalability)

These are intentional for academic demonstration of data structures, not production deployment.

## 📝 Future Enhancements

- Database persistence (SQLite/PostgreSQL)
- Real file upload with storage
- Password hashing (bcrypt)
- Admin dashboard
- Email notifications
- Calendar integration

## 🎓 Academic Value

This project demonstrates:
- Practical application of 4 core data structures
- Logic-driven workflow vs. simple CRUD
- State management
- Access control
- Workflow validation
- Real-world problem solving with DSA

---

**Built for demonstrating practical data structure applications in legal case management.**
