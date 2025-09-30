# manage_item.py
from db import get_db_connection

def get_devices_with_details():
    conn = get_db_connection()
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

            conn.commit()
    finally:
        conn.close()