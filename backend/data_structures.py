
from datetime import datetime
from typing import Any, Optional, List, Dict, Tuple


class Node:
    """Linked list node for hash table chaining"""
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.next = None


class DynamicArray:
    """Dynamic array without using append/pop"""
    
    INITIAL_CAPACITY = 16
    
    def __init__(self):
        self.capacity = self.INITIAL_CAPACITY
        self.data = [None] * self.capacity
        self.length = 0
    
    def add(self, item: Any) -> None:
        if self.length >= self.capacity:
            self._resize()
        self.data[self.length] = item
        self.length = self.length + 1
    
    def _resize(self) -> None:
        new_capacity = self.capacity * 2
        new_data = [None] * new_capacity
        for i in range(self.length):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity
    
    def get(self, index: int) -> Optional[Any]:
        if index < 0 or index >= self.length:
            return None
        return self.data[index]
    
    def to_list(self) -> list:
        result = [None] * self.length
        for i in range(self.length):
            result[i] = self.data[i]
        return result


class Stack:
    """LIFO Stack - used for case update undo functionality"""
    
    DEFAULT_CAPACITY = 1000
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.items = [None] * capacity
        self.top = -1  # -1 means empty
    
    def push(self, item: Any) -> bool:
        if self.top >= self.capacity - 1:
            return False
        self.top = self.top + 1
        self.items[self.top] = item
        return True
    
    def pop(self) -> Optional[Any]:
        if self.top == -1:
            return None
        item = self.items[self.top]
        self.items[self.top] = None
        self.top = self.top - 1
        return item
    
    def peek(self) -> Optional[Any]:
        if self.top == -1:
            return None
        return self.items[self.top]
    
    def is_empty(self) -> bool:
        return self.top == -1
    
    def size(self) -> int:
        return self.top + 1
    
    def clear(self) -> None:
        for i in range(self.top + 1):
            self.items[i] = None
        self.top = -1


class Queue:
    """FIFO Queue using circular array - for messages, follow-ups, notifications"""
    
    DEFAULT_CAPACITY = 1000
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.items = [None] * capacity
        self.front = -1
        self.rear = -1
        self.count = 0
    
    def enqueue(self, item: Any) -> bool:
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
    
    def dequeue(self) -> Optional[Any]:
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
    
    def peek(self) -> Optional[Any]:
        if self.front == -1:
            return None
        return self.items[self.front]
    
    def is_empty(self) -> bool:
        return self.front == -1
    
    def size(self) -> int:
        return self.count
    
    def get_all(self) -> list:
        if self.front == -1:
            return []
        
        result = [None] * self.count
        i = self.front
        result_idx = 0
        while result_idx < self.count:
            result[result_idx] = self.items[i]
            i = (i + 1) % self.capacity
            result_idx = result_idx + 1
        
        return result


class PriorityQueue:
    """Min-heap priority queue - lower number = higher priority"""
    
    DEFAULT_CAPACITY = 1000
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.heap = [None] * capacity
        self.heap_size = 0
        self.entry_counter = 0  # for FIFO among same priority
    
    def _parent(self, index: int) -> int:
        return (index - 1) // 2
    
    def _left_child(self, index: int) -> int:
        return 2 * index + 1
    
    def _right_child(self, index: int) -> int:
        return 2 * index + 2
    
    def _swap(self, i: int, j: int) -> None:
        temp = self.heap[i]
        self.heap[i] = self.heap[j]
        self.heap[j] = temp
    
    def _compare(self, entry1: Tuple, entry2: Tuple) -> bool:
        # entry format: (priority, counter, item)
        if entry1[0] != entry2[0]:
            return entry1[0] < entry2[0]
        return entry1[1] < entry2[1]
    
    def _heapify_up(self, index: int) -> None:
        while index > 0:
            parent_idx = self._parent(index)
            if self._compare(self.heap[index], self.heap[parent_idx]):
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break
    
    def _heapify_down(self, index: int) -> None:
        while True:
            smallest = index
            left = self._left_child(index)
            right = self._right_child(index)
            
            if left < self.heap_size and self._compare(self.heap[left], self.heap[smallest]):
                smallest = left
            if right < self.heap_size and self._compare(self.heap[right], self.heap[smallest]):
                smallest = right
            
            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break
    
    def enqueue(self, item: Any, priority: int) -> bool:
        if self.heap_size >= self.capacity:
            return False
        
        entry = (priority, self.entry_counter, item)
        self.entry_counter = self.entry_counter + 1
        
        self.heap[self.heap_size] = entry
        self._heapify_up(self.heap_size)
        self.heap_size = self.heap_size + 1
        return True
    
    def dequeue(self) -> Optional[Any]:
        if self.heap_size == 0:
            return None
        
        root_entry = self.heap[0]
        item = root_entry[2]
        
        self.heap_size = self.heap_size - 1
        if self.heap_size > 0:
            self.heap[0] = self.heap[self.heap_size]
            self.heap[self.heap_size] = None
            self._heapify_down(0)
        else:
            self.heap[0] = None
        
        return item
    
    def peek(self) -> Optional[Any]:
        if self.heap_size == 0:
            return None
        return self.heap[0][2]
    
    def is_empty(self) -> bool:
        return self.heap_size == 0
    
    def size(self) -> int:
        return self.heap_size
    
    def get_all(self) -> list:
        if self.heap_size == 0:
            return []
        
        entries = [None] * self.heap_size
        for i in range(self.heap_size):
            entries[i] = self.heap[i]
        
        # bubble sort by priority
        n = self.heap_size
        for i in range(n):
            for j in range(0, n - i - 1):
                if not self._compare(entries[j], entries[j + 1]):
                    temp = entries[j]
                    entries[j] = entries[j + 1]
                    entries[j + 1] = temp
        
        result = [None] * self.heap_size
        for i in range(self.heap_size):
            result[i] = entries[i][2]
        return result


