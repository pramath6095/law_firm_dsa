from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import uuid
import os

from data_structures import CaseStore, UserStore, DocumentStore
from core_logic import (
    CaseManager, MessageManager,
    DocumentManager, FollowUpManager, NotificationManager,
    EventManager, AvailableCasesPool
)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

CORS(app, 
     origins=['http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost:5000', 'http://127.0.0.1:5000'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# data stores
user_store = UserStore()
case_store = CaseStore()
document_store = DocumentStore()

# managers
case_manager = CaseManager(case_store)
message_manager = MessageManager()
document_manager = DocumentManager(document_store, case_store)
followup_manager = FollowUpManager()
notification_manager = NotificationManager()
event_manager = EventManager(case_store)
available_cases_pool = AvailableCasesPool()

FIRM_CONTACT_INFO = {
    'phone': '+1-555-LAW-FIRM',
    'email': 'contact@premierlegalpartners.com',
    'message': 'All our specialists in this practice area are currently at capacity. Please contact us to discuss your case.'
}


def init_sample_data():
    lawyers = [
        {
            "id": "LAWYER-001", 
            "name": "Sarah Mitchell", 
            "email": "a@lawfirm.com",
            "speciality": ["Civil Law", "Criminal Law"],
            "cost_per_hearing": 5000.00
        },
        {
            "id": "LAWYER-002", 
            "name": "David Chen", 
            "email": "b@lawfirm.com",
            "speciality": ["Civil Law", "Criminal Law"],
            "cost_per_hearing": 5500.00
        },
        {
            "id": "LAWYER-003", 
            "name": "Emily Rodriguez", 
            "email": "c@lawfirm.com",
            "speciality": ["Family Law"],
            "cost_per_hearing": 3500.00
        },
        {
            "id": "LAWYER-004", 
            "name": "Michael Johnson", 
            "email": "d@lawfirm.com",
            "speciality": ["Corporate Law"],
            "cost_per_hearing": 4500.00
        },
        {
            "id": "LAWYER-005", 
            "name": "Priya Sharma", 
            "email": "e@lawfirm.com",
            "speciality": ["Property Law"],
            "cost_per_hearing": 6000.00
        },
    ]
    
    for lawyer in lawyers:
        user_store.add_user(lawyer["id"], lawyer["email"], {
            'user_id': lawyer["id"],
            'email': lawyer["email"],
            'password': 'password123',
            'name': lawyer["name"],
            'phone': f'555-{lawyer["id"][-3:]}',
            'role': 'lawyer',
            'speciality': lawyer["speciality"],
            'cost_per_hearing': lawyer["cost_per_hearing"]
        })
    
    clients = [
        {"id": "CLIENT-001", "name": "John Doe", "email": "a@gmail.com"},
        {"id": "CLIENT-002", "name": "Jane Smith", "email": "b@gmail.com"},
        {"id": "CLIENT-003", "name": "Robert Brown", "email": "c@gmail.com"},
        {"id": "CLIENT-004", "name": "Lisa Anderson", "email": "d@gmail.com"},
        {"id": "CLIENT-005", "name": "Mark Wilson", "email": "e@gmail.com"},
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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
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


# auth endpoints

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = user_store.get_user_by_email(email)
    
    if not user or user.get('password') != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
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
    data = request.json
    
    required_fields = ['name', 'email', 'phone', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'All fields required'}), 400
    
    if user_store.email_exists(data['email']):
        return jsonify({'error': 'Email already registered'}), 400
    
    user_id = f"CLIENT-{uuid.uuid4().hex[:8].upper()}"
    user_data = {
        'user_id': user_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'password': data['password'],
        'role': 'client',
        'created_at': datetime.now().isoformat()
    }
    
    user_store.add_user(user_id, data['email'], user_data)
    
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
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    user = user_store.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    })


@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    user_id = session['user_id']
    user = user_store.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        profile_data = {
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'role': user['role']
        }
        
        if user['role'] == 'lawyer':
            profile_data['speciality'] = user.get('speciality', [])
            profile_data['cost_per_hearing'] = user.get('cost_per_hearing', 0)
        
        return jsonify(profile_data)
    
    elif request.method == 'PUT':
        data = request.json
        
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        
        if not name or len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        user['name'] = name
        user['phone'] = phone
        
        if user['role'] == 'lawyer' and 'speciality' in data:
            speciality = data.get('speciality')
            if isinstance(speciality, list):
                user['speciality'] = speciality
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'role': user['role']
            }
        })


