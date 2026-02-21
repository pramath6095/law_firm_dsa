from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import uuid

from data_structures import (
    Queue, PriorityQueue, Stack, CaseStore, UserStore, DocumentStore
)

# valid state transitions for cases
VALID_STATE_TRANSITIONS = {
    'created': ['in_review', 'active', 'closed'],
    'in_review': ['active', 'created', 'closed'],
    'active': ['closed'],
    'closed': []
}


class CaseManager:
    """Handles case creation, ownership, and state management"""
    
    def __init__(self, case_store: CaseStore):
        self.case_store = case_store
        self.case_history_stack = {}  # case_id -> Stack for undo
    
    def create_case(self, client_id: str, case_type: str, 
                   description: str, hearing_date: str) -> Dict:
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        
        hearing_datetime = datetime.fromisoformat(hearing_date)
        days_until = (hearing_datetime - datetime.now()).days
        
        if days_until <= 7:
            urgency_level = 'urgent'
        elif days_until <= 14:
            urgency_level = 'high'
        else:
            urgency_level = 'normal'
        
        # lower score = more urgent, overdue cases get 0
        priority_score = max(0, days_until)
        
        case_data = {
            'case_id': case_id,
            'client_id': client_id,
            'lawyer_id': None,
            'case_type': case_type,
            'description': description,
            'hearing_date': hearing_date,
            'urgency_level': urgency_level,
            'days_until_hearing': days_until,
            'priority_score': priority_score,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'updates': [],
            'events': [
                {
                    'event_id': f'EVT-{uuid.uuid4().hex[:8].upper()}',
                    'event_type': 'hearing',
                    'date': hearing_date,
                    'description': 'Court hearing',
                    'created_by': 'system',
                    'created_at': datetime.now().isoformat()
                }
            ]
        }
        
        self.case_store.add_case(case_id, case_data)
        self.case_history_stack[case_id] = Stack()
        
        return case_data
    
    def check_access(self, case_id: str, user_id: str, role: str) -> bool:
        case = self.case_store.get_case(case_id)
        if not case:
            return False
        if role == 'client':
            return case['client_id'] == user_id
        elif role == 'lawyer':
            return case['lawyer_id'] == user_id
        return False
    
    def update_case_status(self, case_id: str, new_status: str, 
                          updated_by: str, notes: str = "") -> Tuple[bool, str]:
        case = self.case_store.get_case(case_id)
        if not case:
            return False, "Case not found"
        
        current_status = case['status']
        
        if new_status not in VALID_STATE_TRANSITIONS.get(current_status, []):
            return False, f"Invalid transition from {current_status} to {new_status}"
        
        # save current state to undo stack before applying
        previous_state = {
            'status': current_status,
            'updates': case['updates'].copy(),
            'updated_at': case['updated_at']
        }
        self.case_history_stack[case_id].push(previous_state)
        
        update_entry = {
            'timestamp': datetime.now().isoformat(),
            'updated_by': updated_by,
            'old_status': current_status,
            'new_status': new_status,
            'notes': notes
        }
        
        case['status'] = new_status
        case['updates'].append(update_entry)
        case['updated_at'] = datetime.now().isoformat()
        
        return True, "Update successful"
    
    def undo_last_update(self, case_id: str) -> Tuple[bool, str]:
        if case_id not in self.case_history_stack:
            return False, "No history found"
        
        stack = self.case_history_stack[case_id]
        if stack.is_empty():
            return False, "No previous state to restore"
        
        previous_state = stack.pop()
        case = self.case_store.get_case(case_id)
        
        if case:
            case['status'] = previous_state['status']
            case['updates'] = previous_state['updates']
            case['updated_at'] = previous_state['updated_at']
            return True, "Successfully undone"
        
        return False, "Case not found"
    
    def assign_lawyer(self, case_id: str, lawyer_id: str) -> bool:
        return self.case_store.update_case(case_id, {'lawyer_id': lawyer_id})
    
    def get_lawyer_case_count(self, lawyer_id: str) -> int:
        all_cases = self.case_store.get_all_cases()
        return sum(1 for c in all_cases 
                    if c.get('lawyer_id') == lawyer_id 
                    and c.get('status') != 'closed')
    
    def find_available_lawyer(self, speciality: str, user_store) -> Optional[str]:
        all_lawyers = [u for u in user_store.get_all_users() if u.get('role') == 'lawyer']
        
        for lawyer in all_lawyers:
            lawyer_specialities = lawyer.get('speciality', [])
            if isinstance(lawyer_specialities, str):
                lawyer_specialities = [lawyer_specialities]
            
            if speciality in lawyer_specialities:
                if self.get_lawyer_case_count(lawyer['user_id']) < 2:
                    return lawyer['user_id']
        
        return None
    
    def create_case_with_assignment(self, client_id, case_type, description, 
                                    hearing_date, selected_lawyer_id, speciality, user_store):
        """Create case and try assigning to selected lawyer, fallback to another if busy"""
        case = self.create_case(client_id, case_type, description, hearing_date)
        
        lawyer = user_store.get_user_by_id(selected_lawyer_id)
        case_count = self.get_lawyer_case_count(selected_lawyer_id)
        
        if case_count < 2:
            case['lawyer_id'] = selected_lawyer_id
            self.case_store.update_case(case['case_id'], {'lawyer_id': selected_lawyer_id})
            return ('success', case, None)
        
        # selected lawyer busy, find alternative
        alternative = self.find_available_lawyer(speciality, user_store)
        
        if alternative:
            case['lawyer_id'] = alternative['user_id']
            self.case_store.update_case(case['case_id'], {'lawyer_id': alternative['user_id']})
            return ('auto_assigned', case, alternative)
        
        return ('all_busy', None, None)


