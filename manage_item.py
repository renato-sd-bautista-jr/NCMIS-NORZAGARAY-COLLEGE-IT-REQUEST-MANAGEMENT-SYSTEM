from db import get_db_connection
import pymysql


def get_devices_with_details():
    conn = get_db_connection()
<<<<<<< HEAD
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    du.accession_id,
                    d.device_id,
                    d.item_name,
                    d.brand_model,
                    du.serial_number,
                    d.quantity,
                    d.device_type,
                    du.status AS unit_status,
                    dep.department_id,
                    dep.department_name   -- ✅ make sure this is selected
                FROM devices d
                JOIN devices_units du ON d.device_id = du.device_id
                LEFT JOIN departments dep ON d.department_id = dep.department_id
                ORDER BY du.accession_id
            """)
            results = cur.fetchall()
            return results
    except Exception as e:
        print(f"Error fetching devices: {e}")
        return []
    finally:
        conn.close()
def get_departments():
    conn = get_db_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:  # ✅ if using pymysql
        cur.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        results = cur.fetchall()
    conn.close()
    return results


def add_device(item_name, brand_model, department_id, serial_number, quantity, device_type, status):
    """
    Adds a new device and one corresponding device unit.
    Works for MySQL (no RETURNING clause).
    """
    conn = get_db_connection()
    try:
        department_id = int(department_id)
        quantity = int(quantity) if quantity else 1

        with conn.cursor() as cur:
            # Insert into devices
            cur.execute("""
                INSERT INTO devices (item_name, brand_model, department_id, quantity, device_type, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item_name, brand_model, department_id, quantity, device_type, status))
=======
    with conn.cursor() as cur:
        cur.execute("""
            SELECT du.accession_id,
                   du.serial_number,
                   du.status AS unit_status,
                   d.device_id,
                   d.item_name,
                   d.brand_model,
                   dept.department_name
            FROM devices_units du
            JOIN devices d ON du.device_id = d.device_id
            LEFT JOIN departments dept ON d.department_id = dept.department_id
            ORDER BY d.item_name, du.accession_id
        """)
        rows = cur.fetchall()
    conn.close()
    return rows


def add_device(item_name, brand_model, department_id, serial_number, quantity, device_type, status):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Insert into devices (main info)
            cursor.execute("""
                INSERT INTO devices
                    (item_name, brand_model, department_id, serial_number, quantity, device_type, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (item_name, brand_model, department_id, serial_number, quantity, device_type, status))
            
            # Get the auto-increment device_id
            device_id = cursor.lastrowid

            # Insert into devices_units (per unit tracking)
            for i in range(int(quantity)):
                cursor.execute("""
                    INSERT INTO devices_units (device_id, serial_number, status)
                    VALUES (%s, %s, %s)
                """, (device_id, serial_number if i == 0 else None, status))

>>>>>>> a0648f6a7a50e5e22ab8e8fe5236864e57a52156
            conn.commit()

            # Get the last inserted device_id
            device_id = cur.lastrowid

            # Insert into devices_units
            cur.execute("""
                INSERT INTO devices_units (device_id, serial_number, status)
                VALUES (%s, %s, %s)
            """, (device_id, serial_number, status))
            conn.commit()

            accession_id = cur.lastrowid
            return accession_id

    except Exception as e:
        conn.rollback()
        print(f"Error adding device: {str(e)}")
        raise
    finally:
        conn.close()