# client endpoints

@app.route('/api/client/dashboard', methods=['GET'])
@login_required
@role_required('client')
def client_dashboard():
    client_id = session['user_id']
    
    cases = case_store.get_cases_by_client(client_id)
    active_cases = [c for c in cases if c['status'] != 'closed']
    
    notifications = notification_manager.get_notifications(client_id)
    unread_count = notification_manager.get_unread_count(client_id)
    
    next_appointment = None
    for case in cases:
        case_id = case['case_id']
    
    return jsonify({
        'active_cases': active_cases[:5],
        'total_cases': len(cases),
        'next_appointment': next_appointment,
        'unread_notifications': unread_count
    })


@app.route('/api/lawyers', methods=['GET'])
def get_lawyers():
    all_lawyers = [u for u in user_store.get_all_users() if u.get('role') == 'lawyer']
    
    lawyers_with_counts = []
    for lawyer in all_lawyers:
        lawyer_data = {
            'user_id': lawyer['user_id'],
            'name': lawyer['name'],
            'email': lawyer.get('email'),
            'speciality': lawyer.get('speciality', 'General Law'),
            'cost_per_hearing': lawyer.get('cost_per_hearing', 0),
            'active_cases': case_manager.get_lawyer_case_count(lawyer['user_id'])
        }
        lawyers_with_counts.append(lawyer_data)
    
    return jsonify({'lawyers': lawyers_with_counts})


@app.route('/api/client/cases', methods=['GET', 'POST'])
@login_required
@role_required('client')
def client_cases():
    client_id = session['user_id']
    
    if request.method == 'GET':
        cases = case_store.get_cases_by_client(client_id)
        
        # bubble sort by priority_score (lower = more urgent)
        n = 0
        for _ in cases:
            n = n + 1
        
        for i in range(n):
            for j in range(0, n - i - 1):
                score_j = cases[j].get('priority_score', 999)
                score_j1 = cases[j + 1].get('priority_score', 999)
                if score_j > score_j1:
                    temp = cases[j]
                    cases[j] = cases[j + 1]
                    cases[j + 1] = temp
        
        return jsonify({'cases': cases})
    
    elif request.method == 'POST':
        data = request.json
        
        case_type = data.get('case_type')
        description = data.get('description')
        hearing_date = data.get('hearing_date')
        selected_lawyer_id = data.get('lawyer_id')
        speciality = data.get('speciality')
        
        if not all([case_type, description, hearing_date, selected_lawyer_id, speciality]):
            return jsonify({'error': 'All fields required: case_type, description, hearing_date, lawyer_id, speciality'}), 400
        
        # need at least 50 words in description
        words = [word for word in description.split() if word.strip()]
        word_count = len(words)
        
        if word_count < 50:
            return jsonify({
                'error': f'Description must be at least 50 words. Current: {word_count} words.',
                'word_count': word_count,
                'required': 50
            }), 400
        
        result_type, case, extra = case_manager.create_case_with_assignment(
            client_id, case_type, description, hearing_date,
            selected_lawyer_id, speciality, user_store
        )
        
        if result_type == 'success':
            notification_manager.add_notification(
                selected_lawyer_id, 'new_case_assigned',
                f'New case assigned: {case["case_id"]} ({case["urgency_level"]} priority) - Hearing in {case["days_until_hearing"]} days',
                case['case_id']
            )
            return jsonify({
                'message': 'Case created and assigned successfully',
                'case': case,
                'assigned_to': selected_lawyer_id,
                'assignment_status': 'success'
            }), 201
        
        elif result_type == 'auto_assigned':
            alternative_lawyer = extra
            notification_manager.add_notification(
                alternative_lawyer['user_id'], 'new_case_assigned',
                f'New case auto-assigned: {case["case_id"]} ({case["urgency_level"]} priority) - Hearing in {case["days_until_hearing"]} days',
                case['case_id']
            )
            return jsonify({
                'message': f'Your selected lawyer is busy. Case assigned to {alternative_lawyer["name"]}.',
                'case': case,
                'assigned_to': alternative_lawyer['user_id'],
                'assigned_to_name': alternative_lawyer['name'],
                'assignment_status': 'auto_assigned'
            }), 201
        
        else:
            return jsonify({
                'error': 'all_specialists_busy',
                'message': FIRM_CONTACT_INFO['message'],
                'contact': {
                    'phone': FIRM_CONTACT_INFO['phone'],
                    'email': FIRM_CONTACT_INFO['email']
                }
            }), 503


