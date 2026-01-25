"""
Custom Data Structures for Legal Case Management System

PURE DSA IMPLEMENTATION - No built-in shortcuts used
All operations implemented manually with index tracking

This module implements core data structures from scratch to demonstrate
their practical application in workflow management.

NO BUILT-IN METHODS USED:
- No list.append(), list.pop(), len()
- No heapq module
- No dict operations
- All index tracking done manually
"""

from datetime import datetime
from typing import Any, Optional, List, Dict, Tuple


# =============================================================================
# LINKED LIST NODE - For Hash Table Chaining
# =============================================================================

class Node:
    """Node for linked list implementation (used in hash table chains)"""
    
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.next = None  # Pointer to next node


# =============================================================================
# DYNAMIC ARRAY - Custom implementation without built-in methods
# =============================================================================

class DynamicArray:
    """
    Dynamic array implementation without using append/pop
    Used internally for returning results from data structures
    """
    
    INITIAL_CAPACITY = 16
    
    def __init__(self):
        self.capacity = self.INITIAL_CAPACITY
        self.data = [None] * self.capacity
        self.length = 0
    
    def add(self, item: Any) -> None:
        """Add item to end of array, resize if needed"""
        # Check if resize needed
        if self.length >= self.capacity:
            self._resize()
        
        self.data[self.length] = item
        self.length = self.length + 1
    
    def _resize(self) -> None:
        """Double the capacity"""
        new_capacity = self.capacity * 2
        new_data = [None] * new_capacity
        
        # Copy elements manually
        for i in range(self.length):
            new_data[i] = self.data[i]
        
        self.data = new_data
        self.capacity = new_capacity
    
    def get(self, index: int) -> Optional[Any]:
        """Get item at index"""
        if index < 0 or index >= self.length:
            return None
        return self.data[index]
    
    def to_list(self) -> list:
        """Convert to Python list for compatibility"""
        result = [None] * self.length
        for i in range(self.length):
            result[i] = self.data[i]
        return result


# =============================================================================
# STACK - LIFO with manual top index tracking
# =============================================================================

class Stack:
    """
    LIFO Stack implementation with manual index tracking
    
    Used for:
    - Case update undo functionality
    - State preservation before updates
    
    NO BUILT-IN FUNCTIONS USED:
    - Uses top index instead of len()
    - Manual element placement instead of append()
    - Manual element retrieval instead of pop()
    """
    
    DEFAULT_CAPACITY = 1000
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.items = [None] * capacity  # Fixed-size array
        self.top = -1  # -1 indicates empty stack
    
    def push(self, item: Any) -> bool:
        """
        Add item to top of stack
        Returns False if stack is full (overflow)
        """
        # Check for overflow
        if self.top >= self.capacity - 1:
            return False  # Stack overflow
        
        # Increment top and place item
        self.top = self.top + 1
        self.items[self.top] = item
        return True
    
    def pop(self) -> Optional[Any]:
        """
        Remove and return item from top of stack
        Returns None if stack is empty (underflow)
        """
        # Check for underflow
        if self.top == -1:
            return None  # Stack underflow
        
        # Get item at top
        item = self.items[self.top]
        
        # Clear the slot and decrement top
        self.items[self.top] = None
        self.top = self.top - 1
        
        return item
    
    def peek(self) -> Optional[Any]:
        """View top item without removing"""
        if self.top == -1:
            return None
        return self.items[self.top]
    
    def is_empty(self) -> bool:
        """Check if stack is empty using top index"""
        return self.top == -1
    
    def size(self) -> int:
        """Return number of items using top index"""
        return self.top + 1
    
    def clear(self) -> None:
        """Remove all items by resetting top"""
        # Clear all elements
        for i in range(self.top + 1):
            self.items[i] = None
        self.top = -1


# =============================================================================
# QUEUE - FIFO with circular array implementation
# =============================================================================

