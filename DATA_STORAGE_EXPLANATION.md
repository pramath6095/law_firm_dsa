# 📦 Data Storage Explanation

This document explains **what data each data structure stores** and **how it stores that data** in the Legal Case Management System.

---

## Table of Contents
1. [Node (Linked List)](#1-node-linked-list)
2. [Dynamic Array](#2-dynamic-array)
3. [Stack](#3-stack)
4. [Queue](#4-queue)
5. [Priority Queue](#5-priority-queue)
6. [Hash Table](#6-hash-table)
7. [Application-Level Stores](#7-application-level-stores)

---

## 1. Node (Linked List)

### What It Stores
| Field | Data Type | Description |
|-------|-----------|-------------|
| `key` | `str` (String) | A unique identifier/name for the data |
| `value` | `Any` (Any type) | The actual data being stored (can be dict, string, number, etc.) |
| `next` | `Node` or `None` | Pointer to the next node in the chain |

### How It Stores
```
Node Structure:
┌──────────────────────────────────────────┐
│  key: "user@email.com"                   │
│  value: {name: "John", role: "client"}   │
│  next: ────────────────────────────────► │ → (points to next Node or None)
└──────────────────────────────────────────┘
```

**Storage Mechanism:**
- Used in **Hash Table chaining** to handle collisions
- Each node holds a key-value pair
- Nodes form a **singly linked list** within each hash bucket

---

## 2. Dynamic Array

### What It Stores
| Field | Data Type | Description |
|-------|-----------|-------------|
| `data` | `list[Any]` | Fixed-size array holding elements of any type |
| `length` | `int` (Integer) | Current number of elements stored |
| `capacity` | `int` (Integer) | Maximum current capacity before resize |

### How It Stores
```
Initial State (capacity = 16):
┌─────┬─────┬─────┬─────┬─────┬─────┬──────────────┐
│  0  │  1  │  2  │ ... │ ... │ ... │     None     │
└─────┴─────┴─────┴─────┴─────┴─────┴──────────────┘
  ↑                           ↑
  index 0                     index 15

After adding items:
┌─────────┬─────────┬─────────┬──────┬──────┬──────┐
│ "case1" │ "case2" │ "case3" │ None │ None │ None │
└─────────┴─────────┴─────────┴──────┴──────┴──────┘
  length = 3, capacity = 16
```

**Storage Mechanism:**
- Pre-allocates array with initial capacity of **16**
- Tracks `length` separately (doesn't use `len()`)
- **Doubles capacity** when full (16 → 32 → 64...)
- Elements can be **any type**: strings, numbers, objects, etc.

---

## 3. Stack

### What It Stores
| Field | Data Type | Description |
|-------|-----------|-------------|
| `items` | `list[Any]` | Fixed-size array (default 1000 slots) |
| `top` | `int` (Integer) | Index of the top element (-1 = empty) |
| `capacity` | `int` (Integer) | Maximum stack size |

### What Data Is Actually Pushed
In this project, the Stack stores **case history states** (dictionaries):

```python
# Each item pushed is a dictionary containing:
{
    "status": "in_review",           # String - previous case status
    "updates": "Reviewed documents", # String - update notes  
    "updated_at": "2025-01-27T10:30" # String - timestamp
}
```

### How It Stores
```
Stack Visualization (LIFO):
                    ┌─────────────────────────────┐
         top → 2    │ {status:"active", ...}      │  ← Last In, First Out
                    ├─────────────────────────────┤
                1   │ {status:"in_review", ...}   │
                    ├─────────────────────────────┤
                0   │ {status:"created", ...}     │  ← First element
                    └─────────────────────────────┘

items[0] = {status: "created", ...}
items[1] = {status: "in_review", ...}
items[2] = {status: "active", ...}    ← top points here
items[3..999] = None                  ← unused slots
```

**Storage Mechanism:**
- Uses `top` index instead of `len()`
- **Push:** Increment `top`, place item at `items[top]`
- **Pop:** Read `items[top]`, clear slot, decrement `top`
- Checks for **overflow** (top >= capacity-1) and **underflow** (top == -1)

---

## 4. Queue

### What It Stores
| Field | Data Type | Description |
|-------|-----------|-------------|
| `items` | `list[Any]` | Circular array (default 1000 slots) |
| `front` | `int` (Integer) | Index of first element (-1 = empty) |
| `rear` | `int` (Integer) | Index of last element |
| `count` | `int` (Integer) | Number of elements in queue |

### What Data Is Actually Enqueued
In this project, the Queue stores **messages** and **notifications** (dictionaries):

```python
# Message queued:
{
    "id": "MSG-001",                 # String - unique ID
    "case_id": "CASE-001",           # String - related case
    "sender_id": "USER-123",         # String - who sent it
    "sender_name": "John Doe",       # String - display name
    "sender_role": "client",         # String - client/lawyer
    "content": "Please review...",   # String - message text
    "timestamp": "2025-01-27T10:30"  # String - when sent
}

# Notification queued:
{
    "id": "NOTIF-001",               # String - unique ID
    "type": "new_case",              # String - notification type
    "message": "New case assigned",  # String - display text
    "timestamp": "2025-01-27T10:30", # String - when created
    "case_id": "CASE-001"            # String (optional) - related case
}
```

### How It Stores
```
Circular Queue Visualization (FIFO):
                capacity = 8

    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │ msg │ msg │ msg │ msg │None │None │None │None │
    │  1  │  2  │  3  │  4  │     │     │     │     │
    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
      ↑                 ↑
    front=0           rear=3
    
    count = 4

After dequeue (remove msg1):
    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │None │ msg │ msg │ msg │None │None │None │None │
    │     │  2  │  3  │  4  │     │     │     │     │
    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
            ↑           ↑
          front=1     rear=3
```

**Storage Mechanism:**
- **Circular array:** `rear = (rear + 1) % capacity`
- **Enqueue:** Move `rear` forward, place item
- **Dequeue:** Read `items[front]`, move `front` forward
- Avoids wasted space by wrapping around

---

## 5. Priority Queue

### What It Stores
| Field | Data Type | Description |
|-------|-----------|-------------|
| `heap` | `list[Tuple]` | Array storing tuples (priority, counter, item) |
| `heap_size` | `int` (Integer) | Number of elements in heap |
| `entry_counter` | `int` (Integer) | For FIFO ordering of same-priority items |

### Entry Format
```python
# Each entry in the heap is a tuple:
(priority, counter, item)

# Example:
(1, 0, case_data)   # Priority 1 (urgent), inserted first
(1, 1, case_data)   # Priority 1 (urgent), inserted second
(2, 2, case_data)   # Priority 2 (normal), inserted third
```

### What Data Is Actually Stored
In this project, the Priority Queue holds **case data** (dictionaries):

```python
# The "item" in (priority, counter, item) is:
{
    "id": "CASE-001",                # String - unique case ID
    "client_id": "CLIENT-123",       # String - client reference
    "lawyer_id": None,               # String or None - assigned lawyer
    "case_type": "Criminal Law",     # String - specialization
    "description": "...",            # String - case details
    "status": "created",             # String - current status
    "urgency_level": "urgent",       # String - urgent/high/normal
    "priority_score": 5,             # Integer - days until hearing
    "hearing_date": "2025-02-01",    # String - date of hearing
    "created_at": "2025-01-27"       # String - creation date
}
```

### How It Stores
```
Min-Heap Visualization (Lower priority number = Higher priority):

                    (1, 0, case_A)      ← Root (highest priority)
                   /              \
          (1, 1, case_B)      (2, 2, case_C)
              /      \
     (2, 3, case_D)  (2, 4, case_E)

Array representation:
┌────────────────┬────────────────┬────────────────┬────────────────┬────────────────┐
│ (1,0,case_A)   │ (1,1,case_B)   │ (2,2,case_C)   │ (2,3,case_D)   │ (2,4,case_E)   │
└────────────────┴────────────────┴────────────────┴────────────────┴────────────────┘
  index 0           index 1          index 2          index 3          index 4
```

**Storage Mechanism:**
- Uses **array-based min-heap**
- Parent index: `(i - 1) // 2`
- Left child: `2 * i + 1`
- Right child: `2 * i + 2`
- **Heapify up** after insertion
- **Heapify down** after extraction
- `entry_counter` ensures FIFO for equal priorities

---

## 6. Hash Table

### What It Stores
| Field | Data Type | Description |
|-------|-----------|-------------|
| `table` | `list[Node]` | Array of linked list heads (size 101) |
| `size` | `int` (Integer) | Number of buckets |
| `count` | `int` (Integer) | Total key-value pairs stored |

### What Data Is Stored
The Hash Table stores **key-value pairs** where:
- **Key:** Always a `string` (case_id, email, doc_id)
- **Value:** Any type, but usually a `dictionary` with the actual data

```python
# Keys and Values:
"CASE-001" → {id, client_id, status, ...}    # case data
"user@email.com" → {id, name, email, ...}    # user data
"DOC-001" → {id, case_id, filename, ...}     # document metadata
```

### How It Stores
```
Hash Table with Chaining:

table[0]: None
table[1]: None
table[2]: ┌─────────────────┐
          │ key: "CASE-003" │ → None
          │ value: {...}    │
          └─────────────────┘
table[3]: None
  ...
table[47]: ┌─────────────────┐    ┌─────────────────┐
           │ key: "CASE-001" │ → │ key: "CASE-056" │ → None
           │ value: {...}    │    │ value: {...}    │
           └─────────────────┘    └─────────────────┘
           (collision: both hash to index 47)
  ...
table[100]: None
```

**Hash Function:**
```python
def _hash(key: str) -> int:
    hash_value = 0
    position = 0
    for char in key:
        position += 1
        hash_value += ord(char) * position  # ASCII weighted by position
    return hash_value % table_size
```

**Storage Mechanism:**
- Uses **linked list chaining** for collisions
- New nodes inserted at **head** of chain
- Lookup traverses chain comparing keys
- Prime table size (101) reduces collisions

---

## 7. Application-Level Stores

### CaseStore

**Wraps:** Hash Table  
**Key Type:** `str` (case_id like "CASE-001")  
**Value Type:** `dict` (case data)

```python
# Stored case data structure:
{
    "id": "CASE-001",                    # String
    "client_id": "CLIENT-123",           # String
    "client_name": "John Doe",           # String
    "lawyer_id": "LAWYER-456",           # String or None
    "lawyer_name": "Jane Smith",         # String or None
    "case_type": "Criminal Law",         # String
    "description": "Detailed case...",   # String
    "status": "active",                  # String (created/in_review/active/closed)
    "urgency_level": "urgent",           # String (urgent/high/normal)
    "priority_score": 5,                 # Integer (0-14 urgent, 15+ normal)
    "hearing_date": "2025-02-01",        # String (ISO date)
    "created_at": "2025-01-27T10:30:00", # String (ISO datetime)
    "updates": "Latest notes..."         # String (optional)
}
```

---

### UserStore

**Wraps:** Two Hash Tables (dual-indexed)  
**Key Types:** `str` (email) and `str` (user_id)  
**Value Type:** `dict` (user data, shared between both tables)

```python
# Stored user data structure:
{
    "id": "USER-001",                    # String
    "email": "user@email.com",           # String
    "password": "hashed_password",       # String
    "name": "John Doe",                  # String
    "phone": "+1234567890",              # String
    "role": "client",                    # String (client/lawyer)
    "speciality": "Criminal Law",        # String (lawyers only)
    "hourly_rate": 150,                  # Integer (lawyers only)
    "is_active": true,                   # Boolean
    "created_at": "2025-01-01T00:00:00"  # String (ISO datetime)
}
```

**Dual-Index Storage:**
```
users_by_email["user@email.com"] ─────┐
                                      ├──► Same dict object
users_by_id["USER-001"] ──────────────┘
```

---

### DocumentStore

**Wraps:** Hash Table  
**Key Type:** `str` (doc_id like "DOC-001")  
**Value Type:** `dict` (document metadata)

```python
# Stored document metadata:
{
    "id": "DOC-001",                     # String
    "case_id": "CASE-001",               # String (links to case)
    "filename": "contract.pdf",          # String
    "file_path": "/uploads/...",         # String
    "file_size": 512000,                 # Integer (bytes)
    "mime_type": "application/pdf",      # String
    "uploaded_by": "CLIENT-123",         # String
    "uploaded_at": "2025-01-27T10:30"    # String (ISO datetime)
}
```

---

## Summary Table

| Data Structure | What It Stores | Data Types Stored |
|----------------|----------------|-------------------|
| **Stack** | Case history states | `dict` with status, updates, timestamp (all strings) |
| **Queue** | Messages & notifications | `dict` with id, content, sender info (strings) |
| **Priority Queue** | Urgent/normal cases | `tuple(int, int, dict)` - priority, counter, case data |
| **Hash Table** | Key-value mappings | Key: `str`, Value: `dict` (users, cases, documents) |
| **Node** | Linked list entries | Key: `str`, Value: `Any`, Next: `Node` pointer |
| **Dynamic Array** | Generic collections | `Any` type elements |

---

## Visual Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW IN THE SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Client Creates Case                                                    │
│        ↓                                                                │
│  ┌─────────────────────┐                                               │
│  │    HASH TABLE       │  ← Stores case data (dict)                    │
│  │    (CaseStore)      │    Key: "CASE-001" (string)                   │
│  └────────┬────────────┘                                               │
│           ↓                                                             │
│  ┌─────────────────────┐                                               │
│  │   PRIORITY QUEUE    │  ← Stores (priority, counter, case)           │
│  │  (AvailableCases)   │    Priority: integer (1=urgent, 2=normal)     │
│  └────────┬────────────┘                                               │
│           ↓                                                             │
│  Lawyer Claims & Updates Case                                           │
│           ↓                                                             │
│  ┌─────────────────────┐                                               │
│  │       STACK         │  ← Stores previous states (dicts)             │
│  │  (Case History)     │    Each: {status, updates, timestamp}         │
│  └────────┬────────────┘                                               │
│           ↓                                                             │
│  Client/Lawyer Send Messages                                            │
│           ↓                                                             │
│  ┌─────────────────────┐                                               │
│  │       QUEUE         │  ← Stores messages (dicts)                    │
│  │  (Case Messages)    │    Each: {id, content, sender, timestamp}     │
│  └─────────────────────┘                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

**Key Insight:** All data structures in this system ultimately store **dictionaries** containing **strings, integers, and booleans**. The data structures themselves just provide different **access patterns** (LIFO, FIFO, priority-based, or O(1) key lookup).
