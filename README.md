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

This system implements custom data structures from scratch to demonstrate their practical application in legal workflow management.

#### 1. **Queue (FIFO)** - First In, First Out

**Used For:**
- Message ordering (chronological preservation)
- Notification delivery
- Follow-up scheduling

**Implementation:**
```python
class Queue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        """Add to back"""
        self.items.append(item)
    
    def dequeue(self):
        """Remove from front"""
        return self.items.pop(0)
```

**Usage Example (Messages):**
```python
class MessageManager:
    def __init__(self):
        self.case_messages = {}  # case_id -> Queue of messages
    
    def send_message(self, case_id, sender_id, content):
        if case_id not in self.case_messages:
            self.case_messages[case_id] = Queue()
        
        self.case_messages[case_id].enqueue({
            'sender_id': sender_id,
            'content': content,
            'timestamp': datetime.now()
        })
```

---

#### 2. **Priority Queue** - Priority-Based Processing

**Used For:**
- Urgent case handling (cases with hearing ≤ 7 days)
- Automatic prioritization without manual sorting
- Available cases pool (lawyers see urgent cases first)

**Implementation:**
```python
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_counter = 0
    
    def enqueue(self, item, priority):
        """Priority 1 = urgent, Priority 2 = normal"""
        entry = (priority, self.entry_counter, item)
        heapq.heappush(self.heap, entry)
        self.entry_counter += 1
    
    def dequeue(self):
        """Returns highest priority item first"""
        priority, counter, item = heapq.heappop(self.heap)
        return item
```

**Usage Example (Urgent Cases):**
```python
# Cases with hearing within 7 days automatically get urgency_level='urgent'
if days_until_hearing <= 7:
    case['urgency_level'] = 'urgent'
    case['priority_score'] = days_until_hearing  # Lower = more urgent

# Lawyer dashboard shows urgent cases first
urgent_cases = [c for c in cases if c['urgency_level'] == 'urgent']
urgent_cases.sort(key=lambda c: c['priority_score'])  # Sorted by priority
```

---

#### 3. **Stack (LIFO)** - Last In, First Out

**Used For:**
- Case status update undo functionality
- State preservation before updates

**Implementation:**
```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """Add to top"""
        self.items.append(item)
    
    def pop(self):
        """Remove from top"""
        return self.items.pop()
```

**Usage Example (Undo Case Updates):**
```python
class CaseManager:
    def __init__(self):
        self.case_history_stack = {}  # case_id -> Stack
    
    def update_case_status(self, case_id, new_status):
        case = self.case_store.get_case(case_id)
        
        # PUSH current state before update
        previous_state = {
            'status': case['status'],
            'updated_at': case['updated_at']
        }
        self.case_history_stack[case_id].push(previous_state)
        
        # Apply update
        case['status'] = new_status
    
    def undo_case_update(self, case_id):
        # POP last state to restore
        previous = self.case_history_stack[case_id].pop()
        case = self.case_store.get_case(case_id)
        case['status'] = previous['status']
        case['updated_at'] = previous['updated_at']
```

---

#### 4. **Hash Tables** - O(1) Lookups

**Used For:**
- User authentication (email → user data)
- Case retrieval (case_id → case details)
- Document access (doc_id → document metadata)

**Implementation:**
```python
class UserStore:
    def __init__(self):
        self.users = {}  # email -> user data (Hash Table)
        self.users_by_id = {}  # user_id -> user data
    
    def get_user_by_email(self, email):
        """O(1) lookup by email"""
        return self.users.get(email)
```

**Usage Example (Authentication):**
```python
@app.route('/api/auth/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    # O(1) hash table lookup instead of O(n) loop
    user = user_store.get_user_by_email(email)
    
    if user and user['password'] == password:
        session['user_id'] = user['user_id']
        return jsonify({'message': 'Login successful'})
```

**Case Store Example:**
```python
class CaseStore:
    def __init__(self):
        self.cases = {}  # case_id -> case_data (Hash Table)
    
    def get_case(self, case_id):
        """O(1) direct access instead of searching array"""
        return self.cases.get(case_id)
    
    def get_cases_by_lawyer(self, lawyer_id):
        """Filter from hash table values"""
        return [case for case in self.cases.values() 
                if case['lawyer_id'] == lawyer_id]
```

---

### Why These Data Structures?

| Data Structure | Why Chosen | Real-World Benefit |
|---------------|------------|-------------------|
| **Queue** | Messages and notifications need FIFO processing | Chronological order preserved |
| **Priority Queue** | Urgent cases need automatic prioritization | System enforces urgency, not manual sorting |
| **Stack** | Legal data is sensitive - mistakes need reversibility | One-click undo for case updates |
| **Hash Tables** | Fast lookups critical for authentication & case access | O(1) instead of O(n) - instant retrieval |

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
