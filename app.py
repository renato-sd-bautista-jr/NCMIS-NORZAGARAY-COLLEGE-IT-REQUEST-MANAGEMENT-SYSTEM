from flask import render_template, request, redirect, url_for, session, Flask, flash, Blueprint

from manage_item import get_devices_with_details, add_device, get_departments
from manage_user import get_user
from dashboard import get_concern_stats, get_borrow_requests,get_all_users,get_all_available_devices,get_all_available_units
from login import login_bp
from borrrow import approve_borrow_request, decline_borrow_request, mark_returned_borrow_request
from userborrow import get_available_units
from db import get_db_connection
from userborrow import userborrow_bp
from qr_functions import qrcode_bp
from manage_pc import (
    manage_pc_bp,   # ✅ add this line
    get_pc_inventory,
    add_pc,
    get_pc_by_id,
    update_pc,
    delete_pc,
    
    delete_pc_in_db
)
import pymysql

app = Flask(__name__)
app.secret_key = 'a2f1e4f8f60b4f81a8d32dd0b3c2ce90'
app.register_blueprint(login_bp)

app.register_blueprint(userborrow_bp)
app.register_blueprint(manage_pc_bp)
app.register_blueprint(qrcode_bp)

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
    units = get_all_available_units()
    requests = get_borrow_requests()
   
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
    pc_list = get_pc_inventory()

    # ✅ Import and call your get_departments function
    from manage_item import get_departments
    departments = get_departments()

    return render_template('inventory.html', pc_list=pc_list, departments=departments)


@app.route('/manage-item', methods=['GET', 'POST'])
def manage_item():
    if request.method == 'GET':
        # Fetch all devices with their details
        items = get_devices_with_details()
        departments = get_departments()

        return render_template('manage_item.html', items=items, departments=departments)


@app.route('/delete-pc/<pcid>', methods=['POST'])
def delete_pc_route(pcid):
    try:
        from manage_pc import delete_pc_in_db
        delete_pc_in_db(pcid)
        flash("PC deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting PC: {e}", "danger")
    return redirect(url_for('inventory'))


@app.route('/add-device', methods=['POST'])
def add_device_route():
    try:
        item_name = request.form.get('item_name')
        brand_model = request.form.get('brand_model')
        department_id = request.form.get('department_id')
        serial_number = request.form.get('serial_number')
        quantity = request.form.get('quantity')
        device_type = request.form.get('device_type')
        status = request.form.get('status')

        if not item_name or not department_id or not status:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('manage_item'))

        from manage_item import add_device  # ensure function is imported
        add_device(item_name, brand_model, department_id, serial_number, quantity, device_type, status)

        flash("Device added successfully!", "success")
        return redirect(url_for('manage_item'))

    except Exception as e:
        flash(f"Error adding device: {str(e)}", "danger")
        return redirect(url_for('manage_item'))



@app.route('/edit-item/<int:accession_id>', methods=['POST'])
def edit_item(accession_id):
    """Update both devices and devices_units tables"""
    if 'user_id' not in session:
        return redirect(url_for('login_bp.login'))

    try:
        # Extract form data
        item_name = request.form.get('item_name')
        brand_model = request.form.get('brand_model')
        serial_number = request.form.get('serial_number')
        department_id = request.form.get('department_id')
        device_type = request.form.get('device_type')
        status = request.form.get('status')

        conn = get_db_connection()
        with conn.cursor() as cur:
            # Update both tables using join logic
            cur.execute("""
                UPDATE devices d
                JOIN devices_units du ON d.device_id = du.device_id
                SET d.item_name = %s,
                    d.brand_model = %s,
                    d.department_id = %s,
                    d.device_type = %s,
                    du.serial_number = %s,
                    du.status = %s
                WHERE du.accession_id = %s
            """, (item_name, brand_model, department_id, device_type, serial_number, status, accession_id))

            conn.commit()

        flash('Device updated successfully', 'success')
        return redirect(url_for('manage_item'))

    except Exception as e:
        print(f"Error editing item {accession_id}: {e}")
        flash("Error updating device", "error")
        return redirect(url_for('manage_item'))

@app.route('/delete-item/<int:id>', methods=['POST'])
def delete_item(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete from devices_units using accession_id
        cursor.execute("DELETE FROM devices_units WHERE accession_id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error deleting item:", e)

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
