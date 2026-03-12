from flask import Blueprint, jsonify, request, render_template, send_file
import pymysql
from db import get_db_connection
from io import BytesIO
import pandas as pd
from utils.permissions import check_permission

transaction_bp = Blueprint('transaction_bp', __name__, template_folder='templates')


@transaction_bp.route('/transactions')
@check_permission('transaction', 'view')
def transaction_page():
    """Render the transaction history page."""
    # additional data fetching can be inserted here later
    return render_template('transaction.html')


def _safe_int(value):
    try:
        if value is None:
            return None
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


@transaction_bp.route('/transactions/api', methods=['GET'])
@check_permission('transaction', 'view')
def get_transactions_api():
    filter_type = (request.args.get('filter') or 'all').lower()
    limit = _safe_int(request.args.get('limit')) or 100
    limit = max(1, min(limit, 500))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            """
            SELECT
                a.audit_id,
                a.entity_type,
                a.entity_id,
                a.action,
                a.field_name,
                a.old_value,
                a.new_value,
                a.performed_by,
                a.performed_at,
                u.username AS performed_by_username,
                df.item_name AS device_item_name,
                pcf.pcname AS pc_item_name
            FROM inventory_audit_log a
            LEFT JOIN users u ON u.user_id = a.performed_by
            LEFT JOIN devices_full df
                ON a.entity_type = 'DEVICE' AND df.accession_id = a.entity_id
            LEFT JOIN pcinfofull pcf
                ON a.entity_type = 'PC' AND pcf.pcid = a.entity_id
            ORDER BY a.performed_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall() or []

        normalized = []
        for r in rows:
            old_qty = _safe_int(r.get('old_value')) if (r.get('field_name') == 'quantity') else None
            new_qty = _safe_int(r.get('new_value')) if (r.get('field_name') == 'quantity') else None
            qty_diff = (new_qty - old_qty) if (old_qty is not None and new_qty is not None) else None

            tx_type = 'other'
            if r.get('field_name') == 'quantity' and qty_diff is not None:
                if qty_diff > 0:
                    tx_type = 'receive'
                elif qty_diff < 0:
                    tx_type = 'return'
                else:
                    tx_type = 'adjust'

            if filter_type in {'receive', 'return'} and tx_type != filter_type:
                continue

            item_name = r.get('pc_item_name') if (r.get('entity_type') == 'PC') else r.get('device_item_name')
            if not item_name:
                item_name = f"{r.get('entity_type')} #{r.get('entity_id')}"

            normalized.append(
                {
                    'id': r.get('audit_id'),
                    'type': tx_type,
                    'entity_type': r.get('entity_type'),
                    'entity_id': r.get('entity_id'),
                    'item_name': item_name,
                    'action': r.get('action'),
                    'field_name': r.get('field_name'),
                    'old_value': r.get('old_value'),
                    'new_value': r.get('new_value'),
                    'quantity_change': qty_diff,
                    'performed_by': r.get('performed_by_username') or r.get('performed_by'),
                    'performed_at': r.get('performed_at').isoformat() if r.get('performed_at') else None,
                }
            )

        return jsonify({'transactions': normalized})

    except Exception as e:
        print(f"❌ Error fetching transactions: {e}")
        return jsonify({'transactions': []}), 500
    finally:
        cursor.close()
        conn.close()


@transaction_bp.route('/transactions/stats', methods=['GET'])
@check_permission('transaction', 'view')
def get_transaction_stats():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    total_received = 0
    total_returned = 0
    try:
        cursor.execute(
            """
            SELECT old_value, new_value
            FROM inventory_audit_log
            WHERE field_name = 'quantity'
            ORDER BY performed_at DESC
            LIMIT 1000
            """
        )
        rows = cursor.fetchall() or []

        for r in rows:
            old_qty = _safe_int(r.get('old_value'))
            new_qty = _safe_int(r.get('new_value'))
            if old_qty is None or new_qty is None:
                continue
            diff = new_qty - old_qty
            if diff > 0:
                total_received += diff
            elif diff < 0:
                total_returned += abs(diff)

        return jsonify(
            {
                'total_received': total_received,
                'total_returned': total_returned,
                'net_change': total_received - total_returned,
            }
        )
    except Exception as e:
        print(f"❌ Error fetching transaction stats: {e}")
        return jsonify({'total_received': 0, 'total_returned': 0, 'net_change': 0}), 500
    finally:
        cursor.close()
        conn.close()
