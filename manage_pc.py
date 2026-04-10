from flask import request, render_template, redirect, url_for, flash, Blueprint,jsonify,session,send_file
from db import get_db_connection
from io import BytesIO
import pandas as pd
import pymysql,re
import uuid
from datetime import date
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from utils.inventory_audit import log_inventory_action
from notification import add_notification

manage_pc_bp = Blueprint('manage_pc_bp', __name__)

   

@manage_pc_bp.route("/delete-pc/<int:pcid>", methods=["POST"])
def delete_pc(pcid):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE pcinfofull SET is_archived = 1, deleted_at = NOW() WHERE pcid = %s", (pcid,))
            conn.commit()
            print(f"PC with ID {pcid} archived (soft deleted).")
        if is_ajax:
            return jsonify(success=True, message="PC archived successfully.")
        flash("PC archived successfully.", "success")
    except Exception as e:
        conn.rollback()
        if is_ajax:
            return jsonify(success=False, error=str(e)), 500
        flash(str(e), "error")
    finally:
        conn.close()
    return redirect(url_for('manage_inventory.inventory_load'))


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
                CASE WHEN LOWER(TRIM(p.status)) IN ('damaged', 'damage', 'unusable') THEN 'High' ELSE p.risk_level END AS risk_level,
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
            WHERE p.is_archived = 0
        """

        params = []
        if status != 'Surrendered':
             query += " AND p.status != 'Surrendered'"

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
            query += " AND (CASE WHEN LOWER(TRIM(p.status)) IN ('damaged', 'damage', 'unusable') THEN 'High' ELSE p.risk_level END) = %s"
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
                    OR DATE_ADD(
                        p.last_checked,
                        INTERVAL GREATEST(
                            1,
                            CASE
                                WHEN IFNULL(p.maintenance_interval_days, 30) < 365
                                    THEN IFNULL(p.maintenance_interval_days, 30) * 365
                                ELSE IFNULL(p.maintenance_interval_days, 30)
                            END
                        ) DAY
                    ) < CURDATE()
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

            # Default new PCs to Available (unless explicitly set) and initialize check/health values
            if not data.get('status'):
                data['status'] = 'Available'

            # Reuse surrendered numbered slot first for single add (e.g., surrendered ...-21 gets reused).
            department_id = data.get('department_id')
            if department_id:
                cur.execute(
                    "SELECT department_name, department_code FROM departments WHERE department_id = %s",
                    (department_id,)
                )
                dept_row = cur.fetchone()

                if dept_row:
                    dept_code = (dept_row['department_code'] or dept_row['department_name']).strip().lower().replace(' ', '-')
                    base_pcname = f"pc-{dept_code}"

                    cur.execute("""
                        SELECT pcname, status
                        FROM pcinfofull
                        WHERE department_id = %s AND pcname LIKE %s
                    """, (department_id, f"{base_pcname}-%"))
                    existing_rows = cur.fetchall()

                    pattern = re.compile(rf"^{re.escape(base_pcname)}-(\d+)$", re.IGNORECASE)
                    active_numbers = set()
                    surrendered_numbers = set()

                    for row in existing_rows:
                        pc_name = (row.get('pcname') or '').strip()
                        match = pattern.match(pc_name)
                        if not match:
                            continue

                        seq_number = int(match.group(1))
                        row_status = str(row.get('status') or '').strip().lower()
                        if row_status == 'surrendered':
                            surrendered_numbers.add(seq_number)
                        else:
                            active_numbers.add(seq_number)

                    reusable_numbers = sorted(num for num in surrendered_numbers if num not in active_numbers)
                    if reusable_numbers:
                        data['pcname'] = f"{base_pcname}-{reusable_numbers[0]:02d}"

            # 🔹 Insert new PC
            cur.execute("""
                INSERT INTO pcinfofull 
                (pcname, department_id, location, quantity, acquisition_cost, date_acquired, accountable, serial_no, municipal_serial_no, status, note,maintenance_interval_days,
                motherboard, ram, storage, gpu, psu, casing, other_parts,
                last_checked, health_score, risk_level)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, CURDATE(), 100, 'Low')
            """, (
                data['pcname'], data['department_id'], data['location'], data['quantity'],
                data['acquisition_cost'], data['date_acquired'], data['accountable'],
                data['serial_no'], data['municipal_serial_no'], data['status'], data['note'],data.get('maintenance_interval_days')
                , data['motherboard'], data['ram'], data['storage'],
                data['gpu'], data['psu'], data['casing'], data['other_parts']
            ))

            # Ensure DB defaults/triggers can't leave the newly created PC in an incorrect state
            new_pcid = cur.lastrowid
            cur.execute("""
                UPDATE pcinfofull
                SET
                    status = 'Available',
                    last_checked = CURDATE(),
                    health_score = 100,
                    risk_level = 'Low'
                WHERE pcid = %s
            """, (new_pcid,))
            conn.commit()



        return jsonify({"success": True, "message": "PC added successfully!"})

    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding PC: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        conn.close()
    manage_inventory.risk




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
                    risk_level=CASE WHEN LOWER(TRIM(%s)) IN ('damaged', 'damage', 'unusable') THEN 'High' ELSE risk_level END,
                    note=%s,
                    maintenance_interval_days=%s,
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
                data['status'],
                data['note'],
                data.get('maintenance_interval_days'),  # ⭐
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
                'maintenance_interval_days',  # ⭐ ADD
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

            # 🔹 Get existing PC names/status for that department
            cur.execute("""
                SELECT pcname, status FROM pcinfofull
                WHERE department_id = %s AND pcname LIKE %s
            """, (department_id, f"{base_pcname}-%"))
            existing_rows = cur.fetchall()

            # Reuse surrendered slots first (e.g., if ...-21 is surrendered, next add gets ...-21).
            pattern = re.compile(rf"^{re.escape(base_pcname)}-(\d+)$", re.IGNORECASE)
            active_numbers = set()
            surrendered_numbers = set()

            for row in existing_rows:
                pc_name = (row.get('pcname') or '').strip()
                match = pattern.match(pc_name)
                if not match:
                    continue

                seq_number = int(match.group(1))
                row_status = str(row.get('status') or '').strip().lower()

                if row_status == 'surrendered':
                    surrendered_numbers.add(seq_number)
                else:
                    active_numbers.add(seq_number)

            reusable_numbers = sorted(num for num in surrendered_numbers if num not in active_numbers)
            all_seen_numbers = active_numbers.union(surrendered_numbers)
            next_number = (max(all_seen_numbers) + 1) if all_seen_numbers else 1

            # 🔹 Insert each PC
            for pc in data:
                required = ['serial_no', 'municipal_serial_no']
                if not all(pc.get(field) for field in required):
                    continue

                if not pc.get('status'):
                    pc['status'] = 'Available'

                # Duplicate check
                cur.execute("""
                    SELECT COUNT(*) AS count
                    FROM pcinfofull
                    WHERE serial_no = %s OR municipal_serial_no = %s
                """, (pc['serial_no'], pc['municipal_serial_no']))
                if cur.fetchone()['count'] > 0:
                    print(f"⚠️ Skipped duplicate: {pc['serial_no']} / {pc['municipal_serial_no']}")
                    continue

                if reusable_numbers:
                    assigned_number = reusable_numbers.pop(0)
                else:
                    while next_number in active_numbers:
                        next_number += 1
                    assigned_number = next_number
                    next_number += 1

                active_numbers.add(assigned_number)
                pc['pcname'] = f"{base_pcname}-{assigned_number:02d}"

                cur.execute("""
                    INSERT INTO pcinfofull (
                        pcname, department_id, location, quantity, acquisition_cost,
                        date_acquired, accountable, serial_no, municipal_serial_no, status, note,maintenance_interval_days,
                         motherboard, ram, storage, gpu, psu, casing, other_parts,
                        last_checked, health_score, risk_level,
                        created_at, updated_at
                    )
                    VALUES (
                        %(pcname)s, %(department_id)s, %(location)s, %(quantity)s, %(acquisition_cost)s,
                        %(date_acquired)s, %(accountable)s, %(serial_no)s, %(municipal_serial_no)s,
                        %(status)s, %(note)s, %(maintenance_interval_days)s, %(motherboard)s, %(ram)s, %(storage)s,
                        %(gpu)s, %(psu)s, %(casing)s, %(other_parts)s,
                        CURDATE(), 100, 'Low',
                        NOW(), NOW()
                    )
                """, pc)
                inserted += 1

        conn.commit()
        return jsonify({
            'success': True,
        #     'message': f'Successfully added {inserted} PCs under {dept_row['department_name']} ({dept_code.upper()})'
        # 
        })

    except Exception as e:
        print("❌ Batch insert error:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@manage_pc_bp.route('/manage_pc/export-selected-pcs', methods=['POST'])
def export_selected_pcs():

    data = request.get_json(silent=True) or {}
    pcids = data.get("pcids") or []

    try:
        pcids = [int(pid) for pid in pcids]
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid PC selection"}), 400

    if not pcids:
        return jsonify({"error": "No PCs selected"}), 400

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            format_strings = ','.join(['%s'] * len(pcids))

            cur.execute(f"""
                SELECT
                    p.pcid,
                    p.pcname,
                    COALESCE(d.department_name, '') AS department,
                    p.location,
                    p.acquisition_cost,
                    p.date_acquired,
                    p.accountable,
                    p.serial_no,
                    p.municipal_serial_no,
                    p.status
                FROM pcinfofull p
                LEFT JOIN departments d ON p.department_id = d.department_id
                WHERE p.pcid IN ({format_strings})
                ORDER BY p.pcid
            """, pcids)

            rows = cur.fetchall()

        if not rows:
            return jsonify({"error": "No matching PCs found for export"}), 404

        df = pd.DataFrame(rows).rename(columns={
            "pcid": "PC ID",
            "pcname": "PC Name",
            "department": "Department",
            "location": "Location",
            "acquisition_cost": "Acquisition Cost",
            "date_acquired": "Date Acquired",
            "accountable": "Accountable",
            "serial_no": "Serial No.",
            "municipal_serial_no": "Municipal Serial No.",
            "status": "Status",
        })

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = 'Selected PCs'
            df.to_excel(writer, index=False, sheet_name=sheet_name)

            ws = writer.sheets[sheet_name]

            header_fill = PatternFill(fill_type='solid', fgColor='4F46E5')
            header_font = Font(color='FFFFFF', bold=True)
            thin_side = Side(style='thin', color='D1D5DB')
            cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

            for col_idx, col_name in enumerate(df.columns, start=1):
                header_cell = ws.cell(row=1, column=col_idx)
                header_cell.fill = header_fill
                header_cell.font = header_font
                header_cell.alignment = Alignment(horizontal='center', vertical='center')
                header_cell.border = cell_border

                values = [str(col_name)]
                for value in df.iloc[:, col_idx - 1].tolist():
                    values.append('' if value is None else str(value))
                max_len = max(len(v) for v in values)
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 3, 36)

            for row_idx in range(2, ws.max_row + 1):
                for col_idx in range(1, ws.max_column + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    cell.border = cell_border

            column_map = {name: idx + 1 for idx, name in enumerate(df.columns)}

            if 'Acquisition Cost' in column_map:
                col = column_map['Acquisition Cost']
                for row_idx in range(2, ws.max_row + 1):
                    ws.cell(row=row_idx, column=col).number_format = '#,##0.00'

            if 'Date Acquired' in column_map:
                col = column_map['Date Acquired']
                for row_idx in range(2, ws.max_row + 1):
                    date_cell = ws.cell(row=row_idx, column=col)
                    date_cell.number_format = 'yyyy-mm-dd'
                    date_cell.alignment = Alignment(horizontal='center', vertical='center')

            for name in ('PC ID', 'Status'):
                if name in column_map:
                    col = column_map[name]
                    for row_idx in range(2, ws.max_row + 1):
                        ws.cell(row=row_idx, column=col).alignment = Alignment(horizontal='center', vertical='center')

            ws.freeze_panes = 'A2'
            ws.auto_filter.ref = ws.dimensions

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="selected_pcs.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        print("❌ Export error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@manage_pc_bp.route('/manage_pc/import-pcs-excel', methods=['POST'])
def import_pcs_excel():
    file = request.files.get("file")
    duplicate_option = request.form.get("duplicate_option", "skip")

    if not file:
        return jsonify({"success": False, "error": "No file uploaded"})

    if duplicate_option not in {"skip", "ignore", "overwrite"}:
        duplicate_option = "skip"

    conn = None

    try:
        df = pd.read_excel(file)

        # Normalize incoming headers so both template exports and raw imports are supported.
        def normalize_header(name):
            text = str(name).strip().lower()
            text = re.sub(r"[^a-z0-9]+", "_", text)
            return text.strip("_")

        df = df.rename(columns={col: normalize_header(col) for col in df.columns})

        alias_map = {
            "pc_name": "pcname",
            "department_name": "department",
        }
        for old_name, new_name in alias_map.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]

        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        added = 0
        updated = 0
        skipped = 0

        department_cache = {}

        def clean_value(value):
            if pd.isna(value):
                return None
            if isinstance(value, str):
                value = value.strip()
                return value or None
            if isinstance(value, pd.Timestamp):
                return value.date()
            return value

        for _, row in df.iterrows():

            pcname = clean_value(row.get("pcname"))
            serial = clean_value(row.get("serial_no"))
            municipal = clean_value(row.get("municipal_serial_no"))
            location = clean_value(row.get("location"))
            acquisition_cost = clean_value(row.get("acquisition_cost"))
            date_acquired = clean_value(row.get("date_acquired"))
            accountable = clean_value(row.get("accountable"))
            status = clean_value(row.get("status")) or "Available"
            status_text = str(status).strip()
            normalized_status_text = status_text.lower()
            imported_risk = "High" if normalized_status_text in {"damaged", "damage", "unusable"} else "Low"

            department_id = clean_value(row.get("department_id"))
            department_name = clean_value(row.get("department"))

            if not department_id and department_name:
                if department_name not in department_cache:
                    cur.execute(
                        "SELECT department_id FROM departments WHERE department_name = %s LIMIT 1",
                        (department_name,)
                    )
                    dept_row = cur.fetchone()
                    department_cache[department_name] = dept_row["department_id"] if dept_row else None
                department_id = department_cache.get(department_name)

            if not serial and not municipal:
                skipped += 1
                continue

            existing = None
            if serial and municipal:
                cur.execute(
                    "SELECT pcid FROM pcinfofull WHERE serial_no = %s OR municipal_serial_no = %s LIMIT 1",
                    (serial, municipal)
                )
                existing = cur.fetchone()
            elif serial:
                cur.execute(
                    "SELECT pcid FROM pcinfofull WHERE serial_no = %s LIMIT 1",
                    (serial,)
                )
                existing = cur.fetchone()
            elif municipal:
                cur.execute(
                    "SELECT pcid FROM pcinfofull WHERE municipal_serial_no = %s LIMIT 1",
                    (municipal,)
                )
                existing = cur.fetchone()

            if existing:
                if duplicate_option == "skip":
                    skipped += 1
                    continue

                if duplicate_option == "ignore":
                    skipped += 1
                    continue

                if duplicate_option == "overwrite":
                    cur.execute("""
                        UPDATE pcinfofull SET
                        pcname = COALESCE(%s, pcname),
                        department_id = COALESCE(%s, department_id),
                        location = COALESCE(%s, location),
                        acquisition_cost = COALESCE(%s, acquisition_cost),
                        date_acquired = COALESCE(%s, date_acquired),
                        accountable = COALESCE(%s, accountable),
                        status = COALESCE(%s, status),
                        risk_level = CASE WHEN LOWER(TRIM(COALESCE(%s, status))) IN ('damaged', 'damage', 'unusable') THEN 'High' ELSE risk_level END
                        WHERE pcid=%s
                    """, (
                        pcname,
                        department_id,
                        location,
                        acquisition_cost,
                        date_acquired,
                        accountable,
                        status,
                        status,
                        existing["pcid"]
                    ))

                    updated += 1
                    continue

            if not pcname:
                skipped += 1
                continue

            cur.execute("""
                INSERT INTO pcinfofull
                (pcname,department_id,location,acquisition_cost,date_acquired,
                 accountable,serial_no,municipal_serial_no,status,
                 last_checked,health_score,risk_level)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, CURDATE(), 100, %s)
            """, (
                pcname,
                department_id,
                location,
                acquisition_cost,
                date_acquired,
                accountable,
                serial,
                municipal,
                status,
                imported_risk
            ))

            added += 1

        conn.commit()

        return jsonify({
            "success": True,
            "added": added,
            "updated": updated,
            "skipped": skipped
        })

    except Exception as e:
        print("Import error:", e)
        return jsonify({"success": False, "error": str(e)})

    finally:
        if conn:
            conn.close()