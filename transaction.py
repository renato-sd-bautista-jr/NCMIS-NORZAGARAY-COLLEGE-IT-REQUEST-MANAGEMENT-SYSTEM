from flask import Blueprint, jsonify, request, render_template, send_file
import pymysql
from db import get_db_connection
from io import BytesIO
import pandas as pd
from utils.permissions import check_permission

transaction_bp = Blueprint('transaction_bp', __name__, template_folder='templates')


 
@check_permission('transaction', 'view')
@transaction_bp.route("/transactions")
def transactions_page():

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            cur.execute("""
                SELECT
                    t.transaction_id,
                    c.item_name,
                    t.transaction_type,
                    t.quantity,
                    t.remarks,
                    t.transacted_by,
                    t.transaction_date
                FROM transactions t
                LEFT JOIN consumables c
                ON t.accession_id = c.accession_id
                ORDER BY t.transaction_date DESC
            """)

            transactions = cur.fetchall()

        return render_template("transaction.html", transactions=transactions)

    finally:
        conn.close()

@transaction_bp.route("/api/consumables")
def get_consumables():

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT accession_id, item_name, quantity
                FROM consumables
                ORDER BY item_name
            """)
            items = cur.fetchall()

        return jsonify(items)

    finally:
        conn.close()

@transaction_bp.route("/api/transaction", methods=["POST"])
def add_transaction():

    data = request.json
    accession_id = data["accession_id"]
    quantity = int(data["quantity"])
    transaction_type = data["transaction_type"]
    remarks = data.get("remarks", "")

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:

            # save transaction history
            cur.execute("""
                INSERT INTO transactions
                (accession_id, transaction_type, quantity, remarks)
                VALUES (%s,%s,%s,%s)
            """,(accession_id,transaction_type,quantity,remarks))

            # update stock
            if transaction_type == "receive":

                cur.execute("""
                    UPDATE consumables
                    SET quantity = quantity + %s
                    WHERE accession_id = %s
                """,(quantity,accession_id))

            elif transaction_type == "return":

                cur.execute("""
                    UPDATE consumables
                    SET quantity = quantity - %s
                    WHERE accession_id = %s
                """,(quantity,accession_id))

        conn.commit()

        return jsonify({"success":True})

    finally:
        conn.close()

@transaction_bp.route("/api/transactions")
def get_transactions():

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            cur.execute("""
                SELECT
                    t.transaction_id,
                    c.item_name,
                    t.transaction_type,
                    t.quantity,
                    t.reason,
                    t.reference_no,
                    t.notes,
                    t.transacted_by,
                    t.transaction_date
                FROM transactions t
                JOIN consumables c
                ON t.accession_id = c.accession_id
                ORDER BY t.transaction_date DESC
            """)

            return jsonify(cur.fetchall())

    finally:
        conn.close()