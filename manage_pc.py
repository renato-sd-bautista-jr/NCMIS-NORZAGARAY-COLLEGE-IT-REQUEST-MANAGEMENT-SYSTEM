from flask import request, render_template, redirect, url_for, flash, Blueprint
from db import get_db_connection
import pymysql

manage_pc_bp = Blueprint('manage_pc_bp', __name__)

# ✅ Display all PCs
def get_pc_inventory():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT * FROM pcs ORDER BY pcid")
        pcs = cur.fetchall()
        for pc in pcs:
            cur.execute("SELECT * FROM pcparts WHERE pcid = %s", (pc["pcid"],))
            pc["parts"] = cur.fetchall()
    conn.close()
    return pcs

# ✅ Get specific PC details
def get_pc_by_id(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM pcs WHERE pcid = %s", (pcid,))
            pc = cur.fetchone()
            return pc
    except Exception as e:
        print(f"Error fetching PC by ID: {e}")
        return None
    finally:
        conn.close()
@manage_pc_bp.route('/add-pc', methods=['POST'])
def add_pc_route():
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
        # Generate custom pcid
        cur.execute("SELECT COUNT(*) AS cnt FROM pcs")
        count = cur.fetchone()['cnt']
        pcid = f"PC-{count + 1:03d}"

        # Insert into pcs
        cur.execute("""
            INSERT INTO pcs (pcid, pcname, department_id, status, note)
            VALUES (%s, %s, %s, %s, %s)
        """, (pcid, pcname, department_id, status, note))

        # Insert into pcparts
        cur.execute("""
            INSERT INTO pcparts (pcid, monitor, motherboard, ram, storage, gpu, psu, casing, other_parts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (pcid, monitor, motherboard, ram, storage, gpu, psu, casing, other_parts))

        conn.commit()
    conn.close()

    flash("PC added successfully!", "success")
    return redirect(url_for('inventory'))

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
        # Insert into pcs

        cur.execute("SELECT COUNT(*) AS cnt FROM pcs")
        count = cur.fetchone()['cnt']
        pcid = f"PC-{count+1:03d}"

        cur.execute("""
        INSERT INTO pcs (pcid, pcname, department_id, status, note)
        VALUES (%s, %s, %s, %s, %s)
        """, (pcid, pcname, department_id, status, note))
        # Insert into pcparts
        cur.execute("""
            INSERT INTO pcparts (monitor, motherboard, ram, storage, gpu, psu, casing, other_parts)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)
        """, (monitor, motherboard, ram, storage, gpu, psu, casing, other_parts))
        conn.commit()
    conn.close()

    flash("PC added successfully!", "success")
    return redirect(url_for('inventory'))


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
    return redirect(url_for('inventory'))

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


# ✅ Edit PC info
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

# ✅ Delete PC
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

        


def delete_pc_in_db(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pcs WHERE pcid=%s", (pcid,))
            conn.commit()
    finally:
        conn.close()

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
