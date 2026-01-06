/**
 * Shared JavaScript utilities for Legal Case Management System
 * Handles API communication, session management, and utilities
 */

const API_BASE_URL = 'http://localhost:5000/api';

// Session management
class Session {
    static getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    static setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    }

    static clearUser() {
        localStorage.removeItem('user');
    }

    static isLoggedIn() {
        return this.getUser() !== null;
    }

    static getUserRole() {
        const user = this.getUser();
        return user ? user.role : null;
    }
}

// API communication
class API {
    static async request(endpoint, options = {}) {
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        if (finalOptions.body && typeof finalOptions.body === 'object') {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, finalOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    static async login(email, password) {
        return await this.request('/auth/login', {
            method: 'POST',
            body: { email, password }
        });
    }

    static async signup(name, email, phone, password) {
        return await this.request('/auth/signup', {
            method: 'POST',
            body: { name, email, phone, password }
        });
    }

    static async logout() {
        return await this.request('/auth/logout', { method: 'POST' });
    }

    static async getCurrentUser() {
        return await this.request('/auth/me');
    }

    // Client endpoints
    static async getClientDashboard() {
        return await this.request('/client/dashboard');
    }

    static async getClientCases() {
        return await this.request('/client/cases');
    }

    static async createCase(caseData) {
        return await this.request('/client/cases', {
            method: 'POST',
            body: caseData
        });
    }

    static async getCaseDetails(caseId) {
        return await this.request(`/client/cases/${caseId}`);
    }

    static async requestAppointment(caseId, preferredDatetime) {
        return await this.request(`/client/cases/${caseId}/appointments`, {
            method: 'POST',
            body: { preferred_datetime: preferredDatetime }
        });
    }

    static async getCaseMessages(caseId) {
        return await this.request(`/client/cases/${caseId}/messages`);
    }

    static async sendMessage(caseId, content) {
        return await this.request(`/client/cases/${caseId}/messages`, {
            method: 'POST',
            body: { content }
        });
    }

    static async getCaseDocuments(caseId) {
        return await this.request(`/client/cases/${caseId}/documents`);
    }

    static async uploadDocument(caseId, filename, filePath) {
        return await this.request(`/client/cases/${caseId}/documents`, {
            method: 'POST',
            body: { filename, file_path: filePath }
        });
    }

    // Lawyer endpoints
    static async getLawyerDashboard() {
        return await this.request('/lawyer/dashboard');
    }

    static async getConsultationRequests() {
        return await this.request('/lawyer/consultation-requests');
    }

    static async approveAppointment(appointmentId, confirmedDatetime) {
        return await this.request(`/lawyer/appointments/${appointmentId}/approve`, {
            method: 'POST',
            body: { confirmed_datetime: confirmedDatetime }
        });
    }

    static async rejectAppointment(appointmentId, reason) {
        return await this.request(`/lawyer/appointments/${appointmentId}/reject`, {
            method: 'POST',
            body: { reason }
        });
    }

    static async rescheduleAppointment(appointmentId, newDatetime) {
        return await this.request(`/lawyer/appointments/${appointmentId}/reschedule`, {
            method: 'POST',
            body: { new_datetime: newDatetime }
        });
    }

    static async getLawyerCases() {
        return await this.request('/lawyer/cases');
    }

    static async getLawyerCaseDetails(caseId) {
        return await this.request(`/lawyer/cases/${caseId}`);
    }

    static async updateCase(caseId, status, notes) {
        return await this.request(`/lawyer/cases/${caseId}/update`, {
            method: 'POST',
            body: { status, notes }
        });
    }

    static async undoCaseUpdate(caseId) {
        return await this.request(`/lawyer/cases/${caseId}/undo`, {
            method: 'POST'
        });
    }

    static async scheduleFollowup(caseId, type, scheduledDate, notes) {
        return await this.request(`/lawyer/cases/${caseId}/followups`, {
            method: 'POST',
            body: { type, scheduled_date: scheduledDate, notes }
        });
    }

    static async sendLawyerMessage(caseId, content) {
        return await this.request(`/lawyer/cases/${caseId}/messages`, {
            method: 'POST',
            body: { content }
        });
    }

    // NEW: Law Firm Portal Endpoints
    static async getAllLawyers() {
        return await this.request('/lawyers');
    }

    static async getAvailableCases() {
        return await this.request('/lawyer/available-cases');
    }

    static async getPendingRequests() {
        return await this.request('/lawyer/pending-requests');
    }

    static async claimCase(caseId) {
        return await this.request(`/lawyer/cases/${caseId}/claim`, {
            method: 'POST'
        });
    }

    static async unclaimCase(caseId) {
        return await this.request(`/lawyer/cases/${caseId}/unclaim`, {
            method: 'POST'
        });
    }

    static async acceptDirectRequest(caseId) {
        return await this.request(`/lawyer/requests/${caseId}/accept`, {
            method: 'POST'
        });
    }

    static async rejectDirectRequest(caseId) {
        return await this.request(`/lawyer/requests/${caseId}/reject`, {
            method: 'POST'
        });
    }

    // Analytics
    static async getQueueStats() {
        return await this.request('/analytics/queue-stats');
    }

    static async getUrgencyDistribution() {
        return await this.request('/analytics/urgency-distribution');
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 5000);
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatStatus(status) {
    return status.replace('_', ' ').toUpperCase();
}

// Tab management
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;

            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });
}

// Auth check redirect
function requireAuth(allowedRole = null) {
    const user = Session.getUser();

    if (!user) {
        // Not logged in - redirect to client login
        if (window.location.pathname.includes('/lawyer/')) {
            window.location.href = '../lawyer/login.html';
        } else {
            window.location.href = '../client/login.html';
        }
        return false;
    }

    if (allowedRole && user.role !== allowedRole) {
        // Wrong role - redirect to correct portal
        if (user.role === 'lawyer') {
            window.location.href = '../lawyer/dashboard.html';
        } else {
            window.location.href = '../client/dashboard.html';
        }
        return false;
    }

    return true;
}

// Logout
async function handleLogout() {
    try {
        await API.logout();
        Session.clearUser();
        window.location.href = '../client/login.html';
    } catch (error) {
        console.error('Logout error:', error);
        // Force logout anyway
        Session.clearUser();
        window.location.href = '../client/login.html';
    }
}
