# Session Conflict Issue - Workaround

## Problem
When both client and lawyer login in the same browser, Flask sessions conflict because they share the same session cookie.

## Solutions

### ✅ Solution 1: Use Different Browsers (Recommended)
- **Client**: Chrome
- **Lawyer**: Firefox/Edge

### ✅ Solution 2: Use Incognito/Private Windows
- **Client**: Regular window
- **Lawyer**: Incognito/Private window

### ✅ Solution 3: Use Browser Profiles
Chrome/Edge support multiple profiles:
1. Click profile icon → "Add"
2. Create "Client" and "Lawyer" profiles
3. Login to each in their respective profile

### ⚠️ Why This Happens
Flask uses cookies for sessions. Since both portals run on `localhost:8000`, they share the same session cookie. When you login as lawyer after client, the session gets overwritten.

### 🔧 Technical Fix (Advanced)
If you want both in same browser/tab:
1. Use different domains (e.g., `client.localhost` and `lawyer.localhost`)
2. Or use token-based auth instead of sessions
3. Or run on different ports with separate CORS configs

**For this demo, using different browsers or incognito is the simplest solution.**

---

## New Features Added

### 1. ✅ Reject Case Button
- Sends claimed case back to general pool
- Available to all lawyers
- Requires rejection reason

### 2. ✅ Mark as Completed Button
- Changes case status to "closed"
- Removes from active cases
- Decreases lawyer case count

### 3. ✅ Improved Role-Based Redirects
- Client trying to access lawyer pages → redirected to client dashboard
- Lawyer trying to access client pages → redirected to lawyer dashboard
