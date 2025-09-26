from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
import bcrypt
from datetime import datetime

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id, username, is_admin, password FROM users WHERE username=%s",
                    (username,)
                )
                user = cursor.fetchone()
        finally:
            conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # store user info in session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])  # cast to bool

            # go to correct dashboard
            if session['is_admin']:
                return redirect(url_for('admin'))   # admin route in app.py
            else:
                
                return redirect(url_for('main'))  # or your user page route
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('login_bp.login'))

    return render_template('login.html')


@login_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_bp.login'))