class MessageManager:
    """Case-bound messaging using queues"""
    
    def __init__(self):
        self.case_messages = {}
    
    def send_message(self, case_id: str, sender_id: str, 
                    sender_role: str, content: str) -> Dict:
        if case_id not in self.case_messages:
            self.case_messages[case_id] = Queue()
        
        message = {
            'message_id': uuid.uuid4().hex[:8],
            'sender_id': sender_id,
            'sender_role': sender_role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.case_messages[case_id].enqueue(message)
        return message
    
    def get_messages(self, case_id: str) -> List[Dict]:
        if case_id not in self.case_messages:
            return []
        return self.case_messages[case_id].get_all()


class DocumentManager:
    """Document upload and access control"""
    
    def __init__(self, document_store: DocumentStore, case_store: CaseStore):
        self.document_store = document_store
        self.case_store = case_store
    
    def upload_document(self, case_id: str, uploader_id: str,
                       filename: str, file_path: str) -> Dict:
        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        
        metadata = {
            'doc_id': doc_id,
            'filename': filename,
            'file_path': file_path,
            'uploader_id': uploader_id,
            'uploaded_at': datetime.now().isoformat()
        }
        
        self.document_store.add_document(doc_id, case_id, metadata)
        return metadata
    
    def check_document_access(self, doc_id: str, user_id: str, 
                             role: str) -> bool:
        doc = self.document_store.get_document(doc_id)
        if not doc:
            return False
        
        case_id = doc['case_id']
        case = self.case_store.get_case(case_id)
        if not case:
            return False
        
        # only case owner and assigned lawyer can access
        if role == 'client' and case['client_id'] == user_id:
            return True
        if role == 'lawyer' and case['lawyer_id'] == user_id:
            return True
        return False


class FollowUpManager:
    """Follow-up and hearing scheduling"""
    
    def __init__(self):
        self.case_followups = {}
    
    def schedule_followup(self, case_id: str, lawyer_id: str,
                         followup_type: str, scheduled_date: str,
                         notes: str = "") -> Dict:
        if case_id not in self.case_followups:
            self.case_followups[case_id] = Queue()
        
        followup = {
            'followup_id': uuid.uuid4().hex[:8],
            'type': followup_type,
            'scheduled_date': scheduled_date,
            'scheduled_by': lawyer_id,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        
        self.case_followups[case_id].enqueue(followup)
        return followup
    
    def get_followups(self, case_id: str) -> List[Dict]:
        if case_id not in self.case_followups:
            return []
        return self.case_followups[case_id].get_all()


class AvailableCasesPool:
    """Manages available cases that lawyers can claim from"""
    
    def __init__(self):
        self.urgent_pool = PriorityQueue()
        self.normal_pool = Queue()
        self.case_assignments = {}
        self.lawyer_case_counts = {}
        self.pending_requests = {}
        self.MAX_CASES_PER_LAWYER = 2
    
    def add_to_pool(self, case: Dict) -> None:
        case_id = case['case_id']
        
        if case.get('assignment_type') == 'direct' and case.get('requested_lawyer_id'):
            lawyer_id = case['requested_lawyer_id']
            if lawyer_id not in self.pending_requests:
                self.pending_requests[lawyer_id] = Queue()
            
            request_data = {
                **case,
                'request_status': 'pending',
                'requested_at': datetime.now().isoformat()
            }
            self.pending_requests[lawyer_id].enqueue(request_data)
            self.case_assignments[case_id] = {
                'status': 'pending_direct',
                'requested_lawyer': lawyer_id
            }
        else:
            if case.get('urgency'):
                self.urgent_pool.enqueue(case, priority=1)
            else:
                self.normal_pool.enqueue(case)
            
            self.case_assignments[case_id] = {
                'status': 'available',
                'in_pool': True
            }
    
    def get_available_cases(self) -> List[Dict]:
        urgent = self.urgent_pool.get_all()
        normal = self.normal_pool.get_all()
        return urgent + normal
    
    def get_pending_requests(self, lawyer_id: str) -> List[Dict]:
        if lawyer_id not in self.pending_requests:
            return []
        return self.pending_requests[lawyer_id].get_all()
    
    def can_lawyer_claim(self, lawyer_id: str) -> Tuple[bool, str]:
        current_count = self.lawyer_case_counts.get(lawyer_id, 0)
        if current_count >= self.MAX_CASES_PER_LAWYER:
            return False, f"Maximum case load reached ({self.MAX_CASES_PER_LAWYER} cases)"
        return True, "OK"
    
    def claim_case(self, case_id: str, lawyer_id: str) -> Tuple[bool, str]:
        can_claim, message = self.can_lawyer_claim(lawyer_id)
        if not can_claim:
            return False, message
        
        if case_id not in self.case_assignments:
            return False, "Case not found"
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] not in ['available', 'rejected_then_available']:
            return False, "Case not available"
        
        case_found = False
        claimed_case = None
        
        # check urgent pool first
        urgent_cases = self.urgent_pool.get_all()
        for case in urgent_cases:
            if case['case_id'] == case_id:
                claimed_case = case
                temp_pool = PriorityQueue()
                for c in urgent_cases:
                    if c['case_id'] != case_id:
                        temp_pool.enqueue(c, priority=1)
                self.urgent_pool = temp_pool
                case_found = True
                break
        
        if not case_found:
            normal_cases = self.normal_pool.get_all()
            for case in normal_cases:
                if case['case_id'] == case_id:
                    claimed_case = case
                    temp_pool = Queue()
                    for c in normal_cases:
                        if c['case_id'] != case_id:
                            temp_pool.enqueue(c)
                    self.normal_pool = temp_pool
                    case_found = True
                    break
        
        if not case_found:
            return False, "Case not in pool"
        
        self.case_assignments[case_id] = {
            'status': 'claimed',
            'lawyer_id': lawyer_id,
            'claimed_at': datetime.now().isoformat()
        }
        self.lawyer_case_counts[lawyer_id] = self.lawyer_case_counts.get(lawyer_id, 0) + 1
        
        return True, "Case claimed successfully"
    
    def unclaim_case(self, case_id: str, case_data: Dict) -> bool:
        if case_id not in self.case_assignments:
            return False
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] != 'claimed':
            return False
        
        lawyer_id = assignment.get('lawyer_id')
        if lawyer_id and lawyer_id in self.lawyer_case_counts:
            self.lawyer_case_counts[lawyer_id] = max(0, self.lawyer_case_counts[lawyer_id] - 1)
        
        if case_data.get('urgency'):
            self.urgent_pool.enqueue(case_data, priority=1)
        else:
            self.normal_pool.enqueue(case_data)
        
        self.case_assignments[case_id] = {
            'status': 'available',
            'in_pool': True
        }
        return True
    
    def accept_direct_request(self, case_id: str, lawyer_id: str) -> Tuple[bool, str]:
        can_claim, message = self.can_lawyer_claim(lawyer_id)
        if not can_claim:
            return False, message
        
        if case_id not in self.case_assignments:
            return False, "Case not found"
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] != 'pending_direct':
            return False, "Not a pending request"
        if assignment.get('requested_lawyer') != lawyer_id:
            return False, "Request not for this lawyer"
        
        # remove from pending queue
        if lawyer_id in self.pending_requests:
            pending_cases = self.pending_requests[lawyer_id].get_all()
            temp_queue = Queue()
            for case in pending_cases:
                if case['case_id'] != case_id:
                    temp_queue.enqueue(case)
            self.pending_requests[lawyer_id] = temp_queue
        
        self.case_assignments[case_id] = {
            'status': 'claimed',
            'lawyer_id': lawyer_id,
            'claimed_at': datetime.now().isoformat(),
            'assignment_type': 'direct'
        }
        self.lawyer_case_counts[lawyer_id] = self.lawyer_case_counts.get(lawyer_id, 0) + 1
        
        return True, "Request accepted"
    
    def reject_direct_request(self, case_id: str, lawyer_id: str, case_data: Dict) -> bool:
        if case_id not in self.case_assignments:
            return False
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] != 'pending_direct':
            return False
        
        if lawyer_id in self.pending_requests:
            pending_cases = self.pending_requests[lawyer_id].get_all()
            temp_queue = Queue()
            for case in pending_cases:
                if case['case_id'] != case_id:
                    temp_queue.enqueue(case)
            self.pending_requests[lawyer_id] = temp_queue
        
        # move to general pool
        if case_data.get('urgency'):
            self.urgent_pool.enqueue(case_data, priority=1)
        else:
            self.normal_pool.enqueue(case_data)
        
        self.case_assignments[case_id] = {
            'status': 'rejected_then_available',
            'rejected_by': lawyer_id,
            'in_pool': True
        }
        return True
    
    def get_lawyer_case_count(self, lawyer_id: str) -> int:
        return self.lawyer_case_counts.get(lawyer_id, 0)


