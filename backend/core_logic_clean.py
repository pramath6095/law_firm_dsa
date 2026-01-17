"""
Core Logic Layer for Legal Case Management System

Implements the 10 critical logic components using data structures:
1. Case Ownership & Access Control
2. Appointment Request Handling
3. Appointment Conflict Detection
4. Urgency-Based Case Handling
5. Case Update with Undo
6. Case State Validation
7. Case-Bound Messaging
8. Document Access Control
9. Follow-Up Scheduling
10. Notification System
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import uuid

from data_structures import (
    Queue, PriorityQueue, Stack, CaseStore, UserStore, DocumentStore
)


# Valid case state transitions
VALID_STATE_TRANSITIONS = {
    'created': ['in_review'],
    'in_review': ['active', 'created'],  # Can go back to created if rejected
    'active': ['closed'],
    'closed': []  # Terminal state
}


class CaseManager:
    """Handles case creation, ownership, and state management"""
    
    def __init__(self, case_store: CaseStore):
        self.case_store = case_store
        self.case_history_stack = {}  # case_id -> Stack of previous states
    
    def create_case(self, client_id: str, case_type: str, 
                   description: str, urgency: bool) -> Dict:
        """
        Create new case with ownership
        Returns: case data dict
        """
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        
        case_data = {
            'case_id': case_id,
            'client_id': client_id,
            'lawyer_id': None,  # Assigned later
            'case_type': case_type,
            'description': description,
            'urgency': urgency,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'updates': []
        }
        
        self.case_store.add_case(case_id, case_data)
        self.case_history_stack[case_id] = Stack()  # Initialize undo stack
        
        return case_data
    
    def check_access(self, case_id: str, user_id: str, role: str) -> bool:
        """
        Core access control logic
        Returns: True if user can access case
        """
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
        """
        Update case status with state validation and undo support
        Returns: (success, message)
        """
        case = self.case_store.get_case(case_id)
        if not case:
            return False, "Case not found"
        
        current_status = case['status']
        
        # Validate state transition
        if new_status not in VALID_STATE_TRANSITIONS.get(current_status, []):
            return False, f"Invalid transition from {current_status} to {new_status}"
        
        # Save current state to undo stack
        previous_state = {
            'status': current_status,
            'updates': case['updates'].copy(),
            'updated_at': case['updated_at']
        }
        self.case_history_stack[case_id].push(previous_state)
        
        # Apply update
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
        """
        Undo last case update using stack
        Returns: (success, message)
        """
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
        """Assign lawyer to case"""
        return self.case_store.update_case(case_id, {'lawyer_id': lawyer_id})
    
    def get_lawyer_case_count(self, lawyer_id: str) -> int:
        """Count active cases for a lawyer"""
        all_cases = self.case_store.get_all_cases()
        return len([c for c in all_cases 
                    if c.get('lawyer_id') == lawyer_id 
                    and c.get('status') != 'closed'])
    
    def find_available_lawyer(self, speciality: str, user_store):
        """Find lawyer with matching speciality and < 2 cases"""
        all_lawyers = [u for u in user_store.users.values() 
                       if u.get('role') == 'lawyer']
        
        for lawyer in all_lawyers:
            if lawyer.get('speciality') == speciality:
                case_count = self.get_lawyer_case_count(lawyer['user_id'])
                if case_count < 2:
                    return lawyer
        
        return None
    
    def create_case_with_assignment(self, client_id, case_type, description, 
                                    hearing_date, selected_lawyer_id, speciality, user_store):
        """
        New flow with auto-assignment:
        1. Create case  
        2. Try to assign to selected_lawyer_id
        3. If busy, find another lawyer with same speciality
        4. If all busy, return error with firm contact
        """
        # Create case using existing create_case method
        case = self.create_case(client_id, case_type, description, hearing_date)
        
        # Try selected lawyer first
        lawyer = user_store.get_user_by_id(selected_lawyer_id)
        case_count = self.get_lawyer_case_count(selected_lawyer_id)
        
        if case_count < 2:
            # Assign to selected lawyer
            case['lawyer_id'] = selected_lawyer_id
            self.case_store.update_case(case['case_id'], {'lawyer_id': selected_lawyer_id})
            return ('success', case, None)
        
        # Selected lawyer busy, find alternative with same speciality
        alternative = self.find_available_lawyer(speciality, user_store)
        
        if alternative:
            case['lawyer_id'] = alternative['user_id']
            self.case_store.update_case(case['case_id'], {'lawyer_id': alternative['user_id']})
            return ('auto_assigned', case, alternative)
        
        # All specialists busy
        return ('all_busy', None, None)


class AppointmentManager:
    """Handles appointment requests with queue-based processing"""
    
    def __init__(self):
        self.normal_queue = Queue()  # Normal appointment requests
        self.urgent_queue = PriorityQueue()  # Urgent appointment requests
        self.appointments = {}  # appointment_id -> appointment data
        self.lawyer_schedules = {}  # lawyer_id -> list of appointment times
    
    def request_appointment(self, case_id: str, client_id: str,
                           preferred_datetime: str, urgency: bool) -> Dict:
        """
        Client requests appointment
        Routes to normal or urgent queue
        """
        appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        
        request_data = {
            'appointment_id': appointment_id,
            'case_id': case_id,
            'client_id': client_id,
            'preferred_datetime': preferred_datetime,
            'status': 'pending',
            'urgency': urgency,
            'created_at': datetime.now().isoformat()
        }
        
        # Route based on urgency
        if urgency:
            self.urgent_queue.enqueue(request_data, priority=1)
        else:
            self.normal_queue.enqueue(request_data)
        
        self.appointments[appointment_id] = request_data
        
        return request_data
    
    def get_next_request(self) -> Optional[Dict]:
        """
        Get next appointment request for lawyer to process
        Urgent queue has priority
        """
        # Check urgent queue first
        if not self.urgent_queue.is_empty():
            return self.urgent_queue.dequeue()
        
        # Then normal queue
        if not self.normal_queue.is_empty():
            return self.normal_queue.dequeue()
        
        return None
    
    def check_conflict(self, lawyer_id: str, proposed_datetime: str) -> bool:
        """
        Check if proposed appointment conflicts with lawyer's schedule
        Returns: True if conflict exists
        """
        if lawyer_id not in self.lawyer_schedules:
            return False
        
        proposed_time = datetime.fromisoformat(proposed_datetime)
        
        for existing_time in self.lawyer_schedules[lawyer_id]:
            existing = datetime.fromisoformat(existing_time)
            # Check if within 1 hour window
            time_diff = abs((existing - proposed_time).total_seconds() / 60)
            if time_diff < 60:  # Conflict if within 60 minutes
                return True
        
        return False
    
    def approve_appointment(self, appointment_id: str, lawyer_id: str,
                           confirmed_datetime: str) -> Tuple[bool, str]:
        """
        Lawyer approves appointment
        Checks for conflicts
        """
        if appointment_id not in self.appointments:
            return False, "Appointment not found"
        
        # Check for conflicts
        if self.check_conflict(lawyer_id, confirmed_datetime):
            return False, "Time slot conflicts with existing appointment"
        
        # Approve
        appointment = self.appointments[appointment_id]
        appointment['status'] = 'approved'
        appointment['confirmed_datetime'] = confirmed_datetime
        appointment['lawyer_id'] = lawyer_id
        
        # Add to lawyer's schedule
        if lawyer_id not in self.lawyer_schedules:
            self.lawyer_schedules[lawyer_id] = []
        self.lawyer_schedules[lawyer_id].append(confirmed_datetime)
        
        return True, "Appointment approved"
    
    def reject_appointment(self, appointment_id: str, reason: str) -> bool:
        """Lawyer rejects appointment"""
        if appointment_id not in self.appointments:
            return False
        
        self.appointments[appointment_id]['status'] = 'rejected'
        self.appointments[appointment_id]['rejection_reason'] = reason
        return True
    
    def reschedule_appointment(self, appointment_id: str, 
                              new_datetime: str) -> bool:
        """Lawyer reschedules appointment"""
        if appointment_id not in self.appointments:
            return False
        
        self.appointments[appointment_id]['status'] = 'rescheduled'
        self.appointments[appointment_id]['rescheduled_datetime'] = new_datetime
        return True
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending requests (for display)"""
        urgent = self.urgent_queue.get_all()
        normal = self.normal_queue.get_all()
        return urgent + normal


