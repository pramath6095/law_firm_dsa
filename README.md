# Law Firm Management System

A case management tool for law firms, built with Flask and vanilla HTML/CSS/JS. Clients can file cases, choose lawyers, and communicate through the portal. Lawyers can manage their caseload, update case statuses, and schedule follow-ups.

Uses custom data structures (hash tables, stacks, queues, priority queues) instead of Python builtins for educational purposes.

## Tech Stack

- **Backend:** Python 3.12, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Docker + Nginx

## Getting Started

### With Docker (recommended)

```bash
docker-compose up --build
```

Then open `http://localhost:8000` in your browser.

### Without Docker

**Backend:**
```bash
cd backend
pip install flask flask-cors
python app.py
```

**Frontend:**
```bash
cd frontend
python -m http.server 8000
```

Backend runs on port 5000, frontend on port 8000.

## Demo Accounts

All passwords are `password123`.

| Role   | Email          | Name            |
|--------|----------------|-----------------|
| Client | a@gmail.com    | John Doe        |
| Client | b@gmail.com    | Jane Smith      |
| Lawyer | a@lawfirm.com  | Sarah Mitchell  |
| Lawyer | b@lawfirm.com  | David Chen      |

You can also sign up as a new client from the login page.

## Project Structure

```
├── backend/
│   ├── app.py               # Flask API endpoints
│   ├── core_logic.py         # Business logic and managers
│   ├── data_structures.py    # Custom data structure implementations
│   ├── Dockerfile.backend
│   └── requirements.txt
├── frontend/
│   ├── client/               # Client-facing pages
│   ├── lawyer/               # Lawyer-facing pages
│   ├── app.js                # Shared JS utilities
│   ├── styles.css            # Global styles
│   ├── Dockerfile.frontend
│   └── nginx.conf
└── docker-compose.yml
```

## Features

- Case filing with lawyer selection and urgency calculation
- Lawyer dashboard with priority-sorted caseload
- In-case messaging between clients and lawyers
- Document uploads
- Follow-up and hearing scheduling
- Weekly calendar view
- Undo functionality for case status updates (stack-based)
- Notification system
- Available cases pool where lawyers can claim/unclaim cases

## Note

This is a demo project. Data is stored in memory (resets on restart), passwords are plaintext, and there's no real file storage. Not meant for production use.
