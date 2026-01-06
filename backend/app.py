"""
Flask Backend API for Legal Case Management System

RESTful API endpoints for client and lawyer interfaces
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import uuid
import os

from data_structures import CaseStore, UserStore, DocumentStore
from core_logic import (
    CaseManager, AppointmentManager, MessageManager,
    DocumentManager, FollowUpManager, NotificationManager,
    AvailableCasesPool
)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Session configuration for CORS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Configure CORS to allow frontend origin with credentials
CORS(app, 
     origins=['http://localhost:8000', 'http://127.0.0.1:8000'],
     supports_credentials=True,
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize data stores
user_store = UserStore()
case_store = CaseStore()
document_store = DocumentStore()

# Initialize managers
case_manager = CaseManager(case_store)
appointment_manager = AppointmentManager()
message_manager = MessageManager()
document_manager = DocumentManager(document_store, case_store)
followup_manager = FollowUpManager()
notification_manager = NotificationManager()
available_cases_pool = AvailableCasesPool()  # NEW: Available cases pool


# Create sample users for testing
def init_sample_data():
    """Initialize with 5 sample lawyers and 5 sample clients"""
    
    # Sample Lawyers
    lawyers = [
        {"id": "LAWYER-001", "name": "Sarah Mitchell", "email": "sarah.mitchell@lawfirm.com"},
        {"id": "LAWYER-002", "name": "David Chen", "email": "david.chen@lawfirm.com"},
        {"id": "LAWYER-003", "name": "Emily Rodriguez", "email": "emily.rodriguez@lawfirm.com"},
        {"id": "LAWYER-004", "name": "Michael Johnson", "email": "michael.johnson@lawfirm.com"},
        {"id": "LAWYER-005", "name": "Priya Sharma", "email": "priya.sharma@lawfirm.com"},
    ]
    
    for lawyer in lawyers:
        user_store.add_user(lawyer["id"], lawyer["email"], {
            'user_id': lawyer["id"],
            'email': lawyer["email"],
            'password': 'password123',
            'name': lawyer["name"],
            'phone': f'555-{lawyer["id"][-3:]}',
            'role': 'lawyer'
        })
    
    # Sample Clients
    clients = [
        {"id": "CLIENT-001", "name": "John Doe", "email": "john.doe@example.com"},
        {"id": "CLIENT-002", "name": "Jane Smith", "email": "jane.smith@example.com"},
        {"id": "CLIENT-003", "name": "Robert Brown", "email": "robert.brown@example.com"},
        {"id": "CLIENT-004", "name": "Lisa Anderson", "email": "lisa.anderson@example.com"},
        {"id": "CLIENT-005", "name": "Mark Wilson", "email": "mark.wilson@example.com"},
    ]
    
    for client in clients:
        user_store.add_user(client["id"], client["email"], {
            'user_id': client["id"],
            'email': client["email"],
            'password': 'password123',
            'name': client["name"],
            'phone': f'555-{client["id"][-3:]}',
            'role': 'client'
        })

init_sample_data()


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """Check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = user_store.get_user_by_id(session['user_id'])
            if not user or user.get('role') != role:
                return jsonify({'error': 'Unauthorized'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User/Lawyer login"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = user_store.get_user_by_email(email)
    
    # Simple password check (in production, use proper hashing)
    if not user or user.get('password') != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create session
    session['user_id'] = user['user_id']
    session['role'] = user['role']
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    })


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Client registration"""
    data = request.json
    
    required_fields = ['name', 'email', 'phone', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'All fields required'}), 400
    
    # Check if email exists
    if user_store.email_exists(data['email']):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new client
    user_id = f"CLIENT-{uuid.uuid4().hex[:8].upper()}"
    user_data = {
        'user_id': user_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'password': data['password'],  # Hash in production!
        'role': 'client',
        'created_at': datetime.now().isoformat()
    }
    
    user_store.add_user(user_id, data['email'], user_data)
    
    # Auto-login
    session['user_id'] = user_id
    session['role'] = 'client'
    
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'user_id': user_id,
            'name': user_data['name'],
            'email': user_data['email'],
            'role': 'client'
        }
    })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user"""
    user = user_store.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    })


# ============================================================================
# CLIENT ENDPOINTS
# ============================================================================