class MessageManager:
    """Handles case-bound messaging"""
    
    def __init__(self):
        self.case_messages = {}  # case_id -> Queue of messages
    
    def send_message(self, case_id: str, sender_id: str, 
                    sender_role: str, content: str) -> Dict:
        """Send message within a case context"""
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
        """Get all messages for a case"""
        if case_id not in self.case_messages:
            return []
        
        return self.case_messages[case_id].get_all()


class DocumentManager:
    """Handles document upload and access control"""
    
    def __init__(self, document_store: DocumentStore, case_store: CaseStore):
        self.document_store = document_store
        self.case_store = case_store
    
    def upload_document(self, case_id: str, uploader_id: str,
                       filename: str, file_path: str) -> Dict:
        """Upload document to case"""
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
        """Check if user can access document"""
        doc = self.document_store.get_document(doc_id)
        if not doc:
            return False
        
        case_id = doc['case_id']
        case = self.case_store.get_case(case_id)
        
        if not case:
            return False
        
        # Only case owner and assigned lawyer can access
        if role == 'client' and case['client_id'] == user_id:
            return True
        if role == 'lawyer' and case['lawyer_id'] == user_id:
            return True
        
        return False


class FollowUpManager:
    """Handles follow-up and hearing scheduling"""
    
    def __init__(self):
        self.case_followups = {}  # case_id -> Queue of follow-ups
    
    def schedule_followup(self, case_id: str, lawyer_id: str,
                         followup_type: str, scheduled_date: str,
                         notes: str = "") -> Dict:
        """Lawyer schedules follow-up (only lawyers can schedule)"""
        if case_id not in self.case_followups:
            self.case_followups[case_id] = Queue()
        
        followup = {
            'followup_id': uuid.uuid4().hex[:8],
            'type': followup_type,  # 'consultation' or 'hearing'
            'scheduled_date': scheduled_date,
            'scheduled_by': lawyer_id,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        
        self.case_followups[case_id].enqueue(followup)
        return followup
    
    def get_followups(self, case_id: str) -> List[Dict]:
        """Get all follow-ups for a case"""
        if case_id not in self.case_followups:
            return []
        
        return self.case_followups[case_id].get_all()


class AvailableCasesPool:
    """
    Manages available cases that lawyers can claim
    Uses Priority Queue for urgent cases, Queue for normal cases
    """
    
    def __init__(self):
        self.urgent_pool = PriorityQueue()  # Urgent cases
        self.normal_pool = Queue()  # Normal cases (FIFO)
        self.case_assignments = {}  # case_id -> assignment status
        self.lawyer_case_counts = {}  # lawyer_id -> active case count
        self.pending_requests = {}  # lawyer_id -> Queue of direct assignment requests
        self.MAX_CASES_PER_LAWYER = 2
    
    def add_to_pool(self, case: Dict) -> None:
        """Add case to available pool"""
        case_id = case['case_id']
        
        # Check if it's a direct assignment or general
        if case.get('assignment_type') == 'direct' and case.get('requested_lawyer_id'):
            # Direct assignment - add to lawyer's pending requests
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
            # General pool
            if case.get('urgency'):
                self.urgent_pool.enqueue(case, priority=1)
            else:
                self.normal_pool.enqueue(case)
            
            self.case_assignments[case_id] = {
                'status': 'available',
                'in_pool': True
            }
    
    def get_available_cases(self) -> List[Dict]:
        """Get all available cases (for display)"""
        urgent = self.urgent_pool.get_all()
        normal = self.normal_pool.get_all()
        return urgent + normal
    
    def get_pending_requests(self, lawyer_id: str) -> List[Dict]:
        """Get pending direct assignment requests for a lawyer"""
        if lawyer_id not in self.pending_requests:
            return []
        return self.pending_requests[lawyer_id].get_all()
    
    def can_lawyer_claim(self, lawyer_id: str) -> Tuple[bool, str]:
        """Check if lawyer can claim more cases (max 2)"""
        current_count = self.lawyer_case_counts.get(lawyer_id, 0)
        if current_count >= self.MAX_CASES_PER_LAWYER:
            return False, f"Maximum case load reached ({self.MAX_CASES_PER_LAWYER} cases)"
        return True, "OK"
    
    def claim_case(self, case_id: str, lawyer_id: str) -> Tuple[bool, str]:
        """Lawyer claims a case from available pool"""
        # Check if lawyer can take more cases
        can_claim, message = self.can_lawyer_claim(lawyer_id)
        if not can_claim:
            return False, message
        
        # Check if case is available
        if case_id not in self.case_assignments:
            return False, "Case not found"
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] not in ['available', 'rejected_then_available']:
            return False, "Case not available"
        
        # Find and remove from pool
        case_found = False
        claimed_case = None
        
        # Try urgent pool
        urgent_cases = self.urgent_pool.get_all()
        for case in urgent_cases:
            if case['case_id'] == case_id:
                claimed_case = case
                # Rebuild pool without this case
                temp_pool = PriorityQueue()
                for c in urgent_cases:
                    if c['case_id'] != case_id:
                        temp_pool.enqueue(c, priority=1)
                self.urgent_pool = temp_pool
                case_found = True
                break
        
        # Try normal pool if not found
        if not case_found:
            normal_cases = self.normal_pool.get_all()
            for case in normal_cases:
                if case['case_id'] == case_id:
                    claimed_case = case
                    # Rebuild pool without this case
                    temp_pool = Queue()
                    for c in normal_cases:
                        if c['case_id'] != case_id:
                            temp_pool.enqueue(c)
                    self.normal_pool = temp_pool
                    case_found = True
                    break
        
        if not case_found:
            return False, "Case not in pool"
        
        # Update assignment
        self.case_assignments[case_id] = {
            'status': 'claimed',
            'lawyer_id': lawyer_id,
            'claimed_at': datetime.now().isoformat()
        }
        
        # Update lawyer case count
        self.lawyer_case_counts[lawyer_id] = self.lawyer_case_counts.get(lawyer_id, 0) + 1
        
        return True, "Case claimed successfully"
    
    def unclaim_case(self, case_id: str, case_data: Dict) -> bool:
        """Lawyer un-claims a case, returns it to pool"""
        if case_id not in self.case_assignments:
            return False
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] != 'claimed':
            return False
        
        lawyer_id = assignment.get('lawyer_id')
        
        # Decrease lawyer case count
        if lawyer_id and lawyer_id in self.lawyer_case_counts:
            self.lawyer_case_counts[lawyer_id] = max(0, self.lawyer_case_counts[lawyer_id] - 1)
        
        # Return to pool
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
        """Lawyer accepts a direct assignment request"""
        # Check case load
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
        
        # Remove from pending requests
        if lawyer_id in self.pending_requests:
            pending_cases = self.pending_requests[lawyer_id].get_all()
            temp_queue = Queue()
            for case in pending_cases:
                if case['case_id'] != case_id:
                    temp_queue.enqueue(case)
            self.pending_requests[lawyer_id] = temp_queue
        
        # Update assignment
        self.case_assignments[case_id] = {
            'status': 'claimed',
            'lawyer_id': lawyer_id,
            'claimed_at': datetime.now().isoformat(),
            'assignment_type': 'direct'
        }
        
        # Update lawyer case count
        self.lawyer_case_counts[lawyer_id] = self.lawyer_case_counts.get(lawyer_id, 0) + 1
        
        return True, "Request accepted"
    
    def reject_direct_request(self, case_id: str, lawyer_id: str, case_data: Dict) -> bool:
        """Lawyer rejects direct request - goes to general pool"""
        if case_id not in self.case_assignments:
            return False
        
        assignment = self.case_assignments[case_id]
        if assignment['status'] != 'pending_direct':
            return False
        
        # Remove from pending requests
        if lawyer_id in self.pending_requests:
            pending_cases = self.pending_requests[lawyer_id].get_all()
            temp_queue = Queue()
            for case in pending_cases:
                if case['case_id'] != case_id:
                    temp_queue.enqueue(case)
            self.pending_requests[lawyer_id] = temp_queue
        
        # Add to general pool
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
        """Get number of active cases for a lawyer"""
        return self.lawyer_case_counts.get(lawyer_id, 0)


