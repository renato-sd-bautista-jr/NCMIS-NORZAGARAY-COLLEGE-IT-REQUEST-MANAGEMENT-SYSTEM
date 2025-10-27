from flask import request, render_template, redirect, url_for, flash, Blueprint,jsonify,session
from db import get_db_connection
import pymysql,re
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



@manage_pc_bp.route('/filter-pcs', methods=['GET'])
def filter_pcs():
    """Filter PC list based on query parameters."""
    conn = get_db_connection()
    try:
        department_id = request.args.get('department_id')
        status = request.args.get('status')
        location = request.args.get('location')
        accountable = request.args.get('accountable')
        serial_no = request.args.get('serial_no')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = """
            SELECT 
                p.pcid,
                p.pcname,
                p.department_id,
                d.department_name,
                p.location,
                p.quantity,
                p.acquisition_cost,
                p.date_acquired,
                p.accountable,
                p.serial_no,
                p.municipal_serial_no,
                p.status,
                p.note,
                p.monitor,
                p.motherboard,
                p.ram,
                p.storage,
                p.gpu,
                p.psu,
                p.casing,
                p.other_parts
            FROM pcinfofull p
            LEFT JOIN departments d ON p.department_id = d.department_id
            WHERE 1=1
        """
        params = []

        if department_id:
            query += " AND p.department_id = %s"
            params.append(department_id)
        if status:
            query += " AND p.status = %s"
            params.append(status)
        if location:
            query += " AND p.location LIKE %s"
            params.append(f"%{location}%")
        if accountable:
            query += " AND p.accountable LIKE %s"
            params.append(f"%{accountable}%")
        if serial_no:
            query += " AND (p.serial_no LIKE %s OR p.municipal_serial_no LIKE %s)"
            params.extend([f"%{serial_no}%", f"%{serial_no}%"])
        if date_from and date_to:
            query += " AND p.date_acquired BETWEEN %s AND %s"
            params.extend([date_from, date_to])

        query += " ORDER BY p.pcid"

        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(query, params)
            pcs = cur.fetchall()

        return jsonify(pcs)

    except Exception as e:
        print(f"❌ Error filtering PCs: {e}")
        return jsonify({"error": "Error filtering PCs."}), 500
    finally:
        conn.close()

@manage_pc_bp.route('/add-pcinfofull', methods=['POST'])
def add_pcinfofull():
    conn = get_db_connection()
    data = request.form.to_dict()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # 🔹 Check for duplicates (Serial No or Municipal Serial No)
            cur.execute("""
                SELECT COUNT(*) AS count FROM pcinfofull 
                WHERE serial_no = %s OR municipal_serial_no = %s
            """, (data['serial_no'], data['municipal_serial_no']))
            duplicate = cur.fetchone()['count']

            if duplicate > 0:
                return jsonify({
                    "success": False,
                    "error": "Duplicate entry: Serial No or Municipal Serial No already exists."
                }), 400

            # 🔹 Insert new PC
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



        return jsonify({"success": True, "message": "PC added successfully!"})

    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding PC: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        conn.close()



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





@manage_pc_bp.route('/batch_add_pcinfofull', methods=['POST'])
def batch_add_pcinfofull():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            inserted = 0

            # 🔹 Get department info from first entry
            first_pc = data[0]
            department_id = first_pc.get('department_id')
            if not department_id:
                return jsonify({'success': False, 'error': 'Missing department ID'}), 400

            # 🔹 Get department_code (new column)
            cur.execute("SELECT department_name, department_code FROM departments WHERE department_id = %s", (department_id,))
            dept_row = cur.fetchone()
            if not dept_row:
                return jsonify({'success': False, 'error': 'Department not found'}), 404

            dept_code = (dept_row['department_code'] or dept_row['department_name']).strip().lower().replace(' ', '-')
            base_pcname = f"pc-{dept_code}"

            # 🔹 Get existing PC names for that department
            cur.execute("""
                SELECT pcname FROM pcinfofull
                WHERE department_id = %s AND pcname LIKE %s
            """, (department_id, f"{base_pcname}-%"))
            existing_names = [row['pcname'] for row in cur.fetchall()]

            # 🔹 Determine next available number
            max_num = 0
            pattern = re.compile(rf"^{re.escape(base_pcname)}-(\d+)$")
            for name in existing_names:
                match = pattern.match(name)
                if match:
                    num = int(match.group(1))
                    max_num = max(max_num, num)

            current_num = max_num + 1

            # 🔹 Insert each PC
            for pc in data:
                required = ['serial_no', 'municipal_serial_no']
                if not all(pc.get(field) for field in required):
                    continue

                pc['pcname'] = f"{base_pcname}-{current_num:02d}"
                current_num += 1

                # Duplicate check
                cur.execute("""
                    SELECT COUNT(*) AS count
                    FROM pcinfofull
                    WHERE serial_no = %s OR municipal_serial_no = %s
                """, (pc['serial_no'], pc['municipal_serial_no']))
                if cur.fetchone()['count'] > 0:
                    print(f"⚠️ Skipped duplicate: {pc['serial_no']} / {pc['municipal_serial_no']}")
                    continue

                cur.execute("""
                    INSERT INTO pcinfofull (
                        pcname, department_id, location, quantity, acquisition_cost,
                        date_acquired, accountable, serial_no, municipal_serial_no, status, note,
                        monitor, motherboard, ram, storage, gpu, psu, casing, other_parts,
                        created_at, updated_at
                    )
                    VALUES (
                        %(pcname)s, %(department_id)s, %(location)s, %(quantity)s, %(acquisition_cost)s,
                        %(date_acquired)s, %(accountable)s, %(serial_no)s, %(municipal_serial_no)s,
                        %(status)s, %(note)s, %(monitor)s, %(motherboard)s, %(ram)s, %(storage)s,
                        %(gpu)s, %(psu)s, %(casing)s, %(other_parts)s,
                        NOW(), NOW()
                    )
                """, pc)
                inserted += 1

        conn.commit()
        return jsonify({
            'success': True,
            'message': f'Successfully added {inserted} PCs under {dept_row['department_name']} ({dept_code.upper()})'
        })

    except Exception as e:
        print("❌ Batch insert error:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()