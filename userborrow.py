from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
 
import pymysql
from datetime import datetime 


now = datetime.now()

userborrow_bp = Blueprint('userborrow_bp', __name__, url_prefix='/borrow')

@userborrow_bp.route('/', methods=['GET', 'POST'])
def borrow_page():
    if request.method == 'POST':
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_initial = request.form['middle_initial']
        student_id = request.form['student_id']
        device_id = request.form['item_id']
        reason = request.form['reason']
        borrow_date = datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        with conn.cursor() as cur:
            # Insert student if not exists
            cur.execute("""
                INSERT IGNORE INTO students (student_id, last_name, first_name, middle_initial)
                VALUES (%s, %s, %s, %s)
            """, (student_id, last_name, first_name, middle_initial))
            # Insert borrow request
            cur.execute("""
                INSERT INTO borrow_requests
                  (student_id, last_name, first_name, middle_initial, device_id, borrow_date, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (student_id, last_name, first_name, middle_initial, device_id, borrow_date, reason))
        conn.commit()
        conn.close()
        flash('Request submitted!')
        return redirect(url_for('userborrow_bp.borrow_page'))

    items = get_available_devices()
    # Fetch students for the table
    students = []
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
    conn.close()
    now = datetime.now()
    return render_template('main.html', items=items, students=students, now=now)


@userborrow_bp.route('/decline/<int:borrow_id>', methods=['POST'])
def cancel_request(borrow_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE borrow_requests
            SET status='Cancelled'
            WHERE borrow_id=%s AND user_id=%s AND status='Pending'
        """, (borrow_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Request cancelled')
    return redirect(url_for('userborrow_bp.borrow_page'))

def get_available_devices():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                d.device_id AS id,
                d.item_name AS name,
                d.serial_number,
                dep.department_name AS department
            FROM devices d
            JOIN departments dep ON d.department_id = dep.department_id
            WHERE d.status = 'Available'
        """)
        devices = cur.fetchall()
    conn.close()
    return devices


@userborrow_bp.route('/return/<int:borrow_id>', methods=['POST'])

def mark_returned_borrow_request(borrow_id,now=now):

    
   
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE borrow_requests
            SET status = 'Returned', return_date = now()
             WHERE borrow_id=%s AND user_id=%s AND status='Approved'
        """, (borrow_id,))
    conn.commit()
    conn.close()
    flash('Item marked as returned.')
    return redirect(url_for('admin'))        
