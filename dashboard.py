from db import get_db_connection

def get_concern_stats():
    stats = {
        'total': 0,
        'pending': 0,
        'ongoing': 0,
        'resolved': 0
    }
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM concerns")
            stats['total'] = cur.fetchone()['cnt']

            cur.execute("SELECT COUNT(*) AS cnt FROM concerns WHERE status='Pending'")
            stats['pending'] = cur.fetchone()['cnt']

            cur.execute("SELECT COUNT(*) AS cnt FROM concerns WHERE status='Ongoing'")
            stats['ongoing'] = cur.fetchone()['cnt']

            # resolved from history table
            cur.execute("SELECT COUNT(*) AS cnt FROM concern_history WHERE status='Resolved'")
            stats['resolved'] = cur.fetchone()['cnt']
    finally:
        conn.close()
    return stats
def get_all_available_devices():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.device_id,
                   d.item_name,
                   d.brand_model,
                   d.serial_number,
                   d.quantity,
                   d.device_type,
                   d.status,
                   dep.department_name
            FROM devices d
            JOIN departments dep ON d.department_id = dep.department_id
            WHERE d.status = 'Available'
        """)
        return cur.fetchall()
def get_all_available_units():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT du.accession_id,
                   d.item_name,
                   d.brand_model,
                   du.serial_number,
                   dep.department_name
            FROM devices_units du
            JOIN devices d ON du.device_id = d.device_id
            JOIN departments dep ON d.department_id = dep.department_id
            WHERE du.status = 'Available'
        """)
        return cur.fetchall()
def get_all_users():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, username, faculty_name, email, is_admin
            FROM users
            ORDER BY username ASC
        """)
        return cur.fetchall()

def get_recent_concerns(limit=5):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT concern_id AS id, description, status, created_at "
                "FROM concerns ORDER BY created_at DESC LIMIT %s", (limit,))
            return cur.fetchall()
    finally:
        conn.close()
def get_borrow_requests():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    br.borrow_id,
                    CONCAT(br.last_name, ', ', br.first_name, ' ', br.middle_initial) AS borrower_name,
                    d.item_name,
                    du.serial_number,
                    br.borrow_date,
                    br.return_date,
                    br.reason,
                    br.status
                FROM borrow_requests br
                JOIN devices d ON br.device_id = d.device_id
                LEFT JOIN devices_units du ON br.device_id = du.device_id
                ORDER BY br.borrow_date DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()