@app.route('/api/client/dashboard', methods=['GET'])
@login_required
@role_required('client')
def client_dashboard():
    """Get client dashboard data"""
    client_id = session['user_id']
    
    # Get active cases
    cases = case_store.get_cases_by_client(client_id)
    active_cases = [c for c in cases if c['status'] != 'closed']
    
    # Get notifications
    notifications = notification_manager.get_notifications(client_id)
    unread_count = notification_manager.get_unread_count(client_id)
    
    # Find next appointment (simplified)
    next_appointment = None
    for case in cases:
        case_id = case['case_id']
        # This is simplified - in real app, query appointments
        # For now, return placeholder
    
    return jsonify({
        'active_cases': active_cases[:5],  # Show first 5
        'total_cases': len(cases),
        'next_appointment': next_appointment,
        'unread_notifications': unread_count
    })


@app.route('/api/client/cases', methods=['GET', 'POST'])
@login_required
@role_required('client')
def client_cases():
    """Get all cases or create new case"""
    client_id = session['user_id']
    
    if request.method == 'GET':
        cases = case_store.get_cases_by_client(client_id)
        return jsonify({'cases': cases})
    
    elif request.method == 'POST':
        data = request.json
        
        case_type = data.get('case_type')
        description = data.get('description')
        urgency = data.get('urgency', False)
        assignment_type = data.get('assignment_type', 'general')  # 'general' or 'direct'
        requested_lawyer_id = data.get('lawyer_id')  # Only if assignment_type is 'direct'
        
        if not case_type or not description:
            return jsonify({'error': 'Case type and description required'}), 400
        
        # Create case
        case = case_manager.create_case(client_id, case_type, description, urgency)
        
        # Add additional fields for assignment
        case['assignment_type'] = assignment_type
        if assignment_type == 'direct' and requested_lawyer_id:
            case['requested_lawyer_id'] = requested_lawyer_id
        
        # Add to available cases pool
        available_cases_pool.add_to_pool(case)
        
        # Update case in store with lawyer if claimed/requested
        if assignment_type == 'direct' and requested_lawyer_id:
            # For direct assignment, notify the lawyer
            notification_manager.add_notification(
                requested_lawyer_id,
                'direct_assignment_request',
                f'New direct assignment request: {case["case_id"]}',
                case['case_id']
            )
        else:
            # For general pool, notify all lawyers
            all_users = list(user_store.users.values())
            for user in all_users:
                if user.get('role') == 'lawyer':
                    notification_manager.add_notification(
                        user['user_id'],
                        'new_available_case',
                        f'New {"urgent" if urgency else ""} case available: {case["case_id"]}',
                        case['case_id']
                    )
        
        return jsonify({'message': 'Case created', 'case': case}), 201


@app.route('/api/client/cases/<case_id>', methods=['GET'])
@login_required
@role_required('client')
def get_case_details(case_id):
    """Get case details"""
    client_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, client_id, 'client'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    # Get additional data
    messages = message_manager.get_messages(case_id)
    documents = document_store.get_documents_by_case(case_id)
    followups = followup_manager.get_followups(case_id)
    
    return jsonify({
        'case': case,
        'messages': messages,
        'documents': documents,
        'followups': followups
    })


@app.route('/api/client/cases/<case_id>/appointments', methods=['POST'])
@login_required
@role_required('client')
def request_appointment(case_id):
    """Request appointment for case"""
    client_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, client_id, 'client'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    preferred_datetime = data.get('preferred_datetime')
    
    if not preferred_datetime:
        return jsonify({'error': 'Preferred datetime required'}), 400
    
    # Get case to check urgency
    case = case_store.get_case(case_id)
    urgency = case.get('urgency', False)
    
    # Create appointment request
    appointment = appointment_manager.request_appointment(
        case_id, client_id, preferred_datetime, urgency
    )
    
    # Notify lawyer
    lawyer_id = case.get('lawyer_id')
    if lawyer_id:
        notification_manager.add_notification(
            lawyer_id,
            'appointment_request',
            f'New appointment request for case {case_id}',
            appointment['appointment_id']
        )
    
    return jsonify({
        'message': 'Appointment requested',
        'appointment': appointment
    }), 201


@app.route('/api/client/cases/<case_id>/messages', methods=['GET', 'POST'])
@login_required
@role_required('client')
def case_messages(case_id):
    """Get or send messages for case"""
    client_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, client_id, 'client'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        messages = message_manager.get_messages(case_id)
        return jsonify({'messages': messages})
    
    elif request.method == 'POST':
        data = request.json
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'Message content required'}), 400
        
        message = message_manager.send_message(case_id, client_id, 'client', content)
        
        # Notify lawyer
        case = case_store.get_case(case_id)
        if case and case.get('lawyer_id'):
            notification_manager.add_notification(
                case['lawyer_id'],
                'new_message',
                f'New message in case {case_id}',
                case_id
            )
        
        return jsonify({'message': 'Message sent', 'data': message}), 201