class NotificationManager:
    """Handles event-driven notifications"""
    
    def __init__(self):
        self.user_notifications = {}  # user_id -> Queue of notifications
    
    def add_notification(self, user_id: str, notification_type: str,
                        message: str, related_id: str = None) -> None:
        """Add notification to user's queue"""
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
        """Get all notifications for user"""
        if user_id not in self.user_notifications:
            return []
        
        return self.user_notifications[user_id].get_all()
    
    def get_unread_count(self, user_id: str) -> int:
        """Count unread notifications"""
        notifications = self.get_notifications(user_id)
        return sum(1 for n in notifications if not n['read'])
 
  
 c l a s s   E v e n t M a n a g e r :  
         " " " M a n a g e s   h e a r i n g s ,   a p p o i n t m e n t s ,   a n d   f o l l o w - u p s   f o r   c a s e s " " "  
          
         d e f   _ _ i n i t _ _ ( s e l f ,   c a s e _ s t o r e ) :  
                 s e l f . c a s e _ s t o r e   =   c a s e _ s t o r e  
          
         d e f   a d d _ e v e n t ( s e l f ,   c a s e _ i d ,   e v e n t _ t y p e ,   d a t e ,   d e s c r i p t i o n ,   c r e a t e d _ b y ) :  
                 " " " A d d   e v e n t   t o   c a s e   -   e v e n t _ t y p e :   h e a r i n g ,   a p p o i n t m e n t ,   f o l l o w u p " " "  
                 e v e n t   =   {  
                         ' e v e n t _ i d ' :   f ' E V T - { u u i d . u u i d 4 ( ) . h e x [ : 8 ] . u p p e r ( ) } ' ,  
                         ' e v e n t _ t y p e ' :   e v e n t _ t y p e ,  
                         ' d a t e ' :   d a t e ,  
                         ' d e s c r i p t i o n ' :   d e s c r i p t i o n ,  
                         ' c r e a t e d _ b y ' :   c r e a t e d _ b y ,  
                         ' c r e a t e d _ a t ' :   d a t e t i m e . n o w ( ) . i s o f o r m a t ( )  
                 }  
                  
                 c a s e   =   s e l f . c a s e _ s t o r e . g e t _ c a s e ( c a s e _ i d )  
                 i f   ' e v e n t s '   n o t   i n   c a s e :  
                         c a s e [ ' e v e n t s ' ]   =   [ ]  
                 c a s e [ ' e v e n t s ' ] . a p p e n d ( e v e n t )  
                 s e l f . c a s e _ s t o r e . u p d a t e _ c a s e ( c a s e _ i d ,   c a s e )  
                 r e t u r n   e v e n t  
          
         d e f   g e t _ w e e k l y _ e v e n t s ( s e l f ,   u s e r _ i d ,   r o l e ,   s t a r t _ d a t e = N o n e ) :  
                 " " " G e t   a l l   e v e n t s   f o r   t h e   w e e k ,   s o r t e d   b y   p r i o r i t y " " "  
                 i f   s t a r t _ d a t e   i s   N o n e :  
                         s t a r t _ d a t e   =   d a t e t i m e . n o w ( )  
                
                 w e e k _ s t a r t   =   s t a r t _ d a t e   -   t i m e d e l t a ( d a y s = s t a r t _ d a t e . w e e k d a y ( ) )  
                 w e e k _ e n d   =   w e e k _ s t a r t   +   t i m e d e l t a ( d a y s = 7 )  
                  
                 i f   r o l e   = =   ' c l i e n t ' :  
                         c a s e s   =   s e l f . c a s e _ s t o r e . g e t _ c a s e s _ b y _ c l i e n t ( u s e r _ i d )  
                 e l s e :  
                         c a s e s   =   s e l f . c a s e _ s t o r e . g e t _ c a s e s _ b y _ l a w y e r ( u s e r _ i d )  
                  
                 a l l _ e v e n t s   =   [ ]  
                 f o r   c a s e   i n   c a s e s :  
                         f o r   e v e n t   i n   c a s e . g e t ( ' e v e n t s ' ,   [ ] ) :  
                                 e v e n t _ d a t e   =   d a t e t i m e . f r o m i s o f o r m a t ( e v e n t [ ' d a t e ' ] )  
                                 i f   w e e k _ s t a r t   < =   e v e n t _ d a t e   < =   w e e k _ e n d :  
                                         a l l _ e v e n t s . a p p e n d ( {  
                                                 * * e v e n t ,  
                                                 ' c a s e _ i d ' :   c a s e [ ' c a s e _ i d ' ] ,  
                                                 ' c a s e _ t y p e ' :   c a s e [ ' c a s e _ t y p e ' ] ,  
                                                 ' u r g e n c y _ l e v e l ' :   c a s e . g e t ( ' u r g e n c y _ l e v e l ' ) ,  
                                                 ' p r i o r i t y _ s c o r e ' :   c a s e . g e t ( ' p r i o r i t y _ s c o r e ' ,   0 )  
                                         } )  
                  
                 a l l _ e v e n t s . s o r t ( k e y = l a m b d a   e :   e . g e t ( ' p r i o r i t y _ s c o r e ' ,   0 ) ,   r e v e r s e = T r u e )  
                 r e t u r n   a l l _ e v e n t s  
 