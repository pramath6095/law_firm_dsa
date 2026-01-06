# Running on Local Network (Access from Other Devices)

This guide shows how to access the application from other devices on the same WiFi/network.

---

## 📋 Prerequisites

1. Host PC and other devices must be on the **same WiFi network**
2. Windows Firewall must allow the connections

---

## Step 1: Find Your Host PC's IP Address

### On Windows:
```bash
ipconfig
```

Look for **IPv4 Address** under your active network adapter (WiFi or Ethernet):
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100  <-- This one!
```

Example IPs: `192.168.1.100`, `192.168.0.50`, `10.0.0.25`

**Write this down!** Let's call it `HOST_IP`

---

## Step 2: Update Backend to Accept Network Connections

### Option A: Command Line (Temporary)

Edit `backend/app.py`, find the last line:
```python
app.run(debug=True, port=5000)
```

Change to:
```python
app.run(host='0.0.0.0', debug=True, port=5000)
```

This allows connections from any device on the network.

---

## Step 3: Update Frontend API URL

Edit `frontend/app.js`, find line 6:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

Change to your host IP:
```javascript
const API_BASE_URL = 'http://192.168.1.100:5000/api';  // Use YOUR IP!
```

---

## Step 4: Update Backend CORS Configuration

Edit `backend/app.py`, find the CORS section (around line 30):

```python
CORS(app, 
     origins=['http://localhost:8000', 'http://127.0.0.1:8000'],
     supports_credentials=True,
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

Change to:
```python
CORS(app, 
     origins=[
         'http://localhost:8000', 
         'http://127.0.0.1:8000',
         'http://192.168.1.100:8000',  # Use YOUR IP!
         'http://*:8000'  # Allow all devices on port 8000
     ],
     supports_credentials=True,
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

---

## Step 5: Configure Windows Firewall

### Allow Python through Firewall:

1. **Open Windows Defender Firewall**
   - Search "Windows Defender Firewall" in Start menu
   - Click "Allow an app through firewall"

2. **Add Python:**
   - Click "Change settings" (needs admin)
   - Click "Allow another app..."
   - Browse to: `C:\Users\[YourName]\AppData\Local\Programs\Python\Python3XX\python.exe`
   - Check both "Private" and "Public"
   - Click "Add"

### Alternative: Create Firewall Rules (Advanced)

```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "Python Flask Backend" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "Python HTTP Server Frontend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## Step 6: Start the Servers

### Terminal 1 - Backend:
```bash
cd backend
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

### Terminal 2 - Frontend:
```bash
cd frontend
python -m http.server 8000
```

---

## Step 7: Access from Other Devices

On your **phone, tablet, or another PC** (same WiFi):

### Client Portal:
```
http://192.168.1.100:8000/client/login.html
```

### Lawyer Portal:
```
http://192.168.1.100:8000/lawyer/login.html
```

**Replace `192.168.1.100` with YOUR actual host IP!**

---

## 🔧 Troubleshooting

### Can't Connect from Other Device?

**1. Verify connectivity:**
```bash
# From other device, ping host
ping 192.168.1.100
```

**2. Check firewall:**
- Temporarily disable Windows Firewall to test
- If it works, re-enable and add proper rules

**3. Check antivirus:**
- Some antivirus software blocks network access
- Add Python to allowed apps

**4. Check router:**
- AP Isolation might be enabled (common in public WiFi)
- Devices can't communicate with each other

### CORS Errors?
- Make sure you updated CORS origins in `app.py`
- Restart backend after changes

### Session Issues?
- Sessions work best on same device
- Use different browsers on different devices

---

## 📱 Testing on Mobile

1. Connect phone to same WiFi
2. Open browser
3. Go to `http://192.168.1.100:8000/client/login.html`
4. Login and test!

---

## 🔒 Security Note

**WARNING:** This configuration allows anyone on your network to access the app!

For production:
- Use HTTPS with proper certificates
- Implement proper authentication
- Use a production WSGI server (not Flask dev server)
- Hash passwords properly
- Add rate limiting

This setup is for **development/demo only!**

---

## 🎯 Quick Summary

1. Find host IP: `ipconfig`
2. Edit `backend/app.py`: Change to `host='0.0.0.0'`
3. Edit `frontend/app.js`: Change `API_BASE_URL` to host IP
4. Edit `backend/app.py`: Add host IP to CORS origins
5. Allow Python through firewall
6. Start both servers
7. Access from other device: `http://HOST_IP:8000/client/login.html`

---

## 💡 Reverting to Localhost

To go back to localhost-only:
1. Change `app.run(host='0.0.0.0')` back to `app.run()`
2. Change `API_BASE_URL` back to `http://localhost:5000/api`
3. Remove extra CORS origins
