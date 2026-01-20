# 📚 Legal Case Management System - DSA Course Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Data Structures Implemented](#data-structures-implemented)
3. [Core Features](#core-features)
4. [System Architecture](#system-architecture)
5. [How to Run the Application](#how-to-run-the-application)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Testing the Data Structures](#testing-the-data-structures)
8. [Time Complexity Analysis](#time-complexity-analysis)

---

## Project Overview

This project is a **Legal Case Management System** that demonstrates the practical application of fundamental data structures in a real-world workflow management scenario. The system manages legal cases, client-lawyer relationships, appointments, and notifications using custom implementations of **Queues**, **Priority Queues**, **Stacks**, and **Hash Tables**.

### Tech Stack
| Component | Technology |
|-----------|------------|
| Backend | Python 3.x + Flask |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Data Storage | In-memory data structures |
| Architecture | RESTful API |

---

## Data Structures Implemented

### 1. Queue (FIFO - First In, First Out)
**Location:** `backend/data_structures.py` → `Queue` class

```python
class Queue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, item: Any) -> None:     # Add to back - O(1)
    def dequeue(self) -> Optional[Any]:        # Remove from front - O(n)*
    def peek(self) -> Optional[Any]:           # View front - O(1)
    def is_empty(self) -> bool:                # Check empty - O(1)
    def size(self) -> int:                     # Count items - O(1)
    def get_all(self) -> List[Any]:            # Get copy - O(n)
```

**Use Cases in the Project:**
| Feature | Why Queue? |
|---------|-----------|
| Normal Appointment Requests | First-come, first-served processing |
| Case Messages | Preserve chronological order |
| Follow-up Scheduling | Sequential scheduling |
| Notifications | Time-ordered display |

**Implementation Details:**
- Uses Python list as underlying storage
- `enqueue()` appends to end - O(1) amortized
- `dequeue()` removes from front using `pop(0)` - O(n) due to shifting
- Could be optimized using `collections.deque` for O(1) dequeue

---

### 2. Priority Queue
**Location:** `backend/data_structures.py` → `PriorityQueue` class

```python
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_counter = 0  # FIFO tiebreaker
    
    def enqueue(self, item: Any, priority: int) -> None:  # Add with priority - O(log n)
    def dequeue(self) -> Optional[Any]:                    # Get highest priority - O(log n)
    def peek(self) -> Optional[Any]:                       # View top - O(1)
    def is_empty(self) -> bool:                            # Check empty - O(1)
    def size(self) -> int:                                 # Count items - O(1)
    def get_all(self) -> List[Any]:                        # Get sorted - O(n log n)
```

**Use Cases in the Project:**
| Feature | Why Priority Queue? |
|---------|-------------------|
| Urgent Case Handling | Urgent cases processed before normal |
| Urgent Appointments | Jump ahead in queue |
| Available Cases Pool | Lawyers see urgent cases first |

**Implementation Details:**
- Uses Python's `heapq` module (min-heap)
- Entry format: `(priority, entry_counter, item)`
- Lower priority number = higher priority (1 = urgent, 2 = normal)
- `entry_counter` ensures FIFO ordering for same-priority items

---

### 3. Stack (LIFO - Last In, First Out)
**Location:** `backend/data_structures.py` → `Stack` class

```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item: Any) -> None:        # Add to top - O(1)
    def pop(self) -> Optional[Any]:           # Remove from top - O(1)
    def peek(self) -> Optional[Any]:          # View top - O(1)
    def is_empty(self) -> bool:               # Check empty - O(1)
    def size(self) -> int:                    # Count items - O(1)
    def clear(self) -> None:                  # Remove all - O(1)
```

**Use Cases in the Project:**
| Feature | Why Stack? |
|---------|-----------|
| Case Update Undo | Rollback last status change |
| State Preservation | Push before update, pop on undo |
| Legal Data Safety | Sensitive data mistakes can be reversed |

**Implementation Details:**
- Uses Python list as underlying storage
- All operations are O(1) using list's `append()` and `pop()`
- Each case has its own history stack: `case_history_stack[case_id] = Stack()`

---

### 4. Hash Tables
**Location:** `backend/data_structures.py` → `CaseStore`, `UserStore`, `DocumentStore` classes

```python
class CaseStore:
    def __init__(self):
        self.cases: Dict[str, Dict] = {}  # case_id → case data
    
    def add_case(case_id, case_data)       # Store - O(1)
    def get_case(case_id)                  # Retrieve - O(1)
    def update_case(case_id, updates)      # Update - O(1)
    def get_cases_by_client(client_id)     # Filter - O(n)
    def get_cases_by_lawyer(lawyer_id)     # Filter - O(n)

class UserStore:
    def __init__(self):
        self.users: Dict[str, Dict] = {}       # email → user data
        self.users_by_id: Dict[str, Dict] = {} # user_id → user data
    
    def add_user(user_id, email, user_data)    # Dual-indexed storage
    def get_user_by_email(email)               # O(1) lookup
    def get_user_by_id(user_id)                # O(1) lookup

class DocumentStore:
    def __init__(self):
        self.documents: Dict[str, Dict] = {}   # doc_id → metadata
    
    def add_document(doc_id, case_id, metadata)
    def get_document(doc_id)                    # O(1) lookup
    def get_documents_by_case(case_id)          # O(n) filter
```

**Use Cases in the Project:**
| Store | Purpose | Key → Value |
|-------|---------|------------|
| UserStore | Authentication & Profile | email → user data, user_id → user data |
| CaseStore | Case Management | case_id → case details |
| DocumentStore | Document Management | doc_id → file metadata |

**Implementation Details:**
- Uses Python's built-in `dict` (hash table implementation)
- O(1) average case for insert, lookup, delete
- Dual-indexed UserStore enables O(1) lookup by both email and ID

---

## Core Features

### 1. Case Ownership & Access Control
- Clients can only access their own cases
- Lawyers can only access assigned cases
- Role-based authorization at API level

### 2. Appointment Request Handling
```
Client Request → Queue (Normal) OR Priority Queue (Urgent) → Lawyer Processing
```
- Normal requests go to FIFO Queue
- Urgent requests go to Priority Queue
- Lawyers always see urgent requests first

### 3. Appointment Conflict Detection
- 60-minute buffer between appointments
- Automatic conflict checking before approval
- Prevents double-booking

### 4. Urgency-Based Case Handling
| Days Until Hearing | Urgency Level | Priority Score |
|-------------------|---------------|----------------|
| ≤ 7 days | Urgent | 0-7 |
| 8-14 days | High | 8-14 |
| > 14 days | Normal | 15+ |

### 5. Case Update with Undo (Stack-Based)
```python
# Before update: Push current state to stack
previous_state = {status, updates, updated_at}
case_history_stack[case_id].push(previous_state)

# To undo: Pop from stack and restore
previous_state = case_history_stack[case_id].pop()
case.status = previous_state.status
```

### 6. Case State Validation
Valid transitions enforced:
```
Created → In Review → Active → Closed
       ↘ Active
       ↘ Closed (direct completion)
```

### 7. Case-Bound Messaging
- Messages stored per case: `case_messages[case_id] = Queue()`
- Chronological ordering via Queue
- Only case participants can view

### 8. Document Access Control
- Documents linked to specific cases
- Access verified through case ownership

### 9. Follow-Up Scheduling
- Queue-based chronological scheduling
- Types: consultation, hearing

### 10. Notification System
- Per-user notification queues
- Types: new_case, appointment_request, message, document

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │   Client Portal     │    │   Lawyer Portal     │            │
│  │  - login.html       │    │  - login.html       │            │
│  │  - dashboard.html   │    │  - dashboard.html   │            │
│  │  - create-case.html │    │  - cases.html       │            │
│  │  - my-cases.html    │    │  - case-details.html│            │
│  │  - case-details.html│    │  - profile.html     │            │
│  │  - profile.html     │    │                     │            │
│  │  - signup.html      │    │                     │            │
│  └─────────────────────┘    └─────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask API)                          │
│                       app.py                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Manager Layer                          │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐   │  │
│  │  │CaseManager  │ │Appointment   │ │MessageManager   │   │  │
│  │  │             │ │Manager       │ │                 │   │  │
│  │  └─────────────┘ └──────────────┘ └─────────────────┘   │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐   │  │
│  │  │Document     │ │FollowUp      │ │Notification     │   │  │
│  │  │Manager      │ │Manager       │ │Manager          │   │  │
│  │  └─────────────┘ └──────────────┘ └─────────────────┘   │  │
│  │  ┌─────────────┐ ┌──────────────────────────────────┐   │  │
│  │  │EventManager │ │AvailableCasesPool               │   │  │
│  │  └─────────────┘ └──────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                Data Structures Layer                      │  │
│  │  ┌────────┐  ┌──────────────┐  ┌───────┐  ┌───────────┐ │  │
│  │  │ Queue  │  │PriorityQueue │  │ Stack │  │Hash Tables│ │  │
│  │  └────────┘  └──────────────┘  └───────┘  └───────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Data Stores                            │  │
│  │    UserStore      CaseStore      DocumentStore           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## How to Run the Application

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser

### Method 1: Manual Setup

```bash
# Step 1: Navigate to backend folder
cd backend

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Start the Flask server
python app.py
```

**Server will start at:** `http://localhost:5000`

```bash
# Step 4: Open the frontend
# For Clients: Open in browser
frontend/client/login.html

# For Lawyers: Open in browser  
frontend/lawyer/login.html
```

### Method 2: Using Docker (Recommended)

**Windows:**
```batch
start-docker.bat
```

**Linux/Mac:**
```bash
chmod +x start-docker.sh
./start-docker.sh
```

**Access Points:**
| Interface | URL |
|-----------|-----|
| Frontend | http://localhost:8000 |
| Backend API | http://localhost:5000/api |

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Client | a@gmail.com | password123 |
| Client | b@gmail.com | password123 |
| Client | c@gmail.com | password123 |
| Client | d@gmail.com | password123 |
| Client | e@gmail.com | password123 |
| Lawyer | a@lawfirm.com | password123 |
| Lawyer | b@lawfirm.com | password123 |
| Lawyer | c@lawfirm.com | password123 |
| Lawyer | d@lawfirm.com | password123 |
| Lawyer | e@lawfirm.com | password123 |

---

## API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login for clients and lawyers |
| POST | `/api/auth/signup` | Client registration |
| POST | `/api/auth/logout` | Logout current session |
| GET | `/api/auth/me` | Get current logged-in user |
| GET/PUT | `/api/profile` | Get or update user profile |

---

### Client Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/client/dashboard` | Get dashboard data (active cases, notifications) |
| GET | `/api/lawyers` | Get all lawyers with specialities and costs |
| GET | `/api/client/cases` | Get all client's cases |
| POST | `/api/client/cases` | Create a new case |
| GET | `/api/client/cases/<case_id>` | Get specific case details |
| POST | `/api/client/cases/<case_id>/appointments` | Request appointment |
| GET/POST | `/api/client/cases/<case_id>/messages` | Get or send messages |
| GET/POST | `/api/client/cases/<case_id>/documents` | Get or upload documents |

**Create Case Request Body:**
```json
{
  "case_type": "Civil Law",
  "description": "Detailed description (minimum 50 words)...",
  "hearing_date": "2025-02-15T10:00:00",
  "lawyer_id": "LAWYER-001",
  "speciality": "Civil Law"
}
```

---

### Lawyer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lawyer/dashboard` | Get dashboard (urgent cases, pending requests) |
| GET | `/api/lawyer/consultation-requests` | Get pending appointment requests |
| POST | `/api/lawyer/appointments/<id>/approve` | Approve appointment |
| POST | `/api/lawyer/appointments/<id>/reject` | Reject appointment |
| POST | `/api/lawyer/appointments/<id>/reschedule` | Reschedule appointment |
| GET | `/api/lawyer/cases` | Get all assigned cases |
| GET | `/api/lawyer/cases/<case_id>` | Get case details |
| POST | `/api/lawyer/cases/<case_id>/update` | Update case status |
| POST | `/api/lawyer/cases/<case_id>/undo` | Undo last update (Stack-based) |
| POST | `/api/lawyer/cases/<case_id>/followup` | Schedule follow-up |
| GET/POST | `/api/lawyer/cases/<case_id>/messages` | Get or send messages |

**Update Case Request Body:**
```json
{
  "status": "in_review",  // created, in_review, active, closed
  "notes": "Optional notes about the update"
}
```

---

### Available Cases Pool Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lawyer/available-cases` | Get available cases in pool |
| GET | `/api/lawyer/pending-requests` | Get direct assignment requests |
| POST | `/api/lawyer/cases/<case_id>/claim` | Claim case from pool |
| POST | `/api/lawyer/cases/<case_id>/unclaim` | Return case to pool |
| POST | `/api/lawyer/cases/<case_id>/accept-direct` | Accept direct request |
| POST | `/api/lawyer/cases/<case_id>/reject-direct` | Reject direct request |

---

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/queue-stats` | Get queue statistics |
| GET | `/api/analytics/urgency-distribution` | Get urgency distribution |

**Queue Stats Response:**
```json
{
  "normal_queue_length": 5,
  "urgent_queue_length": 2,
  "total_pending": 7
}
```

---

### Calendar Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/weekly` | Get all events for current week |
| POST | `/api/lawyer/cases/<case_id>/events` | Create hearing/appointment/follow-up |

---

## Testing the Data Structures

### 1. Test Queue (FIFO) Behavior

```
1. Login as client (a@gmail.com / password123)
2. Create 3 cases with different timestamps
3. Request appointments for all 3
4. Login as lawyer (a@lawfirm.com / password123)
5. Check consultation requests
✓ Verify: Requests appear in creation order (FIFO)
```

### 2. Test Priority Queue

```
1. Login as client
2. Create a case with hearing date within 7 days (urgent)
3. Create a case with hearing date > 14 days (normal)
4. Login as lawyer dashboard
✓ Verify: Urgent case appears before normal cases
```

### 3. Test Stack (Undo Functionality)

```
1. Login as lawyer
2. Go to an assigned case
3. Update status: created → in_review
4. Update status: in_review → active
5. Click "Undo Last Update"
✓ Verify: Status reverts to in_review (LIFO behavior)
```

### 4. Test Hash Table (O(1) Lookup)

```
1. Login with email (uses UserStore email lookup)
2. View a case by ID (uses CaseStore case_id lookup)
3. Access a document (uses DocumentStore doc_id lookup)
✓ Verify: All lookups are instantaneous
```

### 5. Test State Validation

```
1. Login as lawyer with an assigned case
2. Try invalid transition: created → closed (skip in_review)
✓ Verify: System rejects with error message
```

---

## Time Complexity Analysis

### Data Structure Operations

| Data Structure | Operation | Time Complexity |
|---------------|-----------|-----------------|
| **Queue** | enqueue | O(1) |
| | dequeue | O(n)* |
| | peek | O(1) |
| | is_empty | O(1) |
| **Priority Queue** | enqueue | O(log n) |
| | dequeue | O(log n) |
| | peek | O(1) |
| **Stack** | push | O(1) |
| | pop | O(1) |
| | peek | O(1) |
| **Hash Table** | insert | O(1) average |
| | lookup | O(1) average |
| | delete | O(1) average |

*Note: Queue dequeue is O(n) because Python list's `pop(0)` requires shifting elements. This could be optimized to O(1) using `collections.deque`.

### Manager Operations

| Manager | Operation | Complexity | Uses |
|---------|-----------|------------|------|
| CaseManager | create_case | O(1) | Hash Table |
| | check_access | O(1) | Hash Table |
| | update_case_status | O(1) | Hash Table + Stack |
| | undo_last_update | O(1) | Stack |
| AppointmentManager | request_appointment | O(1)/O(log n) | Queue/Priority Queue |
| | get_next_request | O(1)/O(log n) | Queue/Priority Queue |
| | check_conflict | O(m) | Linear search (m = appointments) |
| MessageManager | send_message | O(1) | Queue |
| | get_messages | O(n) | Queue (copy all) |
| NotificationManager | add_notification | O(1) | Queue |
| | get_notifications | O(n) | Queue (copy all) |

---

## Academic Value Summary

This project demonstrates practical application of:

1. **Queue (FIFO)** - Fair first-come-first-served processing
2. **Priority Queue** - Urgency-based prioritization with heap
3. **Stack (LIFO)** - Undo/rollback functionality
4. **Hash Table** - O(1) constant-time lookups

### Real-World Applicability
- Legal case management workflows
- Hospital patient queuing systems
- Customer service ticket management
- E-commerce order processing

---

## File Structure

```
law/
├── backend/
│   ├── data_structures.py    # ← Custom Queue, PriorityQueue, Stack, Hash Tables
│   ├── core_logic.py         # ← 10 core logic implementations using DS
│   ├── app.py                # ← Flask API server (51 endpoints)
│   └── requirements.txt
├── frontend/
│   ├── app.js                # Shared utilities
│   ├── styles.css            # Global styles
│   ├── client/               # Client interface (7 pages)
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── my-cases.html
│   │   ├── create-case.html
│   │   ├── case-details.html
│   │   └── profile.html
│   └── lawyer/               # Lawyer interface (6 pages)
│       ├── login.html
│       ├── dashboard.html
│       ├── cases.html
│       ├── case-details.html
│       ├── profile.html
│       └── calendar-grid.js
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── nginx.conf
├── start-docker.bat
├── start-docker.sh
└── README.md
```

---

**Built for demonstrating practical data structure applications in legal case management.**

*DSA Course Project - RVCE 3rd Semester*
