from flask import request, render_template, redirect, url_for, flash, Blueprint
from db import get_db_connection
import pymysql
import uuid
manage_pc_bp = Blueprint('manage_pc_bp', __name__)

@manage_pc_bp.route('/inventory')
def inventory():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Load departments
            cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            departments = cur.fetchall()

            # Load PCs with joined info
            cur.execute("""
                SELECT 
                    p.pcid,
                    p.pcname,
                    p.department_id,
                    d.department_name,
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
                LEFT JOIN departments d ON p.department_id = d.department_id
                LEFT JOIN pcparts pa ON p.pcid = pa.pcid
                ORDER BY p.pcid ASC
            """)
            pc_list = cur.fetchall()

        # Debugging info (see your terminal if it still redirects)
        print("✅ Loaded PCs:", pc_list)
        print("✅ Loaded Departments:", departments)

        return render_template('inventory.html', pc_list=pc_list, departments=departments)

    except Exception as e:
        print("❌ Error loading inventory:", e)
        flash(f"Error loading inventory: {e}", "danger")
        # Temporarily comment out redirect for debugging
        # return redirect(url_for('dashboard_bp.dashboard_load'))
        return f"<h3>Error loading inventory: {e}</h3>", 500

    finally:
        conn.close()

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

@manage_pc_bp.route('/get-pc-by-id/<string:pcid>')
def get_pc_by_id(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.*,
                    dep.department_name,
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
                WHERE p.pcid = %s
            """, (pcid,))
            return cur.fetchone()
    except Exception as e:
        print(f"Error fetching PC by ID: {e}")
        return None
    finally:
        conn.close()



@manage_pc_bp.route('/add-pc', methods=['POST'])
def add_pc_route():
    conn = get_db_connection()
    form = request.form

    try:
        with conn.cursor() as cur:
            # ✅ Generate a unique PCID string (like "PC-uuid4")
            pcid = f"PC-{uuid.uuid4().hex[:8].upper()}"

            pcname = form['pcname']
            department_id = form['department_id']
            status = form['status']
            note = form['note']

            monitor = form['monitor']
            motherboard = form['motherboard']
            ram = form['ram']
            storage = form['storage']
            gpu = form['gpu']
            psu = form['psu']
            casing = form['casing']
            other_parts = form['other_parts']

            # ✅ Insert into pcs first
            cur.execute("""
                INSERT INTO pcs (pcid, pcname, department_id, status, note)
                VALUES (%s, %s, %s, %s, %s)
            """, (pcid, pcname, department_id, status, note))

            # ✅ Then insert into pcparts using the same pcid
            cur.execute("""
                INSERT INTO pcparts (pcid, monitor, motherboard, ram, storage, gpu, psu, casing, other_parts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (pcid, monitor, motherboard, ram, storage, gpu, psu, casing, other_parts))

            conn.commit()

        flash("PC and parts added successfully!", "success")

    except Exception as e:
        conn.rollback()
        print(f"Error adding PC: {e}")
        flash(f"Error adding PC: {str(e)}", "danger")

    finally:
        conn.close()

    return redirect(url_for('manage_pc_bp.manage_pc_page'))



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
    return redirect(url_for('manage_pc_bp.manage_pc_page'))


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

        return redirect(url_for('manage_pc_bp.inventory'))
    finally:
        conn.close()
