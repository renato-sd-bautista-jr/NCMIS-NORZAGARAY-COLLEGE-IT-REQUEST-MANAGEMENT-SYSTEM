from flask import request, render_template, redirect, url_for, flash, Blueprint,jsonify,session
from db import get_db_connection
import pymysql
import uuid
from notification import add_notification

manage_pc_bp = Blueprint('manage_pc_bp', __name__)

   
@manage_pc_bp.route('/delete-pc/<string:pcid>', methods=['POST'])
def delete_pc(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pcinfofull WHERE pcid=%s", (pcid,))
            conn.commit()
            return redirect(url_for('manage_inventory.inventory_load'))
    except Exception as e:
        print(f"Error deleting PC: {e}")
        conn.rollback()
        
    finally:
        
        conn.close()




@manage_pc_bp.route('/add-pcinfofull', methods=['POST'])
def add_pcinfofull():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("You must be logged in as admin to perform this action.", "warning")
        return redirect(url_for('login_bp.login'))

    conn = get_db_connection()
    data = request.form

    try:
        with conn.cursor() as cur:
            # Insert PC info
            cur.execute("""
                INSERT INTO pcinfofull 
                (pcname, department_id, location, quantity, acquisition_cost, date_acquired, accountable, serial_no, municipal_serial_no, status, note,
                 monitor, motherboard, ram, storage, gpu, psu, casing, other_parts)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data['pcname'], data['department_id'], data['location'], data['quantity'],
                data['acquisition_cost'], data['date_acquired'], data['accountable'],
                data['serial_no'], data['municipal_serial_no'], data['status'], data['note'],
                data['monitor'], data['motherboard'], data['ram'], data['storage'],
                data['gpu'], data['psu'], data['casing'], data['other_parts']
            ))

            conn.commit()

        # ✅ Log notification
        user_id = session['user_id']
        action = f"Added new PC: {data['pcname']} (Serial: {data['serial_no']})"
        try:
            add_notification(user_id, action, target_type="PC", target_id=data['serial_no'])
        except Exception as e:
            print(f"❌ Notification error: {e}")

        flash("PC added successfully!", "success")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding PC: {e}")
        flash(f"Error adding PC: {str(e)}", "danger")

    finally:
        conn.close()

    return redirect(url_for('manage_pc_bp.manage_pc_page'))


@manage_pc_bp.route('/update-pcinfofull', methods=['POST'])
def update_pcinfofull():
    conn = get_db_connection()
    data = request.form
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pcinfofull SET
                    pcname=%s, department_id=%s, location=%s, quantity=%s, acquisition_cost=%s, date_acquired=%s,
                    accountable=%s, serial_no=%s, municipal_serial_no=%s, status=%s, note=%s,
                    monitor=%s, motherboard=%s, ram=%s, storage=%s, gpu=%s, psu=%s, casing=%s, other_parts=%s
                WHERE pcid=%s
            """, (
                data['pcname'], data['department_id'], data['location'], data['quantity'],
                data['acquisition_cost'], data['date_acquired'], data['accountable'],
                data['serial_no'], data['municipal_serial_no'], data['status'], data['note'],
                data['monitor'], data['motherboard'], data['ram'], data['storage'],
                data['gpu'], data['psu'], data['casing'], data['other_parts'], data['pcid']
            ))
            conn.commit()
        flash("PC updated successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('manage_inventory.inventory_load'))
