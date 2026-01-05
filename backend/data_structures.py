"""
Custom Data Structures for Legal Case Management System

This module implements core data structures from scratch to demonstrate
their practical application in workflow management.
"""

from datetime import datetime
import heapq
from typing import Any, Optional, List, Dict


class Queue:
    """
    FIFO Queue implementation for:
    - Normal appointment requests
    - Message ordering
    - Follow-up scheduling
    - Notifications
    """
    
    def __init__(self):
        self.items = []
    
    def enqueue(self, item: Any) -> None:
        """Add item to the back of the queue"""
        self.items.append(item)
    
    def dequeue(self) -> Optional[Any]:
        """Remove and return item from front of queue"""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def peek(self) -> Optional[Any]:
        """View front item without removing"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.items) == 0
    
    def size(self) -> int:
        """Return number of items in queue"""
        return len(self.items)
    
    def get_all(self) -> List[Any]:
        """Return all items (for viewing)"""
        return self.items.copy()


class PriorityQueue:
    """
    Priority Queue implementation for:
    - Urgent case handling
    - Urgent appointment requests
    
    Lower priority number = higher priority (1 is highest)
    """
    
    def __init__(self):
        self.heap = []
        self.entry_counter = 0  # For FIFO among same priority
    
    def enqueue(self, item: Any, priority: int) -> None:
        """
        Add item with priority
        Priority 1 = urgent, Priority 2 = normal
        """
        # Use counter to maintain FIFO for same priority
        entry = (priority, self.entry_counter, item)
        heapq.heappush(self.heap, entry)
        self.entry_counter += 1
    
    def dequeue(self) -> Optional[Any]:
        """Remove and return highest priority item"""
        if self.is_empty():
            return None
        priority, counter, item = heapq.heappop(self.heap)
        return item
    
    def peek(self) -> Optional[Any]:
        """View highest priority item without removing"""
        if self.is_empty():
            return None
        return self.heap[0][2]
    
    def is_empty(self) -> bool:
        """Check if priority queue is empty"""
        return len(self.heap) == 0
    
    def size(self) -> int:
        """Return number of items"""
        return len(self.heap)
    
    def get_all(self) -> List[Any]:
        """Return all items sorted by priority (for viewing)"""
        return [item for priority, counter, item in sorted(self.heap)]


class Stack:
    """
    LIFO Stack implementation for:
    - Case update undo functionality
    - Optional document upload undo
    """
    
    def __init__(self):
        self.items = []
    
    def push(self, item: Any) -> None:
        """Add item to top of stack"""
        self.items.append(item)
    
    def pop(self) -> Optional[Any]:
        """Remove and return item from top of stack"""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self) -> Optional[Any]:
        """View top item without removing"""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self) -> bool:
        """Check if stack is empty"""
        return len(self.items) == 0
    
    def size(self) -> int:
        """Return number of items"""
        return len(self.items)
    
    def clear(self) -> None:
        """Remove all items"""
        self.items = []


class CaseStore:
    """
    Hash Table wrapper for O(1) case lookups
    Key data structure for case ownership and access control
    """
    
    def __init__(self):
        self.cases: Dict[str, Dict] = {}
    
    def add_case(self, case_id: str, case_data: Dict) -> None:
        """Store case with unique ID"""
        self.cases[case_id] = case_data
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Retrieve case by ID"""
        return self.cases.get(case_id)
    
    def update_case(self, case_id: str, updates: Dict) -> bool:
        """Update case data"""
        if case_id in self.cases:
            self.cases[case_id].update(updates)
            return True
        return False
    
    def get_cases_by_client(self, client_id: str) -> List[Dict]:
        """Get all cases for a specific client"""
        return [
            case for case in self.cases.values()
            if case.get('client_id') == client_id
        ]
    
    def get_cases_by_lawyer(self, lawyer_id: str) -> List[Dict]:
        """Get all cases assigned to a specific lawyer"""
        return [
            case for case in self.cases.values()
            if case.get('lawyer_id') == lawyer_id
        ]
    
    def case_exists(self, case_id: str) -> bool:
        """Check if case exists"""
        return case_id in self.cases


class UserStore:
    """
    Hash Table wrapper for user (client/lawyer) data
    Email-based lookup for authentication
    """
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}  # email -> user data
        self.users_by_id: Dict[str, Dict] = {}  # user_id -> user data
    
    def add_user(self, user_id: str, email: str, user_data: Dict) -> None:
        """Store user with both email and ID lookups"""
        self.users[email] = user_data
        self.users_by_id[user_id] = user_data
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Retrieve user by email (for login)"""
        return self.users.get(email)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Retrieve user by ID"""
        return self.users_by_id.get(user_id)
    
    def email_exists(self, email: str) -> bool:
        """Check if email is already registered"""
        return email in self.users


class DocumentStore:
    """
    Hash Table for document metadata
    Links documents to cases with access control
    """
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}  # doc_id -> metadata
    
    def add_document(self, doc_id: str, case_id: str, metadata: Dict) -> None:
        """Store document metadata linked to case"""
        self.documents[doc_id] = {
            'case_id': case_id,
            **metadata
        }
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retrieve document metadata"""
        return self.documents.get(doc_id)
    
    def get_documents_by_case(self, case_id: str) -> List[Dict]:
        """Get all documents for a specific case"""
        return [
            doc for doc in self.documents.values()
            if doc.get('case_id') == case_id
        ]