@app.route('/api/client/cases/<case_id>/documents', methods=['GET', 'POST'])
@login_required
@role_required('client')
def case_documents(case_id):
    """Get or upload documents for case"""
    client_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, client_id, 'client'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        documents = document_store.get_documents_by_case(case_id)
        return jsonify({'documents': documents})
    
    elif request.method == 'POST':
        data = request.json
        filename = data.get('filename')
        file_path = data.get('file_path')  # In real app, handle file upload
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        document = document_manager.upload_document(
            case_id, client_id, filename, file_path or 'uploads/' + filename
        )
        
        # Notify lawyer
        case = case_store.get_case(case_id)
        if case and case.get('lawyer_id'):
            notification_manager.add_notification(
                case['lawyer_id'],
                'new_document',
                f'New document uploaded in case {case_id}',
                case_id
            )
        
        return jsonify({'message': 'Document uploaded', 'document': document}), 201


# ============================================================================
# LAWYER ENDPOINTS
# ============================================================================

@app.route('/api/lawyer/dashboard', methods=['GET'])
@login_required
@role_required('lawyer')
def lawyer_dashboard():
    """Get lawyer dashboard data"""
    lawyer_id = session['user_id']
    
    # Get assigned cases
    cases = case_store.get_cases_by_lawyer(lawyer_id)
    urgent_cases = [c for c in cases if c.get('urgency')]
    
    # Get pending appointment requests
    pending_requests = appointment_manager.get_pending_requests()
    
    # Get notifications
    notifications = notification_manager.get_notifications(lawyer_id)
    unread_count = notification_manager.get_unread_count(lawyer_id)
    
    return jsonify({
        'total_cases': len(cases),
        'urgent_cases_count': len(urgent_cases),
        'pending_requests_count': len(pending_requests),
        'unread_notifications': unread_count,
        'urgent_cases': urgent_cases[:5]
    })


@app.route('/api/lawyer/consultation-requests', methods=['GET'])
@login_required
@role_required('lawyer')
def consultation_requests():
    """Get pending consultation requests"""
    pending = appointment_manager.get_pending_requests()
    return jsonify({'requests': pending})