class NotificationManager:
    """Event-driven notifications using queues"""
    
    def __init__(self):
        self.user_notifications = {}
    
    def add_notification(self, user_id: str, notification_type: str,
                        message: str, related_id: str = None) -> None:
        if user_id not in self.user_notifications:
            self.user_notifications[user_id] = Queue()
        
        notification = {
            'type': notification_type,
            'message': message,
            'related_id': related_id,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        self.user_notifications[user_id].enqueue(notification)
    
    def get_notifications(self, user_id: str) -> List[Dict]:
        if user_id not in self.user_notifications:
            return []
        return self.user_notifications[user_id].get_all()
    
    def get_unread_count(self, user_id: str) -> int:
        notifications = self.get_notifications(user_id)
        return sum(1 for n in notifications if not n['read'])



class EventManager:
    """Manages hearings, appointments, and follow-ups for cases"""
    
    def __init__(self, case_store):
        self.case_store = case_store
    
    def add_event(self, case_id, event_type, date, description, created_by):
        event = {
            'event_id': f'EVT-{uuid.uuid4().hex[:8].upper()}',
            'event_type': event_type,
            'date': date,
            'description': description,
            'created_by': created_by,
            'created_at': datetime.now().isoformat()
        }
        
        case = self.case_store.get_case(case_id)
        if 'events' not in case:
            case['events'] = []
        case['events'].append(event)
        self.case_store.update_case(case_id, case)
        return event
    
    def get_weekly_events(self, user_id, role, start_date=None):
        if start_date is None:
            start_date = datetime.now()
       
        # week boundaries: Sunday to Saturday
        days_since_sunday = (start_date.weekday() + 1) % 7
        week_start = start_date - timedelta(days=days_since_sunday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        if role == 'client':
            cases = self.case_store.get_cases_by_client(user_id)
        else:
            cases = self.case_store.get_cases_by_lawyer(user_id)
        
        all_events = []
        for case in cases:
            if case.get('status') == 'closed':
                continue
            
            for event in case.get('events', []):
                event_date = datetime.fromisoformat(event['date'])
                if event_date.tzinfo is not None:
                    event_date = event_date.replace(tzinfo=None)
                
                if week_start <= event_date <= week_end:
                    all_events.append({
                        **event,
                        'case_id': case['case_id'],
                        'case_type': case['case_type'],
                        'urgency_level': case.get('urgency_level'),
                        'priority_score': case.get('priority_score', 0)
                    })
        
        all_events.sort(key=lambda e: datetime.fromisoformat(e['date']).replace(tzinfo=None) if datetime.fromisoformat(e['date']).tzinfo else datetime.fromisoformat(e['date']))
        return all_events