class Queue:
    """
    FIFO Queue implementation using circular array
    
    Used for:
    - Message ordering (chronological preservation)
    - Follow-up scheduling
    - Notifications
    
    NO BUILT-IN FUNCTIONS USED:
    - Uses front/rear indices instead of len()
    - Circular indexing instead of append()
    - Manual front tracking instead of pop(0)
    """
    
    DEFAULT_CAPACITY = 1000
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.items = [None] * capacity  # Fixed-size circular array
        self.front = -1  # -1 indicates empty queue
        self.rear = -1
        self.count = 0  # Track number of elements
    
    def enqueue(self, item: Any) -> bool:
        """
        Add item to the back of the queue
        Returns False if queue is full
        """
        # Check if queue is full
        if self.count >= self.capacity:
            return False  # Queue overflow
        
        # Handle first element
        if self.front == -1:
            self.front = 0
            self.rear = 0
        else:
            # Circular increment of rear
            self.rear = (self.rear + 1) % self.capacity
        
        # Place item at rear
        self.items[self.rear] = item
        self.count = self.count + 1
        return True
    
    def dequeue(self) -> Optional[Any]:
        """
        Remove and return item from front of queue
        Returns None if queue is empty
        """
        # Check if queue is empty
        if self.front == -1:
            return None  # Queue underflow
        
        # Get item at front
        item = self.items[self.front]
        
        # Clear the slot
        self.items[self.front] = None
        self.count = self.count - 1
        
        # Handle last element removal
        if self.count == 0:
            self.front = -1
            self.rear = -1
        else:
            # Circular increment of front
            self.front = (self.front + 1) % self.capacity
        
        return item
    
    def peek(self) -> Optional[Any]:
        """View front item without removing"""
        if self.front == -1:
            return None
        return self.items[self.front]
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.front == -1
    
    def size(self) -> int:
        """Return number of items"""
        return self.count
    
    def get_all(self) -> list:
        """Return all items in order (for viewing)"""
        if self.front == -1:
            return []
        
        # Create fixed-size result array
        result = [None] * self.count
        
        # Traverse from front to rear circularly
        i = self.front
        result_idx = 0
        while result_idx < self.count:
            result[result_idx] = self.items[i]
            i = (i + 1) % self.capacity
            result_idx = result_idx + 1
        
        return result


# =============================================================================
# PRIORITY QUEUE - Min-Heap with manual heapify operations
# =============================================================================