@app.route('/api/lawyer/appointments/<appointment_id>/approve', methods=['POST'])
@login_required
@role_required('lawyer')
def approve_appointment(appointment_id):
    """Approve appointment request"""
    lawyer_id = session['user_id']
    data = request.json
    
    confirmed_datetime = data.get('confirmed_datetime')
    if not confirmed_datetime:
        return jsonify({'error': 'Confirmed datetime required'}), 400
    
    success, message = appointment_manager.approve_appointment(
        appointment_id, lawyer_id, confirmed_datetime
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    # Notify client
    appointment = appointment_manager.appointments.get(appointment_id)
    if appointment:
        notification_manager.add_notification(
            appointment['client_id'],
            'appointment_approved',
            f'Your appointment has been approved for {confirmed_datetime}',
            appointment_id
        )
    
    return jsonify({'message': message})


@app.route('/api/lawyer/appointments/<appointment_id>/reject', methods=['POST'])
@login_required
@role_required('lawyer')
def reject_appointment(appointment_id):
    """Reject appointment request"""
    data = request.json
    reason = data.get('reason', 'No reason provided')
    
    success = appointment_manager.reject_appointment(appointment_id, reason)
    if not success:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Notify client
    appointment = appointment_manager.appointments.get(appointment_id)
    if appointment:
        notification_manager.add_notification(
            appointment['client_id'],
            'appointment_rejected',
            f'Your appointment was rejected: {reason}',
            appointment_id
        )
    
    return jsonify({'message': 'Appointment rejected'})


@app.route('/api/lawyer/appointments/<appointment_id>/reschedule', methods=['POST'])
@login_required
@role_required('lawyer')
def reschedule_appointment(appointment_id):
    """Reschedule appointment"""
    data = request.json
    new_datetime = data.get('new_datetime')
    
    if not new_datetime:
        return jsonify({'error': 'New datetime required'}), 400
    
    success = appointment_manager.reschedule_appointment(appointment_id, new_datetime)
    if not success:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Notify client
    appointment = appointment_manager.appointments.get(appointment_id)
    if appointment:
        notification_manager.add_notification(
            appointment['client_id'],
            'appointment_rescheduled',
            f'Your appointment has been rescheduled to {new_datetime}',
            appointment_id
        )
    
    return jsonify({'message': 'Appointment rescheduled'})


@app.route('/api/lawyer/cases', methods=['GET'])
@login_required
@role_required('lawyer')
def lawyer_cases():
    """Get all assigned cases"""
    lawyer_id = session['user_id']
    cases = case_store.get_cases_by_lawyer(lawyer_id)
    return jsonify({'cases': cases})


@app.route('/api/lawyer/cases/<case_id>', methods=['GET'])
@login_required
@role_required('lawyer')
def lawyer_get_case(case_id):
    """Get case details"""
    lawyer_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    # Get additional data
    messages = message_manager.get_messages(case_id)
    documents = document_store.get_documents_by_case(case_id)
    followups = followup_manager.get_followups(case_id)
    
    return jsonify({
        'case': case,
        'messages': messages,
        'documents': documents,
        'followups': followups
    })


@app.route('/api/lawyer/cases/<case_id>/update', methods=['POST'])
@login_required
@role_required('lawyer')
def update_case(case_id):
    """Update case status"""
    lawyer_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    new_status = data.get('status')
    notes = data.get('notes', '')
    
    if not new_status:
        return jsonify({'error': 'Status required'}), 400
    
    success, message = case_manager.update_case_status(
        case_id, new_status, lawyer_id, notes
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    # Notify client
    case = case_store.get_case(case_id)
    if case:
        notification_manager.add_notification(
            case['client_id'],
            'case_update',
            f'Your case status has been updated to {new_status}',
            case_id
        )
    
    return jsonify({'message': message})


@app.route('/api/lawyer/cases/<case_id>/undo', methods=['POST'])
@login_required
@role_required('lawyer')
def undo_case_update(case_id):
    """Undo last case update"""
    lawyer_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    success, message = case_manager.undo_last_update(case_id)
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({'message': message})


@app.route('/api/lawyer/cases/<case_id>/followups', methods=['POST'])
@login_required
@role_required('lawyer')
def schedule_followup(case_id):
    """Schedule follow-up or hearing"""
    lawyer_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    followup_type = data.get('type')  # 'consultation' or 'hearing'
    scheduled_date = data.get('scheduled_date')
    notes = data.get('notes', '')
    
    if not followup_type or not scheduled_date:
        return jsonify({'error': 'Type and date required'}), 400
    
    followup = followup_manager.schedule_followup(
        case_id, lawyer_id, followup_type, scheduled_date, notes
    )
    
    # Notify client
    case = case_store.get_case(case_id)
    if case:
        notification_manager.add_notification(
            case['client_id'],
            'followup_scheduled',
            f'New {followup_type} scheduled for {scheduled_date}',
            case_id
        )
    
    return jsonify({'message': 'Follow-up scheduled', 'followup': followup}), 201


@app.route('/api/lawyer/cases/<case_id>/messages', methods=['GET', 'POST'])
@login_required
@role_required('lawyer')
def lawyer_case_messages(case_id):
    """Get or send messages for case (lawyer endpoint)"""
    lawyer_id = session['user_id']
    
    # Check access
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        messages = message_manager.get_messages(case_id)
        return jsonify({'messages': messages})
    
    elif request.method == 'POST':
        data = request.json
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'Message content required'}), 400
        
        message = message_manager.send_message(case_id, lawyer_id, 'lawyer', content)
        
        # Notify client
        case = case_store.get_case(case_id)
        if case:
            notification_manager.add_notification(
                case['client_id'],
                'new_message',
                f'New message from lawyer in case {case_id}',
                case_id
            )
        
        return jsonify({'message': 'Message sent', 'data': message}), 201


# NEW: Available Cases Pool Endpoints
@app.route('/api/lawyer/available-cases', methods=['GET'])
@login_required
@role_required('lawyer')
def get_available_cases():
    """Get all available cases in the pool"""
    available = available_cases_pool.get_available_cases()
    lawyer_id = session['user_id']
    case_count = available_cases_pool.get_lawyer_case_count(lawyer_id)
    
    return jsonify({
        'available_cases': available,
        'your_case_count': case_count,
        'max_cases': 2
    })


@app.route('/api/lawyer/pending-requests', methods=['GET'])
@login_required
@role_required('lawyer')
def get_pending_direct_requests():
    """Get pending direct assignment requests for this lawyer"""
    lawyer_id = session['user_id']
    requests = available_cases_pool.get_pending_requests(lawyer_id)
    
    return jsonify({'requests': requests})