class HashTable:
    """Hash table with linked list chaining for collision handling"""
    
    DEFAULT_SIZE = 101  # prime for better distribution
    
    def __init__(self, size: int = DEFAULT_SIZE):
        self.size = size
        self.table = [None] * size
        self.count = 0
    
    def _hash(self, key: str) -> int:
        hash_value = 0
        position = 0
        for char in key:
            ascii_val = ord(char)
            position = position + 1
            hash_value = hash_value + (ascii_val * position)
        return hash_value % self.size
    
    def put(self, key: str, value: Any) -> None:
        index = self._hash(key)
        
        current = self.table[index]
        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next
        
        new_node = Node(key, value)
        new_node.next = self.table[index]
        self.table[index] = new_node
        self.count = self.count + 1
    
    def get(self, key: str) -> Optional[Any]:
        index = self._hash(key)
        current = self.table[index]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None
    
    def contains(self, key: str) -> bool:
        index = self._hash(key)
        current = self.table[index]
        while current is not None:
            if current.key == key:
                return True
            current = current.next
        return False
    
    def remove(self, key: str) -> bool:
        index = self._hash(key)
        current = self.table[index]
        prev = None
        
        while current is not None:
            if current.key == key:
                if prev is None:
                    self.table[index] = current.next
                else:
                    prev.next = current.next
                self.count = self.count - 1
                return True
            prev = current
            current = current.next
        return False
    
    def get_all_values(self) -> list:
        total = 0
        for i in range(self.size):
            current = self.table[i]
            while current is not None:
                total = total + 1
                current = current.next
        
        result = [None] * total
        result_idx = 0
        for i in range(self.size):
            current = self.table[i]
            while current is not None:
                result[result_idx] = current.value
                result_idx = result_idx + 1
                current = current.next
        return result


class CaseStore:
    """Hash table wrapper for case lookups"""
    
    def __init__(self):
        self.cases = HashTable()
    
    def add_case(self, case_id: str, case_data: Dict) -> None:
        self.cases.put(case_id, case_data)
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        return self.cases.get(case_id)
    
    def update_case(self, case_id: str, updates: Dict) -> bool:
        case = self.cases.get(case_id)
        if case is None:
            return False
        for key in updates:
            case[key] = updates[key]
        return True
    
    def get_cases_by_client(self, client_id: str) -> list:
        all_cases = self.cases.get_all_values()
        
        match_count = 0
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('client_id') == client_id:
                match_count = match_count + 1
        
        result = [None] * match_count
        result_idx = 0
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('client_id') == client_id:
                result[result_idx] = case
                result_idx = result_idx + 1
        return result
    
    def get_cases_by_lawyer(self, lawyer_id: str) -> list:
        all_cases = self.cases.get_all_values()
        
        match_count = 0
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('lawyer_id') == lawyer_id:
                match_count = match_count + 1
        
        result = [None] * match_count
        result_idx = 0
        for i in range(self._get_array_length(all_cases)):
            case = all_cases[i]
            if case is not None and case.get('lawyer_id') == lawyer_id:
                result[result_idx] = case
                result_idx = result_idx + 1
        return result
    
    def _get_array_length(self, arr: list) -> int:
        count = 0
        for _ in arr:
            count = count + 1
        return count
    
    def case_exists(self, case_id: str) -> bool:
        return self.cases.contains(case_id)
    
    def get_all_cases(self) -> list:
        return self.cases.get_all_values()


class UserStore:
    """Dual-indexed hash table for user management (by email and by ID)"""
    
    def __init__(self):
        self.users_by_email = HashTable()
        self.users_by_id = HashTable()
    
    @property
    def users(self):
        all_values = self.users_by_email.get_all_values()
        result = {}
        for i in range(self._get_array_length(all_values)):
            user = all_values[i]
            if user is not None and 'email' in user:
                result[user['email']] = user
        return result
    
    def _get_array_length(self, arr: list) -> int:
        count = 0
        for _ in arr:
            count = count + 1
        return count
    
    def add_user(self, user_id: str, email: str, user_data: Dict) -> None:
        self.users_by_email.put(email, user_data)
        self.users_by_id.put(user_id, user_data)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self.users_by_email.get(email)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return self.users_by_id.get(user_id)
    
    def email_exists(self, email: str) -> bool:
        return self.users_by_email.contains(email)
    
    def get_all_users(self) -> list:
        return self.users_by_email.get_all_values()


class DocumentStore:
    """Hash table for document metadata, linked to cases"""
    
    def __init__(self):
        self.documents = HashTable()
    
    def add_document(self, doc_id: str, case_id: str, metadata: Dict) -> None:
        doc_data = {'case_id': case_id}
        for key in metadata:
            doc_data[key] = metadata[key]
        self.documents.put(doc_id, doc_data)
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        return self.documents.get(doc_id)
    
    def get_documents_by_case(self, case_id: str) -> list:
        all_docs = self.documents.get_all_values()
        
        match_count = 0
        for i in range(self._get_array_length(all_docs)):
            doc = all_docs[i]
            if doc is not None and doc.get('case_id') == case_id:
                match_count = match_count + 1
        
        result = [None] * match_count
        result_idx = 0
        for i in range(self._get_array_length(all_docs)):
            doc = all_docs[i]
            if doc is not None and doc.get('case_id') == case_id:
                result[result_idx] = doc
                result_idx = result_idx + 1
        return result
    
    def _get_array_length(self, arr: list) -> int:
        count = 0
        for _ in arr:
            count = count + 1
        return count
