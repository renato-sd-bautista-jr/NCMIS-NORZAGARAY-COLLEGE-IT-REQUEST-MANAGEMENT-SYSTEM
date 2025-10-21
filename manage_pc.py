from flask import request, render_template, redirect, url_for, flash, Blueprint,jsonify,session
from db import get_db_connection
import pymysql
import uuid
from notification import add_notification

manage_pc_bp = Blueprint('manage_pc_bp', __name__)

# @manage_pc_bp.route('/inventory')
# def inventory():
#     conn = get_db_connection()
#     try:
#         with conn.cursor(pymysql.cursors.DictCursor) as cur:
#             # Load departments
#             cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
#             departments = cur.fetchall()

#             # Load PCs with joined info
#             cur.execute("""
#                 SELECT 
#                     p.pcid,
#                     p.pcname,
#                     p.department_id,
#                     d.department_name,
#                     p.status,
#                     p.note,
#                     pa.monitor,
#                     pa.motherboard,
#                     pa.ram,
#                     pa.storage,
#                     pa.gpu,
#                     pa.psu,
#                     pa.casing,
#                     pa.other_parts
#                 FROM pcs p
#                 LEFT JOIN departments d ON p.department_id = d.department_id
#                 LEFT JOIN pcparts pa ON p.pcid = pa.pcid
#                 ORDER BY p.pcid ASC
#             """)
#             pc_list = cur.fetchall()

#         # Debugging info (see your terminal if it still redirects)
#         print("✅ Loaded PCs:", pc_list)
#         print("✅ Loaded Departments:", departments)

#         return render_template('test.html', pc_list=pc_list, departments=departments)

#     except Exception as e:
#         print("❌ Error loading inventory:", e)
#         flash(f"Error loading inventory: {e}", "danger")
#         # Temporarily comment out redirect for debugging
#         # return redirect(url_for('dashboard_bp.dashboard_load'))
#         return f"<h3>Error loading inventory: {e}</h3>", 500

#     finally:
#         conn.close()



# @manage_pc_bp.route('/inventory')
# def inventory():
#     return render_template('test.html')

   

# ✅ Display all PCs
@manage_pc_bp.route('/get-pc-inventory')
def get_pc_inventory():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                p.pcid,
                p.pcname,
                p.department_id,
                dep.department_name,
                p.status,
                p.note,
                pa.monitor,
                pa.motherboard,
                pa.ram,
                pa.storage,
                pa.gpu,
                pa.psu,
                pa.casing,
                pa.other_parts
            FROM pcs p
            LEFT JOIN departments dep ON p.department_id = dep.department_id
            LEFT JOIN pcparts pa ON p.pcid = pa.pcid
            ORDER BY p.pcid
        """)
        pcs = cur.fetchall()
    conn.close()
    return pcs

# ✅ Get specific PC details



@manage_pc_bp.route('/add-pc', methods=['POST'])
def add_pc_route():
    # Ensure only logged-in admins can add PCs
    if 'user_id' not in session or not session.get('is_admin'):
        flash("You must be logged in as admin to perform this action.", "danger")
        return redirect(url_for('login_bp.login'))

    conn = get_db_connection()
    form = request.form

    try:
        with conn.cursor() as cur:
            # Generate unique PC ID
            import uuid
            pcid = f"PC-{uuid.uuid4().hex[:8].upper()}"

            # PC basic info
            pcname = form.get('pcname')
            department_id = form.get('department_id')
            status = form.get('status')
            note = form.get('note')

            # PC parts
            monitor = form.get('monitor')
            motherboard = form.get('motherboard')
            ram = form.get('ram')
            storage = form.get('storage')
            gpu = form.get('gpu')
            psu = form.get('psu')
            casing = form.get('casing')
            other_parts = form.get('other_parts')

            # Insert into pcs table
            cur.execute("""
                INSERT INTO pcs (pcid, pcname, department_id, status, note)
                VALUES (%s, %s, %s, %s, %s)
            """, (pcid, pcname, department_id, status, note))

            # Insert into pcparts table
            cur.execute("""
                INSERT INTO pcparts (pcid, monitor, motherboard, ram, storage, gpu, psu, casing, other_parts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (pcid, monitor, motherboard, ram, storage, gpu, psu, casing, other_parts))

            # Commit inserts
            conn.commit()

            # Log notification
            user_id = session['user_id']
            action = f"Added new PC: {pcname} ({pcid})"
            try:
                add_notification(user_id, action, target_type="PC", target_id=pcid)
                print("✅ Notification logged")
            except Exception as e:
                print(f"❌ Failed to log notification: {e}")

            flash("PC and parts added successfully!", "success")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding PC: {e}")
        flash(f"Error adding PC: {str(e)}", "danger")

    finally:
        conn.close()

    return redirect(url_for('manage_inventory.inventory_load'))


