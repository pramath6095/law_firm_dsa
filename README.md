# Legal Case Management System

A comprehensive web-based system for managing legal cases, client relationships, and lawyer assignments with intelligent case prioritization and workflow control.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

The easiest way to run the application:

```bash
# Start the application
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d

# Stop the application
docker-compose down
```

**Access the application:**
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000/api

### Option 2: Manual Setup (Without Docker)

**Prerequisites:**
- Python 3.12+
- Modern web browser

**Steps:**

1. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   python app.py
   ```
   Backend will run at `http://localhost:5000`

3. **Serve the frontend:**
   
   You need a web server for the frontend. Use one of these:
   
   **Option A - Python HTTP Server:**
   ```bash
   cd frontend
   python -m http.server 8000
   ```
   
   **Option B - Node.js http-server:**
   ```bash
   npm install -g http-server
   cd frontend
   http-server -p 8000
   ```

4. **Access the application:**
   - Open http://localhost:8000 in your browser

---

## 🔐 Login & Demo Accounts

### Client Portal
🔗 **Login URL:** http://localhost:8000/client/login.html

**Sample Client Accounts:**
| Email | Password | Name |
|-------|----------|------|
| `a@gmail.com` | `password123` | John Doe |
| `b@gmail.com` | `password123` | Jane Smith |
| `c@gmail.com` | `password123` | Robert Brown |
| `d@gmail.com` | `password123` | Lisa Anderson |
| `e@gmail.com` | `password123` | Mark Wilson |

### Lawyer Portal
🔗 **Login URL:** http://localhost:8000/lawyer/login.html

**Sample Lawyer Accounts:**
| Email | Password | Name | Speciality | Cost/Hearing |
|-------|----------|------|------------|--------------|
| `a@lawfirm.com` | `password123` | Sarah Mitchell | Civil Law, Criminal Law | $5,000 |
| `b@lawfirm.com` | `password123` | David Chen | Civil Law, Criminal Law | $5,500 |
| `c@lawfirm.com` | `password123` | Emily Rodriguez | Family Law | $3,500 |
| `d@lawfirm.com` | `password123` | Michael Johnson | Corporate Law | $4,500 |
| `e@lawfirm.com` | `password123` | Priya Sharma | Property Law | $6,000 |

---

## 📋 Features

### For Clients
- ✅ Create and track legal cases
- ✅ Select preferred lawyers by specialization
- ✅ View case status and updates
- ✅ Communicate with assigned lawyer
- ✅ Weekly calendar view of hearings and appointments
- ✅ Upload case documents
- ✅ Track case urgency and priority

### For Lawyers
- ✅ Dashboard with urgent cases highlighted
- ✅ Manage assigned cases
- ✅ Update case status with undo functionality
- ✅ Schedule follow-ups and hearings
- ✅ Communicate with clients
- ✅ Weekly calendar with all events
- ✅ Case status breakdown analytics

---

## 🏗️ Architecture

### Tech Stack
- **Backend:** Python 3.12 + Flask
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Web Server:** Nginx (in Docker)
- **Data Storage:** In-memory 


### Data Structures Implementation

> **⚠️ PURE DSA IMPLEMENTATION**: All data structures are implemented **without built-in Python shortcuts** (no `append()`, `pop()`, `len()`, `heapq`, or `dict`). Manual index tracking and custom algorithms used throughout.

---

#### 1. **Stack (LIFO)** - Manual Top Index Tracking

**Used For:**
- Case status update undo functionality
- State preservation before updates

**Pure DSA Implementation:**
```python
class Stack:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.items = [None] * capacity  # Fixed-size array
        self.top = -1  # -1 indicates empty stack
    
    def push(self, item):
        """Add to top using index tracking"""
        if self.top >= self.capacity - 1:
            return False  # Overflow
        self.top = self.top + 1
        self.items[self.top] = item
        return True
    
    def pop(self):
        """Remove from top - NO built-in pop()"""
        if self.top == -1:
            return None  # Underflow
        item = self.items[self.top]
        self.items[self.top] = None
        self.top = self.top - 1
        return item
    
    def is_empty(self):
        """Check empty using top index - NO len()"""
        return self.top == -1
```

---