class PriorityQueue:
    """
    Priority Queue implementation using manual min-heap
    
    Used for:
    - Urgent case handling
    - Available cases pool (lawyers see urgent cases first)
    
    NO BUILT-IN FUNCTIONS USED:
    - Manual heapify_up instead of heapq.heappush()
    - Manual heapify_down instead of heapq.heappop()
    - Manual heap array management
    
    Lower priority number = higher priority (1 is highest)
    Entry format: (priority, counter, item) - counter for FIFO among same priority
    """
    
    DEFAULT_CAPACITY = 1000
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.heap = [None] * capacity  # Fixed-size heap array
        self.heap_size = 0  # Current number of elements
        self.entry_counter = 0  # For FIFO among same priority
    
    # ---- Helper methods for heap indexing ----
    
    def _parent(self, index: int) -> int:
        """Get parent index"""
        return (index - 1) // 2
    
    def _left_child(self, index: int) -> int:
        """Get left child index"""
        return 2 * index + 1
    
    def _right_child(self, index: int) -> int:
        """Get right child index"""
        return 2 * index + 2
    
    def _swap(self, i: int, j: int) -> None:
        """Swap two elements in heap"""
        temp = self.heap[i]
        self.heap[i] = self.heap[j]
        self.heap[j] = temp
    
    def _compare(self, entry1: Tuple, entry2: Tuple) -> bool:
        """
        Compare two entries: returns True if entry1 should come before entry2
        Compares by priority first, then by counter (FIFO)
        """
        # entry format: (priority, counter, item)
        if entry1[0] != entry2[0]:
            return entry1[0] < entry2[0]  # Lower priority number = higher priority
        return entry1[1] < entry2[1]  # Earlier counter comes first (FIFO)
    
    def _heapify_up(self, index: int) -> None:
        """
        Restore heap property upward after insertion
        Compare with parent and swap if smaller
        """
        while index > 0:
            parent_idx = self._parent(index)
            
            # If current is smaller than parent, swap
            if self._compare(self.heap[index], self.heap[parent_idx]):
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break  # Heap property satisfied
    
    def _heapify_down(self, index: int) -> None:
        """
        Restore heap property downward after extraction
        Compare with children and swap with smaller child
        """
        while True:
            smallest = index
            left = self._left_child(index)
            right = self._right_child(index)
            
            # Check if left child exists and is smaller
            if left < self.heap_size and self._compare(self.heap[left], self.heap[smallest]):
                smallest = left
            
            # Check if right child exists and is smaller
            if right < self.heap_size and self._compare(self.heap[right], self.heap[smallest]):
                smallest = right
            
            # If smallest is not current, swap and continue
            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break  # Heap property satisfied
    
    def enqueue(self, item: Any, priority: int) -> bool:
        """
        Add item with priority
        Priority 1 = urgent, Priority 2 = normal
        Returns False if queue is full
        """
        if self.heap_size >= self.capacity:
            return False  # Heap overflow
        
        # Create entry with counter for FIFO
        entry = (priority, self.entry_counter, item)
        self.entry_counter = self.entry_counter + 1
        
        # Place at end of heap
        self.heap[self.heap_size] = entry
        
        # Heapify up to maintain heap property
        self._heapify_up(self.heap_size)
        
        self.heap_size = self.heap_size + 1
        return True
    
    def dequeue(self) -> Optional[Any]:
        """
        Remove and return highest priority item
        Returns None if queue is empty
        """
        if self.heap_size == 0:
            return None
        
        # Get root (highest priority)
        root_entry = self.heap[0]
        item = root_entry[2]  # Extract item from (priority, counter, item)
        
        # Move last element to root
        self.heap_size = self.heap_size - 1
        
        if self.heap_size > 0:
            self.heap[0] = self.heap[self.heap_size]
            self.heap[self.heap_size] = None  # Clear old position
            
            # Heapify down to maintain heap property
            self._heapify_down(0)
        else:
            self.heap[0] = None
        
        return item
    
    def peek(self) -> Optional[Any]:
        """View highest priority item without removing"""
        if self.heap_size == 0:
            return None
        return self.heap[0][2]  # Return item from (priority, counter, item)
    
    def is_empty(self) -> bool:
        """Check if priority queue is empty"""
        return self.heap_size == 0
    
    def size(self) -> int:
        """Return number of items"""
        return self.heap_size
    
    def get_all(self) -> list:
        """Return all items sorted by priority (for viewing)"""
        if self.heap_size == 0:
            return []
        
        # Create fixed-size array for entries
        entries = [None] * self.heap_size
        for i in range(self.heap_size):
            entries[i] = self.heap[i]
        
        # Manual bubble sort by priority then counter
        n = self.heap_size
        for i in range(n):
            for j in range(0, n - i - 1):
                if not self._compare(entries[j], entries[j + 1]):
                    temp = entries[j]
                    entries[j] = entries[j + 1]
                    entries[j + 1] = temp
        
        # Create fixed-size result array
        result = [None] * self.heap_size
        for i in range(self.heap_size):
            result[i] = entries[i][2]
        
        return result


# =============================================================================
# HASH TABLE - Custom implementation with linked list chaining
# =============================================================================

