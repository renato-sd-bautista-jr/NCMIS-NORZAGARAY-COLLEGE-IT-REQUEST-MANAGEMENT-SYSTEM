from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
 
import pymysql
from datetime import datetime 


now = datetime.now()

userborrow_bp = Blueprint('userborrow_bp', __name__, url_prefix='/borrow')

@userborrow_bp.route('/', methods=['GET', 'POST'])
def borrow_page():
    print(">>> borrow_page route was hit")
    if request.method == 'POST':
        conn = get_db_connection()
        user_id = session.get('user_id')
        device_id = request.form['item_id']
        borrow_date = request.form['borrow_date']
        borrow_time = request.form['borrow_time']
        return_time = request.form['return_time']
        reason = request.form['reason']

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO borrow_requests
                  (user_id, device_id, borrow_date, reason, status)
                VALUES (%s,%s,%s,%s,'Pending')
            """, (user_id, device_id, borrow_date, reason))
        conn.commit()
        conn.close()

        flash('Request submitted!')
        return redirect(url_for('userborrow_bp.borrow_page'))

    # ✅ get available devices as dictionaries
    items = get_available_devices()
    print("DEBUG available items:", items)
    now = datetime.now()
    return render_template('main.html', items=items, now=now)

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