@manage_pc_bp.route('/update-pc-with-parts', methods=['POST'])
def update_pc_with_parts():
    pcid = request.form['pcid']
    pcname = request.form['pcname']
    department_id = request.form['department_id']
    status = request.form['status']
    note = request.form['note']

    monitor = request.form['monitor']
    motherboard = request.form['motherboard']
    ram = request.form['ram']
    storage = request.form['storage']
    gpu = request.form['gpu']
    psu = request.form['psu']
    casing = request.form['casing']
    other_parts = request.form['other_parts']

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE pcs
            SET pcname=%s, department_id=%s, status=%s, note=%s
            WHERE pcid=%s
        """, (pcname, department_id, status, note, pcid))

        cur.execute("""
            UPDATE pcparts
            SET monitor=%s, motherboard=%s, ram=%s, storage=%s,
                gpu=%s, psu=%s, casing=%s, other_parts=%s
            WHERE pcid=%s
        """, (monitor, motherboard, ram, storage, gpu, psu, casing, other_parts, pcid))

        conn.commit()

    conn.close()
    flash("PC updated successfully!", "success")
    return redirect(url_for('manage_inventory.inventory_load'))


@manage_pc_bp.route('/add-pc-single', methods=['POST'])
def add_pc(pcname, department_id, status, note):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pcs (pcname, department_id, status, note)
                VALUES (%s, %s, %s, %s)
            """, (pcname, department_id, status, note))
            conn.commit()
    except Exception as e:
        print(f"Error adding PC: {e}")
        conn.rollback()
    finally:
        conn.close()


@manage_pc_bp.route('/update-pc', methods=['POST'])
def update_pc(pcid, pcname, department_id, status, note):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pcs
                SET pcname=%s, department_id=%s, status=%s, note=%s
                WHERE pcid=%s
                """,
                (pcname, department_id, status, note, pcid)
            )
            conn.commit()
    except Exception as e:
        print(f"Error updating PC: {e}")
        conn.rollback()
    finally:
        conn.close()

@manage_pc_bp.route('/delete-pc/<string:pcid>', methods=['POST'])
def delete_pc(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pcs WHERE pcid=%s", (pcid,))
            conn.commit()
    except Exception as e:
        print(f"Error deleting PC: {e}")
        conn.rollback()
    finally:
        conn.close()

        
@manage_pc_bp.route('/add-multiple-pcs', methods=['POST'])
def add_multiple_pcs(pcname, pcid, department_id, status, note, quantity):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for i in range(quantity):
                cur.execute("""
                    INSERT INTO pcs (pcname, pcid, department_id, status, note)
                    VALUES (%s, %s, %s, %s, %s)
                """, (f"{pcname}-{i+1}", f"{pcid}-{i+1}", department_id, status, note))
            conn.commit()
    finally:
        conn.close()

@manage_pc_bp.route('/manage-pc')
def manage_pc_page():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            departments = cur.fetchall()

            cur.execute("""
                SELECT pcs.*, d.department_name
                FROM pcs
                LEFT JOIN departments d ON pcs.department_id = d.department_id
                ORDER BY pcs.pcid
            """)
            pc_list = cur.fetchall()

            for pc in pc_list:
                cur.execute("SELECT * FROM pcparts WHERE pcid = %s", (pc["pcid"],))
                pc["parts"] = cur.fetchall()

        return redirect(url_for('manage_inventory.inventory_load'))
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
