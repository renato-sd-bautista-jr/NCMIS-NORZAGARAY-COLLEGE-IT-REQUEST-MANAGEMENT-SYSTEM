# manage_item.py
from db import get_db_connection

def get_devices_with_details():
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
        """)
        return cur.fetchall()
    


    

def add_device(device_name, quantity, department_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO devices (device_name, quantity, department_id)
                VALUES (%s, %s, %s)
                """,
                (device_name, quantity, department_id)
            )
            conn.commit()
    finally:
        conn.close()