@app.route('/api/client/cases/<case_id>', methods=['GET'])
@login_required
@role_required('client')
def get_case_details(case_id):
    client_id = session['user_id']
    
    if not case_manager.check_access(case_id, client_id, 'client'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    messages = message_manager.get_messages(case_id)
    documents = document_store.get_documents_by_case(case_id)
    followups = followup_manager.get_followups(case_id)
    
    return jsonify({
        'case': case,
        'messages': messages,
        'documents': documents,
        'followups': followups
    })


@app.route('/api/client/cases/<case_id>/messages', methods=['GET', 'POST'])
@login_required
@role_required('client')
def case_messages(case_id):
    client_id = session['user_id']
    
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
    client_id = session['user_id']
    
    if not case_manager.check_access(case_id, client_id, 'client'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        documents = document_store.get_documents_by_case(case_id)
        return jsonify({'documents': documents})
    
    elif request.method == 'POST':
        data = request.json
        filename = data.get('filename')
        file_path = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        document = document_manager.upload_document(
            case_id, client_id, filename, file_path or 'uploads/' + filename
        )
        
        case = case_store.get_case(case_id)
        if case and case.get('lawyer_id'):
            notification_manager.add_notification(
                case['lawyer_id'],
                'new_document',
                f'New document uploaded in case {case_id}',
                case_id
            )
        
        return jsonify({'message': 'Document uploaded', 'document': document}), 201


# lawyer endpoints

@app.route('/api/lawyer/dashboard', methods=['GET'])
@login_required
@role_required('lawyer')
def lawyer_dashboard():
    lawyer_id = session['user_id']
    
    cases = case_store.get_cases_by_lawyer(lawyer_id)
    
    cases_with_hearings = [c for c in cases if c.get('days_until_hearing') is not None]
    cases_with_hearings.sort(key=lambda c: c.get('priority_score', 999))
    
    urgent_cases = [c for c in cases_with_hearings if c.get('urgency_level') == 'urgent']
    
    notifications = notification_manager.get_notifications(lawyer_id)
    unread_count = notification_manager.get_unread_count(lawyer_id)
    
    return jsonify({
        'total_cases': len(cases),
        'urgent_cases_count': len(urgent_cases),
        'unread_notifications': unread_count,
        'urgent_cases': urgent_cases[:5]
    })


@app.route('/api/lawyer/cases', methods=['GET'])
@login_required
@role_required('lawyer')
def lawyer_cases():
    lawyer_id = session['user_id']
    cases = case_store.get_cases_by_lawyer(lawyer_id)
    return jsonify({'cases': cases})


@app.route('/api/lawyer/cases/<case_id>', methods=['GET'])
@login_required
@role_required('lawyer')
def lawyer_get_case(case_id):
    lawyer_id = session['user_id']
    
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
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
    lawyer_id = session['user_id']
    
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
    lawyer_id = session['user_id']
    
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
    lawyer_id = session['user_id']
    
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    followup_type = data.get('type')
    scheduled_date = data.get('scheduled_date')
    notes = data.get('notes', '')
    
    if not followup_type or not scheduled_date:
        return jsonify({'error': 'Type and date required'}), 400
    
    followup = followup_manager.schedule_followup(
        case_id, lawyer_id, followup_type, scheduled_date, notes
    )
    
    case = case_store.get_case(case_id)
    if case:
        event_manager.add_event(
            case_id=case_id,
            event_type='followup',
            date=scheduled_date,
            description=f"{followup_type.capitalize()}: {notes if notes else 'Follow-up appointment'}",
            created_by=lawyer_id
        )
        
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
    lawyer_id = session['user_id']
    
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
        
        case = case_store.get_case(case_id)
        if case:
            notification_manager.add_notification(
                case['client_id'],
                'new_message',
                f'New message from lawyer in case {case_id}',
                case_id
            )
        
        return jsonify({'message': 'Message sent', 'data': message}), 201


# available cases pool endpoints

@app.route('/api/lawyer/available-cases', methods=['GET'])
@login_required
@role_required('lawyer')
def get_available_cases():
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
    lawyer_id = session['user_id']
    requests = available_cases_pool.get_pending_requests(lawyer_id)
    return jsonify({'requests': requests})


@app.route('/api/lawyer/cases/<case_id>/claim', methods=['POST'])
@login_required
@role_required('lawyer')
def claim_case(case_id):
    lawyer_id = session['user_id']
    
    success, message = available_cases_pool.claim_case(case_id, lawyer_id)
    
    if not success:
        return jsonify({'error': message}), 400
    
    case_manager.assign_lawyer(case_id, lawyer_id)
    
    case = case_store.get_case(case_id)
    if case and case['status'] == 'created':
        case['status'] = 'in_review'
        case['updated_at'] = datetime.now().isoformat()
        case_store.cases[case_id] = case
    
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
    lawyer_id = session['user_id']
    
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    success = available_cases_pool.unclaim_case(case_id, case)
    
    if not success:
        return jsonify({'error': 'Cannot unclaim case'}), 400
    
    case_manager.assign_lawyer(case_id, None)
    
    if case['status'] == 'in_review':
        case['status'] = 'created'
        case['updated_at'] = datetime.now().isoformat()
        case_store.cases[case_id] = case
    
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
    lawyer_id = session['user_id']
    
    success, message = available_cases_pool.accept_direct_request(case_id, lawyer_id)
    
    if not success:
        return jsonify({'error': message}), 400
    
    case_manager.assign_lawyer(case_id, lawyer_id)
    
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
    lawyer_id = session['user_id']
    
    case = case_store.get_case(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    success = available_cases_pool.reject_direct_request(case_id, lawyer_id, case)
    
    if not success:
        return jsonify({'error': 'Cannot reject request'}), 400
    
    notification_manager.add_notification(
        case['client_id'],
        'request_rejected',
        f'Your direct assignment was rejected. Case is now in general pool.',
        case_id
    )
    
    return jsonify({'message': 'Request rejected, case moved to general pool'})


@app.route('/api/lawyers', methods=['GET'])
@login_required
def get_all_lawyers():
    all_users = user_store.get_all_users()
    lawyers = [
        {
            'user_id': u['user_id'],
            'name': u['name'],
            'email': u['email']
        }
        for u in all_users if u.get('role') == 'lawyer'
    ]
    return jsonify({'lawyers': lawyers})


# analytics


@app.route('/api/analytics/urgency-distribution', methods=['GET'])
@login_required
def urgency_distribution():
    all_cases = case_store.get_all_cases()
    urgent_count = sum(1 for c in all_cases if c.get('urgency'))
    normal_count = len(all_cases) - urgent_count
    
    return jsonify({
        'total_cases': len(all_cases),
        'urgent_cases': urgent_count,
        'normal_cases': normal_count,
        'urgent_percentage': (urgent_count / len(all_cases) * 100) if all_cases else 0
    })


# calendar

@app.route('/api/calendar/week', methods=['GET'])
@login_required
def get_weekly_calendar():
    user_id = session['user_id']
    role = session['role']
    
    start_date_str = request.args.get('start_date')
    start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
    
    events = event_manager.get_weekly_events(user_id, role, start_date)
    
    return jsonify({
        'events': events,
        'week_start': (start_date or datetime.now()).strftime('%Y-%m-%d')
    })


@app.route('/api/cases/<case_id>/events', methods=['POST'])
@login_required
@role_required('lawyer')
def create_event(case_id):
    data = request.json
    lawyer_id = session['user_id']
    
    if not case_manager.check_access(case_id, lawyer_id, 'lawyer'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    event = event_manager.add_event(
        case_id,
        data.get('event_type'),
        data.get('date'),
        data.get('description'),
        lawyer_id
    )
    
    case = case_store.get_case(case_id)
    notification_manager.add_notification(
        case['client_id'],
        f'new_{event["event_type"]}',
        f'New {event["event_type"]} scheduled for {event["date"]}',
        case_id
    )
    
    return jsonify({'event': event}), 201


if __name__ == '__main__':
    print("Legal Case Management System - Backend")
    print("Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