#### 2. **Queue (FIFO)** - Circular Array Implementation

**Used For:**
- Message ordering (chronological preservation)
- Notification delivery
- Follow-up scheduling

**Pure DSA Implementation:**
```python
class Queue:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.items = [None] * capacity  # Circular array
        self.front = -1
        self.rear = -1
        self.count = 0
    
    def enqueue(self, item):
        """Add to rear - NO append()"""
        if self.count >= self.capacity:
            return False
        if self.front == -1:
            self.front = 0
            self.rear = 0
        else:
            self.rear = (self.rear + 1) % self.capacity
        self.items[self.rear] = item
        self.count = self.count + 1
        return True
    
    def dequeue(self):
        """Remove from front - NO pop(0)"""
        if self.front == -1:
            return None
        item = self.items[self.front]
        self.items[self.front] = None
        self.count = self.count - 1
        if self.count == 0:
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity
        return item
```

---

#### 3. **Priority Queue** - Manual Heap with Heapify

**Used For:**
- Urgent case handling (cases with hearing ≤ 7 days)
- Automatic prioritization without manual sorting
- Available cases pool (lawyers see urgent cases first)

**Pure DSA Implementation:**
```python
class PriorityQueue:
    def __init__(self, capacity=1000):
        self.heap = [None] * capacity  # NO heapq module
        self.heap_size = 0
        self.entry_counter = 0
    
    def _parent(self, i): return (i - 1) // 2
    def _left(self, i): return 2 * i + 1
    def _right(self, i): return 2 * i + 2
    
    def _heapify_up(self, index):
        """Manual bubble up after insert"""
        while index > 0:
            parent = self._parent(index)
            if self.heap[index][0] < self.heap[parent][0]:
                # Manual swap
                temp = self.heap[index]
                self.heap[index] = self.heap[parent]
                self.heap[parent] = temp
                index = parent
            else:
                break
    
    def enqueue(self, item, priority):
        """Insert with manual heapify - NO heappush()"""
        entry = (priority, self.entry_counter, item)
        self.heap[self.heap_size] = entry
        self._heapify_up(self.heap_size)
        self.heap_size = self.heap_size + 1
        self.entry_counter = self.entry_counter + 1
```

---

#### 4. **Hash Table** - Custom Hash Function with Linked List Chaining

**Used For:**
- User authentication (email → user data)
- Case retrieval (case_id → case details)
- Document access (doc_id → document metadata)

**Pure DSA Implementation:**
```python
class Node:
    """Linked list node for chaining"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable:
    def __init__(self, size=101):
        self.size = size
        self.table = [None] * size  # NO Python dict
    
    def _hash(self, key):
        """Custom hash function - NO built-in hash()"""
        hash_value = 0
        position = 0
        for char in key:
            position = position + 1
            hash_value = hash_value + (ord(char) * position)
        return hash_value % self.size
    
    def put(self, key, value):
        """Insert with chaining - NO dict assignment"""
        index = self._hash(key)
        # Check if key exists (update)
        current = self.table[index]
        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next
        # Insert at head
        new_node = Node(key, value)
        new_node.next = self.table[index]
        self.table[index] = new_node
    
    def get(self, key):
        """Retrieve - NO dict.get()"""
        index = self._hash(key)
        current = self.table[index]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None
```

---

#### 5. **Bubble Sort** - Manual Urgency Sorting

**Used For:**
- Sorting cases by priority_score (days until hearing)
- Most urgent cases displayed first

**Pure DSA Implementation:**
```python
# Sort cases by urgency - NO built-in sort()
n = 0
for _ in cases:
    n = n + 1  # Manual length count

for i in range(n):
    for j in range(0, n - i - 1):
        score_j = cases[j].get('priority_score', 999)
        score_j1 = cases[j + 1].get('priority_score', 999)
        if score_j > score_j1:
            # Manual swap
            temp = cases[j]
            cases[j] = cases[j + 1]
            cases[j + 1] = temp
```

---

### Why These Data Structures?

