from flask import Blueprint, jsonify, request, render_template, send_file,session
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

@transaction_bp.route('/consumables/api', methods=['GET'])
@check_permission('transaction', 'view')
def get_consumables():

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("""
            SELECT 
                accession_id,
                item_name,
                quantity,
                unit
            FROM consumables
            ORDER BY item_name
        """)

        rows = cursor.fetchall() or []

        return jsonify({
            "consumables": rows
        })

    except Exception as e:
        print(f"❌ Error fetching consumables: {e}")
        return jsonify({"consumables": []}), 500

    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('/transactions/api', methods=['GET'])
@check_permission('transaction', 'view')
def get_transactions_api():

    limit = int(request.args.get('limit', 200))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:

        cursor.execute("""
            SELECT
                t.transaction_id,
                t.item_name,
                t.action,
                t.quantity,
                t.previous_stock,
                t.new_stock,
                t.created_at,
                u.username
            FROM consumable_transactions t
            LEFT JOIN users u
            ON u.user_id = t.performed_by
            ORDER BY t.created_at DESC
            LIMIT %s
        """, (limit,))

        rows = cursor.fetchall()

        transactions = []

        for r in rows:

            qty_change = r["quantity"]

            transactions.append({
                "id": r["transaction_id"],
                "type": "receive" if r["action"] == "RECEIVE" else "return",
                "item_name": r["item_name"],
                "quantity_change": qty_change,
                "performed_by": r["username"],
                "performed_at": str(r["created_at"])
            })

        return jsonify({"transactions": transactions})

    except Exception as e:
        print("❌ Transaction fetch error:", e)
        return jsonify({"transactions": []}), 500

    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('/transactions/stats')
def get_transaction_stats():

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:

        cursor.execute("""
            SELECT
                SUM(CASE WHEN action='RECEIVE' THEN quantity ELSE 0 END) AS total_received,
                SUM(CASE WHEN action='RETURN' THEN quantity ELSE 0 END) AS total_returned
            FROM consumable_transactions
        """)

        row = cursor.fetchone()

        total_received = row["total_received"] or 0
        total_returned = row["total_returned"] or 0

        return jsonify({
            "total_received": total_received,
            "total_returned": total_returned,
            "net_change": total_received - total_returned
        })

    finally:
        cursor.close()
        conn.close()

        
@transaction_bp.route('/consumables/receive', methods=['POST'])
@check_permission('transaction', 'add')
def receive_consumable():

    data = request.json
    accession_id = data.get('accession_id')
    qty = int(data.get('quantity'))
    notes = data.get('notes')

    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:

        cursor.execute(
            "SELECT quantity, item_name FROM consumables WHERE accession_id=%s",
            (accession_id,)
        )
        item = cursor.fetchone()

        if not item:
            return jsonify({"success": False, "message": "Item not found"}), 404

        previous_stock = item["quantity"]
        new_stock = previous_stock + qty

        cursor.execute("""
            UPDATE consumables
            SET quantity=%s,
                last_updated=NOW()
            WHERE accession_id=%s
        """, (new_stock, accession_id))

        cursor.execute("""
            INSERT INTO consumable_transactions
            (accession_id,item_name,action,quantity,previous_stock,new_stock,notes,performed_by)
            VALUES (%s,%s,'RECEIVE',%s,%s,%s,%s,%s)
        """, (
            accession_id,
            item["item_name"],
            qty,
            previous_stock,
            new_stock,
            notes,
            user_id
        ))

        conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("❌ Receive error:", e)
        return jsonify({"success": False}), 500

    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('/consumables/return', methods=['POST'])
@check_permission('transaction', 'add')
def return_consumable():

    data = request.json
    accession_id = data.get('accession_id')
    qty = int(data.get('quantity'))
    reason = data.get('reason')


    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:

        cursor.execute(
            "SELECT quantity, item_name FROM consumables WHERE accession_id=%s",
            (accession_id,)
        )
        item = cursor.fetchone()

        if not item:
            return jsonify({"success": False, "message": "Item not found"}), 404

        previous_stock = item["quantity"]

        if qty > previous_stock:
            return jsonify({"success": False, "message": "Not enough stock"}), 400

        new_stock = previous_stock - qty

        cursor.execute("""
            UPDATE consumables
            SET quantity=%s,
                last_updated=NOW()
            WHERE accession_id=%s
        """, (new_stock, accession_id))

        cursor.execute("""
            INSERT INTO consumable_transactions
            (accession_id,item_name,action,quantity,previous_stock,new_stock,reason,performed_by)
            VALUES (%s,%s,'RETURN',%s,%s,%s,%s,%s)
        """, (
            accession_id,
            item["item_name"],
            qty,
            previous_stock,
            new_stock,
            reason,
            user_id
        ))

        conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("❌ Return error:", e)
        return jsonify({"success": False}), 500

    finally:
        cursor.close()
        conn.close()