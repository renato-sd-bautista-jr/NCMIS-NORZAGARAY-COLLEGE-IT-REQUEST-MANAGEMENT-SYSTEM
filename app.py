from flask import render_template, request, redirect, url_for, session,Flask,flash  
from manage_item import get_devices_with_details, add_device
from manage_user import get_user
from dashboard import get_concern_stats, get_borrow_requests,get_all_users,get_all_available_devices
from login import login_bp
from borrrow import approve_borrow_request, decline_borrow_request, mark_returned_borrow_request
from userborrow import get_available_units
from db import get_db_connection
from userborrow import userborrow_bp


app = Flask(__name__)
app.secret_key = 'a2f1e4f8f60b4f81a8d32dd0b3c2ce90'
app.register_blueprint(login_bp)

app.register_blueprint(userborrow_bp)

from datetime import datetime


@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))
    if session.get('is_admin'):
        return redirect(url_for('admin'))

    from userborrow import get_available_devices, get_available_units
    raw_items = get_available_devices()
    
    items = [
        {
            'id': i['id'],
            'name': i['name'],
            'serial_number': i['serial_number'],
            'department': i['department']
        }
        for i in raw_items
    ]
    units = get_available_units()  # ← add this
    return render_template(
        'main.html',
        username=session.get('username'),
        items=items,
        units=units           # ← pass it here too
    )
@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))
    if not session.get('is_admin'):
        return redirect(url_for('login_bp.logout'))

    # still use your stats helpers if you want
    stats = get_concern_stats()
    users = get_all_users()
    devices = get_all_available_devices()
    units = get_available_units()

    # do the borrow requests join here instead of get_borrow_requests()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
           SELECT
            br.borrow_id,
            br.student_id,
            CONCAT(br.first_name, ' ', br.middle_initial, '. ', br.last_name) AS borrower_name,

            -- Build device display string right in SQL
            du.accession_id,
            d.item_name,
            d.brand_model,
            du.serial_number,

            br.borrow_date,
            br.return_date,
            br.reason,
            br.status
        FROM borrow_requests br
        JOIN devices_units du ON br.device_id = du.accession_id
        JOIN devices d ON du.device_id = d.device_id
        ORDER BY br.borrow_date DESC
        """)
        requests = cur.fetchall()
    conn.close()

    return render_template(
        'admin.html',
        total_requests=stats['total'],
        pending_requests=stats['pending'],
        ongoing_requests=stats['ongoing'],
        resolved_requests=stats['resolved'],
        requests=requests,
        users=users,
        devices=devices
        ,units=units
    )

# @app.route('/concernlist')
# def concernlist():
#     if 'user_id' not in session:
#         return redirect(url_for('login_bp.logout'))
#     return render_template('concernlist.html', username=session.get('username'))


@app.route('/manage-user')
def manage_user():
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))

    all_users = get_user()
    return render_template('manage_user.html', users=all_users)

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/manage-item', methods=['GET','POST'])
def manage_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        brand_model = request.form.get('brand_model')
        department_id = request.form.get('department_id')
        serial_number = request.form.get('serial_number')
        quantity = request.form.get('quantity')
        device_type = request.form.get('device_type')
        status = request.form.get('status', 'Available')

        add_device(item_name, brand_model, department_id, serial_number, quantity, device_type, status)
        return redirect(url_for('manage_item'))

    items = get_devices_with_details()
    departments = get_departments()  # load your dept dropdown
    return render_template('manage_item.html', items=items, departments=departments)

def get_departments():
    """
    Fetch all departments from the database.
    Returns a list of dicts with keys: department_id, department_name.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            departments = cur.fetchall()
    finally:
        conn.close()
    return departments


@app.route('/edit-item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    # logic to edit the item goes here
    return f"Edit item {id}"  # placeholder for now

@app.route('/delete-item/<int:id>', methods=['POST'])
def delete_item(id):
    # logic to delete the item goes here
    return redirect(url_for('manage_item'))

@app.route('/add_request', methods=['POST'])
def add_request():
    user_id = request.form['user_id']
    device_id = request.form['device_id']
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    return_date = request.form['return_date']
    reason = request.form['reason']  # <-- get reason

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO borrow_requests (user_id, device_id, borrow_date, return_date, reason, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending')
        """, (user_id, device_id, borrow_date, return_date, reason))
        conn.commit()
    conn.close()

    flash('Borrow request added successfully', 'success')
    return redirect(url_for('admin'))


@app.route('/approve/<int:borrow_id>', methods=['POST'])
def approve(borrow_id):
    approve_borrow_request(borrow_id)
    flash('Borrow request approved', 'success')
    return redirect(url_for('admin'))

@app.route('/decline/<int:borrow_id>', methods=['POST'])
def decline(borrow_id):
    decline_borrow_request(borrow_id)
    flash('Borrow request declined', 'warning')
    return redirect(url_for('admin'))

@app.route('/returned/<int:borrow_id>', methods=['POST'])
def returned(borrow_id):
    mark_returned_borrow_request(borrow_id)
    flash('Marked as returned', 'info')
    return redirect(url_for('admin'))
if __name__ == "__main__":
    app.run(debug=True)
