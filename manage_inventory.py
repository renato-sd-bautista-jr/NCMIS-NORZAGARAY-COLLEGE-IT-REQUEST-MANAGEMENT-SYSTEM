from flask import Blueprint, render_template, flash, jsonify,request
from db import get_db_connection
import pymysql
from inventory_auto_check import run_inventory_auto_check

 
 

manage_inventory_bp = Blueprint('manage_inventory', __name__, template_folder='templates')


@manage_inventory_bp.route('/manage_inventory')
def inventory_load():
    """Load Manage Inventory with pagination for devices."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pc_list = get_pc_list()
    item_list, total_items, total_pages = get_item_list_paginated(page, per_page)
     
    if pc_list is None or item_list is None:
        flash("Error loading data. Please try again.", "danger")

    return render_template(
        'manage_inventory.html',
        pc_list=pc_list,
        item_list=item_list,
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages
    )


@manage_inventory_bp.route('/manage_inventory/items-paged')
def items_paged():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    items, total_items, total_pages = get_item_list_paginated(page, per_page)

    return jsonify({
        "items": items,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages
    })
 

@manage_inventory_bp.route('/manage_inventory/get-departments')
def get_departments():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT department_id, department_name 
                FROM departments 
                ORDER BY department_name
            """)
            departments = cur.fetchall()
        return jsonify(departments)
    except Exception as e:
        print(f"❌ Error fetching departments: {e}")
        return jsonify([]), 500
    finally:
        conn.close()


def get_pc_list():
    """Fetch all PCs with department and part details from pcinfofull."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
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
                    p.motherboard,
                    p.ram,
                    p.storage,
                    p.gpu,
                    p.psu,
                    p.casing,
                    p.other_parts,
                    p.risk_level,
                    p.health_score
                   
                
                FROM pcinfofull p
                LEFT JOIN departments d ON p.department_id = d.department_id
                ORDER BY p.pcid
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching PC list: {e}")
        return []
    finally:
        conn.close()



def get_item_list():
    """Fetch all devices from devices_full (for Manage Items section)."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id AS accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.department_id,
                    dep.department_name,
                    df.status,
                    df.updated_at
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                ORDER BY df.accession_id DESC
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching item list: {e}")
        return []
    finally:
        conn.close()

@manage_inventory_bp.route('/manage_inventory/get-item-by-id/<int:item_id>')
def get_item_by_id(item_id):
    """Fetch a single device record with full details."""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    df.accession_id AS accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.department_id,
                    dep.department_name,
                    df.status,
                    df.updated_at
                FROM devices_full df
                LEFT JOIN departments dep 
                    ON df.department_id = dep.department_id
                WHERE df.accession_id = %s
            """, (item_id,))
            item = cur.fetchone()

        if not item:
            return jsonify({'error': 'Item not found'}), 404

        return jsonify(item)
    except Exception as e:
        print(f"❌ Error fetching item by ID: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        conn.close()


@manage_inventory_bp.route('/manage_inventory/get-pc-by-id/<int:pcid>')
def get_pc_by_id(pcid):

    
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
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
                    p.motherboard,
                    p.ram,
                    p.storage,
                    p.gpu,
                    p.psu,
                    p.casing,
                    p.other_parts
                FROM pcinfofull p
                LEFT JOIN departments d ON p.department_id = d.department_id
                WHERE p.pcid = %s
            """, (pcid,))
            pc = cur.fetchone()

            if not pc:
                return {"error": "PC not found"}, 404

            return pc
    except Exception as e:
        print(f"❌ Error fetching PC by ID: {e}")
        return {"error": "Database error"}, 500
    finally:
        conn.close()


@manage_inventory_bp.route('/manage_inventory/pc-filter-modal')
def pc_filter_modal():
    return render_template('pcFilterModal.html')

def get_item_list_paginated(page=1, per_page=10):
    """
    Fetch paginated devices from devices_full.
    Returns:
        items, total_items, total_pages
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Get total count
            cur.execute("SELECT COUNT(*) AS total FROM devices_full")
            total_items = cur.fetchone()["total"]

            # Get paginated data
            cur.execute("""
                SELECT 
                    df.accession_id AS accession_id,
                    df.item_name,
                    df.brand_model,
                    df.serial_no,
                    df.municipal_serial_no,
                    df.quantity,
                    df.device_type,
                    df.acquisition_cost,
                    df.date_acquired,
                    df.accountable,
                    df.department_id,
                    dep.department_name,
                    df.status,
                    df.updated_at
                FROM devices_full df
                LEFT JOIN departments dep ON df.department_id = dep.department_id
                ORDER BY df.accession_id DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))

            items = cur.fetchall()

        total_pages = (total_items + per_page - 1) // per_page
        return items, total_items, total_pages

    except Exception as e:
        print(f"❌ Error fetching paginated items: {e}")
        return [], 0, 0
    finally:
        conn.close()

@manage_inventory_bp.route('/manage_inventory/run-risk-update', methods=['POST'])
def run_risk_update():
    

    try:
        run_inventory_auto_check()
        return jsonify({
            "success": True,
            "message": "Inventory risk levels recalculated."
        })
    except Exception as e:
        print("Risk update error:", e)
        return jsonify({
            "success": False,
            "message": "Risk update failed."
        }), 500
    
@manage_inventory_bp.route('/inventory/pc/<int:pcid>/check', methods=['POST'])
def mark_pc_checked(pcid):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT status, risk_level
                FROM pcinfofull
                WHERE pcid = %s
            """, (pcid,))
            old = cur.fetchone()

            cur.execute("""
                UPDATE pcinfofull
                SET
                    last_checked = CURDATE(),
                    health_score = 100,
                    risk_level = 'Low',
                    status = 'Available'
                WHERE pcid = %s
            """, (pcid,))

            cur.execute("""
                INSERT INTO maintenance_logs (
                    asset_type, asset_id,
                    previous_status, new_status,
                    previous_risk_level, new_risk_level,
                    action
                ) VALUES (
                    'PC', %s,
                    %s, 'Available',
                    %s, 'Low',
                    'Manual inspection completed'
                )
            """, (
                pcid,
                old['status'],
                old['risk_level']
            ))
            cur.execute("""
                INSERT INTO maintenance_history (
                    pcid, asset_type, asset_id,
                    action, old_status, new_status,
                    risk_level, health_score, performed_by, remarks
                ) VALUES (
                    %s, 'PC', %s,
                    'Manual inspection completed', %s, 'Available',
                    'Low', 100, %s, %s
                )
            """, (
                pcid,
                pcid,
                old['status'],
                'System',   # you can replace 'System' with current user if available
                'Marked as checked manually'
            ))

        conn.commit()
        return jsonify(success=True)

    except Exception as e:
        conn.rollback()
        return jsonify(success=False, error=str(e)), 500
    finally:
        conn.close()

@manage_inventory_bp.route('/maintenance-history')
def maintenance_history():
    asset_id = request.args.get('id', type=int)
    asset_type = request.args.get('type')

    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT *
            FROM maintenance_logs
            WHERE asset_type = %s AND asset_id = %s
            ORDER BY performed_at DESC
        """, (asset_type, asset_id))
        logs = cur.fetchall()

    conn.close()
    return render_template('maintenance_history.html', logs=logs)