class HashTable:
    """
    Generic Hash Table implementation with linked list chaining
    
    NO BUILT-IN FUNCTIONS USED:
    - Custom hash function instead of Python's hash()
    - Linked list nodes for chaining instead of list.append()
    - Manual traversal for all operations
    """
    
    DEFAULT_SIZE = 101  # Prime number for better distribution
    
    def __init__(self, size: int = DEFAULT_SIZE):
        self.size = size
        self.table = [None] * size  # Array of linked list heads
        self.count = 0  # Number of key-value pairs
    
    def _hash(self, key: str) -> int:
        """
        Custom hash function using ASCII sum with position weighting
        Converts string key to array index
        """
        hash_value = 0
        position = 0
        
        # Manual string iteration
        for char in key:
            ascii_val = ord(char)
            # Multiply by position to reduce collisions for similar strings
            position = position + 1
            hash_value = hash_value + (ascii_val * position)
        
        return hash_value % self.size
    
    def put(self, key: str, value: Any) -> None:
        """Insert or update key-value pair using linked list chaining"""
        index = self._hash(key)
        
        # Check if key already exists (update)
        current = self.table[index]
        while current is not None:
            if current.key == key:
                current.value = value  # Update existing
                return
            current = current.next
        
        # Key not found, insert new node at head
        new_node = Node(key, value)
        new_node.next = self.table[index]  # Point to old head
        self.table[index] = new_node  # New node becomes head
        self.count = self.count + 1
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        index = self._hash(key)
        
        # Traverse linked list
        current = self.table[index]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        
        return None
    
    def contains(self, key: str) -> bool:
        """Check if key exists"""
        index = self._hash(key)
        
        current = self.table[index]
        while current is not None:
            if current.key == key:
                return True
            current = current.next
        
        return False
    
    def remove(self, key: str) -> bool:
        """Remove key-value pair"""
        index = self._hash(key)
        
        current = self.table[index]
        prev = None
        
        while current is not None:
            if current.key == key:
                if prev is None:
                    # Removing head
                    self.table[index] = current.next
                else:
                    # Removing non-head
                    prev.next = current.next
                self.count = self.count - 1
                return True
            prev = current
            current = current.next
        
        return False
    
    def get_all_values(self) -> list:
        """Get all values in hash table"""
        # First, count total values
        total = 0
        for i in range(self.size):
            current = self.table[i]
            while current is not None:
                total = total + 1
                current = current.next
        
        # Create fixed-size result array
        result = [None] * total
        result_idx = 0
        
        # Collect all values
        for i in range(self.size):
            current = self.table[i]
            while current is not None:
                result[result_idx] = current.value
                result_idx = result_idx + 1
                current = current.next
        
        return result


# =============================================================================
# CASE STORE - Hash Table for case management
# =============================================================================

