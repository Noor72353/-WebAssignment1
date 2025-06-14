# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

import datetime # new line added

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_change_this' # IMPORTANT: Change this to a long, random string!

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('users.db') # Connects to users.db in the same folder
    conn.row_factory = sqlite3.Row # This allows accessing columns by name (e.g., user['username'])
    return conn

# --- Routes (Web Pages) ---

@app.route('/')
def index():
    # Check if user is logged in for personalized greeting (optional)
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # REMINDER: In a real app, HASH passwords!

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. Check for existing user
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                # 2. Display "User already registered" message
                flash('User already registered. Please choose a different username.', 'error')
            else:
                # Store user data
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login')) # Redirect to login page

        except sqlite3.Error as e:
            flash(f'An database error occurred: {e}', 'error')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check credentials
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone() # Fetch one matching row
        conn.close()

        if user:
            flash('Login successful!', 'success')
            # Start a session for the user
            session['username'] = user['username']
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST']) # Allow POST requests
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Handle new comment submission (if method is POST)
    if request.method == 'POST':
        comment_text = request.form['comment_text']
        user_id = session['user_id']
        username = session['username'] # Get username from session

        if comment_text: # Ensure comment is not empty
            try:
                cursor.execute("INSERT INTO comments (user_id, username, comment_text) VALUES (?, ?, ?)",
                               (user_id, username, comment_text))
                conn.commit()
                flash('Comment posted successfully!', 'success')
            except sqlite3.Error as e:
                flash(f'Error posting comment: {e}', 'error')
        else:
            flash('Comment cannot be empty.', 'error')
        return redirect(url_for('dashboard')) # Redirect to prevent form resubmission on refresh

    # Fetch all comments for display (for GET requests or after POST redirect)
    comments = cursor.execute("SELECT username, comment_text, timestamp FROM comments ORDER BY timestamp DESC").fetchall()
    conn.close()

    return render_template('dashboard.html', username=session['username'], comments=comments)

@app.route('/logout')
def logout():
    session.pop('username', None) # Remove username from session
    session.pop('user_id', None)   # Remove user_id from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('index')) # Redirect to home page

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True) # debug=True restarts server on code changes and shows errors