@app.route('/api/lawyer/cases/<case_id>/claim', methods=['POST'])
@login_required
@role_required('lawyer')
def claim_case(case_id):
    """Claim a case from available pool"""
    lawyer_id = session['user_id']
    
    success, message = available_cases_pool.claim_case(case_id, lawyer_id)
    
    if not success:
        return jsonify({'error': message}), 400
    
    # Update case store with lawyer assignment
    case_manager.assign_lawyer(case_id, lawyer_id)
    
    # Update case status to 'in_review' when claimed
    case = case_store.get_case(case_id)
    if case and case['status'] == 'created':
        case['status'] = 'in_review'
        case['updated_at'] = datetime.now().isoformat()
        case_store.cases[case_id] = case
    
    # Notify client
    if case:
        notification_manager.add_notification(
            case['client_id'],
            'case_claimed',
            f'Your case has been claimed by a lawyer',
            case_id
        )
    
    return jsonify({'message': message})


@app.route('/api/lawyer/cases/<case_id>/unclaim', methods=['POST'])
@login_required
@role_required('lawyer')
def unclaim_case(case_id):
    """Un-claim a case, return it to pool"""
    lawyer_id = session['user_id']
    
    # Check if lawyer owns this case
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    success = available_cases_pool.unclaim_case(case_id, case)
    
    if not success:
        return jsonify({'error': 'Cannot unclaim case'}), 400
    
    # Remove lawyer assignment
    case_manager.assign_lawyer(case_id, None)
    
    # Reset status back to 'created'
    if case['status'] == 'in_review':
        case['status'] = 'created'
        case['updated_at'] = datetime.now().isoformat()
        case_store.cases[case_id] = case
    
    # Notify client
    notification_manager.add_notification(
        case['client_id'],
        'case_unclaimed',
        f'Your case is back in the available pool',
        case_id
    )
    
    return jsonify({'message': 'Case returned to pool'})


@app.route('/api/lawyer/requests/<case_id>/accept', methods=['POST'])
@login_required
@role_required('lawyer')
def accept_direct_request(case_id):
    """Accept a direct assignment request"""
    lawyer_id = session['user_id']
    
    success, message = available_cases_pool.accept_direct_request(case_id, lawyer_id)
    
    if not success:
        return jsonify({'error': message}), 400
    
    # Update case store
    case_manager.assign_lawyer(case_id, lawyer_id)
    
    # Notify client
    case = case_store.get_case(case_id)
    if case:
        notification_manager.add_notification(
            case['client_id'],
            'request_accepted',
            f'Your direct assignment request has been accepted',
            case_id
        )
    
    return jsonify({'message': message})


@app.route('/api/lawyer/requests/<case_id>/reject', methods=['POST'])
@login_required
@role_required('lawyer')
def reject_direct_request(case_id):
    """Reject direct request - goes to general pool"""
    lawyer_id = session['user_id']
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    success = available_cases_pool.reject_direct_request(case_id, lawyer_id, case)
    
    if not success:
        return jsonify({'error': 'Cannot reject request'}), 400
    
    # Notify client
    notification_manager.add_notification(
        case['client_id'],
        'request_rejected',
        f'Your direct assignment was rejected. Case is now in general pool.',
        case_id
    )
    
    return jsonify({'message': 'Request rejected, case moved to general pool'})


# NEW: Get all lawyers endpoint for client
@app.route('/api/lawyers', methods=['GET'])
@login_required
def get_all_lawyers():
    """Get list of all lawyers for selection"""
    all_users = list(user_store.users.values())
    lawyers = [
        {
            'user_id': u['user_id'],
            'name': u['name'],
            'email': u['email']
        }
        for u in all_users if u.get('role') == 'lawyer'
    ]
    return jsonify({'lawyers': lawyers})


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/queue-stats', methods=['GET'])
@login_required
def queue_stats():
    """Get queue statistics"""
    return jsonify({
        'normal_queue_length': appointment_manager.normal_queue.size(),
        'urgent_queue_length': appointment_manager.urgent_queue.size(),
        'total_pending': appointment_manager.normal_queue.size() + 
                        appointment_manager.urgent_queue.size()
    })


@app.route('/api/analytics/urgency-distribution', methods=['GET'])
@login_required
def urgency_distribution():
    """Get urgency distribution"""
    all_cases = list(case_store.cases.values())
    urgent_count = sum(1 for c in all_cases if c.get('urgency'))
    normal_count = len(all_cases) - urgent_count
    
    return jsonify({
        'total_cases': len(all_cases),
        'urgent_cases': urgent_count,
        'normal_cases': normal_count,
        'urgent_percentage': (urgent_count / len(all_cases) * 100) if all_cases else 0
    })


# ============================================================================
# START SERVER
# ============================================================================

if __name__ == '__main__':
    print("Legal Case Management System - Backend")
    print("Server starting on http://localhost:5000")
    app.run(debug=True, port=5000)
