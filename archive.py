from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection

archive_bp = Blueprint('archive_bp', __name__)

@archive_bp.route('/archive')
def archive_page():
    return render_template('archive.html')

@archive_bp.route('/api/archived-pcs')
def get_archived_pcs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get total count
            if search:
                count_query = "SELECT COUNT(*) AS total FROM pcinfofull pc LEFT JOIN departments dep ON pc.department_id = dep.department_id WHERE pc.is_archived = 1 AND (pc.pcid LIKE %s OR pc.pcname LIKE %s OR pc.serial_no LIKE %s OR dep.department_name LIKE %s)"
                cur.execute(count_query, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
            else:
                count_query = "SELECT COUNT(*) AS total FROM pcinfofull WHERE is_archived = 1"
                cur.execute(count_query)
            total = cur.fetchone()['total']
            
            # Get paginated data
            offset = (page - 1) * per_page
            if search:
                data_query = "SELECT pc.pcid, pc.pcname, dep.department_name, pc.location, pc.acquisition_cost, pc.date_acquired, pc.accountable, pc.serial_no, pc.municipal_serial_no, pc.status, pc.deleted_at FROM pcinfofull pc LEFT JOIN departments dep ON pc.department_id = dep.department_id WHERE pc.is_archived = 1 AND (pc.pcid LIKE %s OR pc.pcname LIKE %s OR pc.serial_no LIKE %s OR dep.department_name LIKE %s) ORDER BY pc.deleted_at DESC LIMIT %s OFFSET %s"
                cur.execute(data_query, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
            else:
                data_query = "SELECT pc.pcid, pc.pcname, dep.department_name, pc.location, pc.acquisition_cost, pc.date_acquired, pc.accountable, pc.serial_no, pc.municipal_serial_no, pc.status, pc.deleted_at FROM pcinfofull pc LEFT JOIN departments dep ON pc.department_id = dep.department_id WHERE pc.is_archived = 1 ORDER BY pc.deleted_at DESC LIMIT %s OFFSET %s"
                cur.execute(data_query, (per_page, offset))
            pcs = cur.fetchall()
            
            # Convert to list of dicts
            pcs_list = []
            for pc in pcs:
                pcs_list.append({
                    'pcid': pc['pcid'],
                    'pcname': pc['pcname'],
                    'department_name': pc['department_name'],
                    'location': pc['location'],
                    'acquisition_cost': pc['acquisition_cost'],
                    'date_acquired': pc['date_acquired'],
                    'accountable': pc['accountable'],
                    'serial_no': pc['serial_no'],
                    'municipal_serial_no': pc['municipal_serial_no'],
                    'status': 'ARCHIVE',
                    'deleted_at': pc['deleted_at'].strftime('%Y-%m-%d %H:%M:%S') if pc['deleted_at'] else ''
                })
            
            total_pages = (total + per_page - 1) // per_page
            
            return jsonify({
                'data': pcs_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            })
    finally:
        conn.close()

@archive_bp.route('/api/archived-items')
def get_archived_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get total count
            if search:
                count_query = "SELECT COUNT(*) AS total FROM devices_full df LEFT JOIN departments dep ON df.department_id = dep.department_id WHERE df.is_archived = 1 AND (df.accession_id LIKE %s OR df.item_name LIKE %s OR df.brand_model LIKE %s OR df.device_type LIKE %s OR dep.department_name LIKE %s)"
                cur.execute(count_query, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
            else:
                count_query = "SELECT COUNT(*) AS total FROM devices_full WHERE is_archived = 1"
                cur.execute(count_query)
            total = cur.fetchone()['total']
            
            # Get paginated data
            offset = (page - 1) * per_page
            if search:
                data_query = "SELECT df.accession_id, df.item_name, df.brand_model, df.serial_no, df.municipal_serial_no, df.acquisition_cost, df.date_acquired, df.accountable, dep.department_name, df.deleted_at FROM devices_full df LEFT JOIN departments dep ON df.department_id = dep.department_id WHERE df.is_archived = 1 AND (df.accession_id LIKE %s OR df.item_name LIKE %s OR df.brand_model LIKE %s OR df.serial_no LIKE %s OR df.municipal_serial_no LIKE %s OR dep.department_name LIKE %s) ORDER BY df.deleted_at DESC LIMIT %s OFFSET %s"
                cur.execute(data_query, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
            else:
                data_query = "SELECT df.accession_id, df.item_name, df.brand_model, df.serial_no, df.municipal_serial_no, df.acquisition_cost, df.date_acquired, df.accountable, dep.department_name, df.deleted_at FROM devices_full df LEFT JOIN departments dep ON df.department_id = dep.department_id WHERE df.is_archived = 1 ORDER BY df.deleted_at DESC LIMIT %s OFFSET %s"
                cur.execute(data_query, (per_page, offset))
            items = cur.fetchall()
            
            # Convert to list of dicts
            items_list = []
            for item in items:
                items_list.append({
                    'accession_id': item['accession_id'],
                    'item_name': item['item_name'],
                    'brand_model': item['brand_model'],
                    'serial_no': item['serial_no'],
                    'municipal_serial_no': item['municipal_serial_no'],
                    'acquisition_cost': item['acquisition_cost'],
                    'date_acquired': item['date_acquired'],
                    'accountable': item['accountable'],
                    'department_name': item['department_name'],
                    'status': 'ARCHIVED',
                    'deleted_at': item['deleted_at'].strftime('%Y-%m-%d %H:%M:%S') if item['deleted_at'] else ''
                })
            
            total_pages = (total + per_page - 1) // per_page
            
            return jsonify({
                'data': items_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            })
    finally:
        conn.close()