| Data Structure | Why Chosen | Real-World Benefit |
|---------------|------------|-------------------|
| **Stack** | Legal data is sensitive - mistakes need reversibility | One-click undo for case updates |
| **Queue** | Messages and notifications need FIFO processing | Chronological order preserved |
| **Priority Queue** | Urgent cases need automatic prioritization | System enforces urgency, not manual sorting |
| **Hash Table** | Fast lookups critical for authentication & case access | O(1) instead of O(n) - instant retrieval |
| **Bubble Sort** | Display cases in urgency order | Most urgent cases shown first |

---

### Core Logic Components
1. Case ownership & access control
2. Intelligent lawyer assignment with auto-fallback
3. Urgency-based case prioritization
4. Case state validation (Created → In Review → Active → Closed)
5. Case-bound messaging system
6. Document management with access control
7. Follow-up scheduling
8. Notification system
9. Weekly calendar event management

---

## 📁 Project Structure

```
law/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── core_logic.py          # Business logic & managers
│   ├── data_structures.py     # Custom data structures
│   └── requirements.txt
├── frontend/
│   ├── app.js                 # Shared utilities & API client
│   ├── styles.css             # Global styles
│   ├── client/                # Client portal pages
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── my-cases.html
│   │   ├── create-case.html
│   │   ├── case-details.html
│   │   └── profile.html
│   └── lawyer/                # Lawyer portal pages
│       ├── login.html
│       ├── dashboard.html
│       ├── cases.html
│       ├── case-details.html
│       └── profile.html
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
└── README.md
```

---

## 🧪 Testing the System

### 1. Test as Client
1. Login at http://localhost:8000/client/login.html with `a@gmail.com` / `password123`
2. Create a new case from the dashboard
3. Select a lawyer and enter case details (minimum 50 words required)
4. View your case on the dashboard and calendar
5. Check case details and send messages to your lawyer

### 2. Test as Lawyer
1. Login at http://localhost:8000/lawyer/login.html with `a@lawfirm.com` / `password123`
2. View assigned cases on the dashboard
3. Click on a case to view details
4. Update case status
5. Schedule follow-ups and hearings
6. Send messages to clients
7. Test the undo functionality for case updates

### 3. Test Priority Queue
1. Create an urgent case (hearing date within 7 days)
2. Login as lawyer to see it appear in "Urgent Cases" section
3. Verify urgent cases are prioritized in the dashboard

---

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - Client registration
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Client Endpoints
- `GET /api/client/dashboard` - Dashboard data
- `GET /api/client/cases` - Get all client cases
- `POST /api/client/cases` - Create new case
- `GET /api/client/cases/:id` - Get case details

### Lawyer Endpoints
- `GET /api/lawyer/dashboard` - Dashboard data with urgent cases
- `GET /api/lawyer/cases` - Get assigned cases
- `GET /api/lawyer/cases/:id` - Get case details
- `POST /api/lawyer/cases/:id/update` - Update case status
- `POST /api/lawyer/cases/:id/undo` - Undo last update
- `POST /api/lawyer/cases/:id/followups` - Schedule follow-up

### Shared
- `GET /api/calendar/week` - Weekly calendar events
- `GET /api/lawyers` - List all lawyers with specializations

---

## 🐳 Docker Configuration

The application uses Docker Compose with two services:

- **Backend:** Flask app running on port 5000
- **Frontend:** Nginx serving static files on port 8000 with reverse proxy to backend

Nginx proxies `/api/*` requests to the backend, making all requests same-origin and eliminating CORS issues.

---

## ⚠️ Important Notes

### For Development/Demo Purposes Only
- **In-memory storage:** All data is lost when the server restarts
- **No password hashing:** Passwords stored in plain text
- **No file uploads:** Document uploads are simulated
- **Session-based auth:** Uses Flask sessions (not production-ready)

### Not Production Ready
This is a demonstrative application for learning purposes. For production:
- Implement database persistence (PostgreSQL/MySQL)
- Add password hashing (bcrypt)
- Implement JWT authentication
- Add proper file storage (S3/local storage)
- Add input validation and sanitization
- Implement rate limiting
- Add HTTPS/SSL
- Add logging and monitoring

---

## 🤝 Contributing

This is an educational project demonstrating legal case management with data structures and algorithms.

---

## 📄 License

MIT License - Free to use for educational purposes.

---

**Built with Flask, Vanilla JavaScript, and Docker** 🚀