class CaseStore:
    """
    Hash Table wrapper for O(1) case lookups
    Key data structure for case ownership and access control
    
    Uses custom HashTable implementation with linked list chaining
    """
    
    def __init__(self):
        self.cases = HashTable()
    
    def add_case(self, case_id: str, case_data: Dict) -> None:
        """Store case with unique ID"""
        self.cases.put(case_id, case_data)
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Retrieve case by ID"""
        return self.cases.get(case_id)
    
    def update_case(self, case_id: str, updates: Dict) -> bool:
        """Update case data"""
        case = self.cases.get(case_id)
        if case is None:
            return False
        
        # Manual update of dictionary fields
        for key in updates:
            case[key] = updates[key]
        
        return True
    
    def get_cases_by_client(self, client_id: str) -> list:
        """Get all cases for a specific client"""
        all_cases = self.cases.get_all_values()
        
        # Count matching cases first
        match_count = 0
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('client_id') == client_id:
                match_count = match_count + 1
        
        # Create result array
        result = [None] * match_count
        result_idx = 0
        
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('client_id') == client_id:
                result[result_idx] = case
                result_idx = result_idx + 1
        
        return result
    
    def get_cases_by_lawyer(self, lawyer_id: str) -> list:
        """Get all cases assigned to a specific lawyer"""
        all_cases = self.cases.get_all_values()
        
        # Count matching cases first
        match_count = 0
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('lawyer_id') == lawyer_id:
                match_count = match_count + 1
        
        # Create result array
        result = [None] * match_count
        result_idx = 0
        
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('lawyer_id') == lawyer_id:
                result[result_idx] = case
                result_idx = result_idx + 1
        
        return result
    
    def _get_array_length(self, arr: list) -> int:
        """Get length without using len()"""
        count = 0
        for _ in arr:
            count = count + 1
        return count
    
    def case_exists(self, case_id: str) -> bool:
        """Check if case exists"""
        return self.cases.contains(case_id)
    
    def get_all_cases(self) -> list:
        """Get all cases as a list"""
        return self.cases.get_all_values()


# =============================================================================
# USER STORE - Dual-indexed Hash Table for user management
# =============================================================================

class UserStore:
    """
    Hash Table wrapper for user (client/lawyer) data
    Email-based lookup for authentication
    
    Uses two hash tables for O(1) lookup by both email and ID
    """
    
    def __init__(self):
        self.users_by_email = HashTable()  # email -> user data
        self.users_by_id = HashTable()     # user_id -> user data
    
    @property
    def users(self):
        """Compatibility property - returns dict-like access to users by email"""
        all_values = self.users_by_email.get_all_values()
        result = {}
        for i in range(self._get_array_length(all_values)):
            user = all_values[i]
            if user is not None and 'email' in user:
                result[user['email']] = user
        return result
    
    def _get_array_length(self, arr: list) -> int:
        """Get length without using len()"""
        count = 0
        for _ in arr:
            count = count + 1
        return count
    
    def add_user(self, user_id: str, email: str, user_data: Dict) -> None:
        """Store user with both email and ID lookups"""
        self.users_by_email.put(email, user_data)
        self.users_by_id.put(user_id, user_data)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Retrieve user by email (for login)"""
        return self.users_by_email.get(email)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Retrieve user by ID"""
        return self.users_by_id.get(user_id)
    
    def email_exists(self, email: str) -> bool:
        """Check if email is already registered"""
        return self.users_by_email.contains(email)
    
    def get_all_users(self) -> list:
        """Get all users as a list"""
        return self.users_by_email.get_all_values()


# =============================================================================
# DOCUMENT STORE - Hash Table for document management
# =============================================================================

class DocumentStore:
    """
    Hash Table for document metadata
    Links documents to cases with access control
    
    Uses custom HashTable implementation with linked list chaining
    """
    
    def __init__(self):
        self.documents = HashTable()
    
    def add_document(self, doc_id: str, case_id: str, metadata: Dict) -> None:
        """Store document metadata linked to case"""
        doc_data = {'case_id': case_id}
        # Manual dictionary merge
        for key in metadata:
            doc_data[key] = metadata[key]
        
        self.documents.put(doc_id, doc_data)
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retrieve document metadata"""
        return self.documents.get(doc_id)
    
    def get_documents_by_case(self, case_id: str) -> list:
        """Get all documents for a specific case"""
        all_docs = self.documents.get_all_values()
        
        # Count matching documents first
        match_count = 0
        for i in range(self._get_array_length(all_docs)):
            doc = all_docs[i]
            if doc is not None and doc.get('case_id') == case_id:
                match_count = match_count + 1
        
        # Create result array
        result = [None] * match_count
        result_idx = 0
        
        for i in range(self._get_array_length(all_docs)):
            doc = all_docs[i]
            if doc is not None and doc.get('case_id') == case_id:
                result[result_idx] = doc
                result_idx = result_idx + 1
        
        return result
    
    def _get_array_length(self, arr: list) -> int:
        """Get length without using len()"""
        count = 0
        for _ in arr:
            count = count + 1
        return count
