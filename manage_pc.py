from flask import request, render_template, redirect, url_for, flash, Blueprint,jsonify,session
from db import get_db_connection
import pymysql,re
import uuid
from datetime import date
from utils.inventory_audit import log_inventory_action
from notification import add_notification

manage_pc_bp = Blueprint('manage_pc_bp', __name__)

   
@manage_pc_bp.route("/delete-pc/<int:pcid>", methods=["POST"])
def delete_pc(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pcinfofull WHERE pcid = %s", (pcid,))
            conn.commit()
        flash("PC deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(str(e), "error")
    finally:
        conn.close()

    return redirect(url_for("manage_inventory.inventory_load"))


@manage_pc_bp.route('/filter-pcs', methods=['GET'])
def filter_pcs():
    conn = get_db_connection()

    try:
        args = request.args

        department_id = args.get('department_id')
        status = args.get('status')
        location = args.get('location')
        accountable = args.get('accountable')
        serial_no = args.get('serial_no')

        date_from = args.get('date_from')
        date_to = args.get('date_to')

        risk_level = args.get('risk_level')
        health_min = args.get('health_min', type=int)
        health_max = args.get('health_max', type=int)

        last_checked_from = args.get('last_checked_from')
        last_checked_to = args.get('last_checked_to')

        overdue_only = args.get('overdue') == '1'
        needs_checking = args.get('needs_checking') == '1'

        search = args.get('search')

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

                -- health & maintenance
                p.health_score,
                p.risk_level,
                p.last_checked,
                p.maintenance_interval_days,

                -- parts
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
            query += """
                AND (
                    p.serial_no LIKE %s
                    OR p.municipal_serial_no LIKE %s
                )
            """
            params.extend([f"%{serial_no}%", f"%{serial_no}%"])

        if date_from and date_to:
            query += " AND p.date_acquired BETWEEN %s AND %s"
            params.extend([date_from, date_to])

        # 🔹 NEW FILTERS

        if risk_level:
            query += " AND p.risk_level = %s"
            params.append(risk_level)

        if health_min is not None:
            query += " AND p.health_score >= %s"
            params.append(health_min)

        if health_max is not None:
            query += " AND p.health_score <= %s"
            params.append(health_max)

        if last_checked_from and last_checked_to:
            query += " AND p.last_checked BETWEEN %s AND %s"
            params.extend([last_checked_from, last_checked_to])

        if overdue_only:
            query += """
                AND (
                    p.last_checked IS NULL
                    OR DATE_ADD(p.last_checked, INTERVAL p.maintenance_interval_days DAY) < CURDATE()
                )
            """

        if needs_checking:
            query += " AND p.status = 'Needs Checking'"

        if search:
            query += """
                AND (
                    p.pcname LIKE %s
                    OR p.motherboard LIKE %s
                    OR p.ram LIKE %s
                    OR p.storage LIKE %s
                    OR p.gpu LIKE %s
                )
            """
            params.extend([f"%{search}%"] * 5)

        query += " ORDER BY p.pcid DESC"

        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(query, params)
            pcs = cur.fetchall()

        return jsonify(pcs)

    except Exception as e:
        print(f"❌ Error filtering PCs: {e}")
        return jsonify({"error": "Error filtering PCs"}), 500

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
                motherboard, ram, storage, gpu, psu, casing, other_parts)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data['pcname'], data['department_id'], data['location'], data['quantity'],
                data['acquisition_cost'], data['date_acquired'], data['accountable'],
                data['serial_no'], data['municipal_serial_no'], data['status'], data['note']
                , data['motherboard'], data['ram'], data['storage'],
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
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    data = request.form
    user_id = session['user']['user_id']

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            # 🔹 1. Duplicate check
            cur.execute("""
                SELECT COUNT(*) AS count
                FROM pcinfofull
                WHERE (serial_no = %s OR municipal_serial_no = %s)
                  AND pcid != %s
            """, (
                data['serial_no'],
                data['municipal_serial_no'],
                data['pcid']
            ))

            if cur.fetchone()['count'] > 0:
                return jsonify({
                    "success": False,
                    "error": "Duplicate entry: Serial No or Municipal Serial No already exists."
                }), 400

            # 🔹 2. Fetch OLD values
            cur.execute("SELECT * FROM pcinfofull WHERE pcid = %s", (data['pcid'],))
            old_pc = cur.fetchone()

            if not old_pc:
                return jsonify({"success": False, "error": "PC not found"}), 404

            # 🔹 3. Perform UPDATE
            cur.execute("""
                UPDATE pcinfofull SET
                    pcname=%s,
                    department_id=%s,
                    location=%s,
                    quantity=%s,
                    acquisition_cost=%s,
                    date_acquired=%s,
                    accountable=%s,
                    serial_no=%s,
                    municipal_serial_no=%s,
                    status=%s,
                    note=%s,
                    motherboard=%s,
                    ram=%s,
                    storage=%s,
                    gpu=%s,
                    psu=%s,
                    casing=%s,
                    other_parts=%s
                WHERE pcid=%s
            """, (
                data['pcname'],
                data['department_id'],
                data['location'],
                data['quantity'],
                data['acquisition_cost'],
                data['date_acquired'],
                data['accountable'],
                data['serial_no'],
                data['municipal_serial_no'],
                data['status'],
                data['note'],
                data['motherboard'],
                data['ram'],
                data['storage'],
                data['gpu'],
                data['psu'],
                data['casing'],
                data['other_parts'],
                data['pcid']
            ))

            # 🔹 4. AUDIT LOGGING
            tracked_fields = [
                'pcname', 'department_id', 'location', 'quantity',
                'acquisition_cost', 'date_acquired', 'accountable',
                'serial_no', 'municipal_serial_no', 'status', 'note',
                'motherboard', 'ram', 'storage', 'gpu',
                'psu', 'casing', 'other_parts'
            ]

            for field in tracked_fields:
                old_value = old_pc.get(field)
                new_value = data.get(field)

                # Normalize dates
                if isinstance(old_value, date):
                    old_value = old_value.strftime('%Y-%m-%d')

                # Skip if both empty
                if (old_value is None or old_value == '') and (new_value is None or new_value == ''):
                    continue

                if str(old_value) != str(new_value):
                    log_inventory_action(
                        entity_type='PC',
                        entity_id=data['pcid'],
                        action='UPDATE',
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        performed_by=user_id
                    )

            conn.commit()

        return jsonify({"success": True, "message": "PC updated successfully!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        conn.close()

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
                         motherboard, ram, storage, gpu, psu, casing, other_parts,
                        created_at, updated_at
                    )
                    VALUES (
                        %(pcname)s, %(department_id)s, %(location)s, %(quantity)s, %(acquisition_cost)s,
                        %(date_acquired)s, %(accountable)s, %(serial_no)s, %(municipal_serial_no)s,
                        %(status)s, %(note)s, %(motherboard)s, %(ram)s, %(storage)s,
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