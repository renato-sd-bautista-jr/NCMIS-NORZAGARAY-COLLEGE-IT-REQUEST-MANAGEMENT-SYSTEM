from db import get_db_connection
from datetime import date
import pymysql

def run_inventory_auto_check():
    conn = get_db_connection()
    today = date.today()

    try:
        with conn.cursor() as cur:

            # PCs
            cur.execute("""
                UPDATE pcinfofull
                SET
                    status = 'Needs Checking',
                    risk_level = 'Medium'
                WHERE status = 'Available'
                AND (
                    last_checked IS NULL
                    OR DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY) < %s
                )
            """, (today,))

            # Devices
            cur.execute("""
                UPDATE devices_full
                SET
                    status = 'Needs Checking',
                    risk_level = 'Medium'
                WHERE status = 'Available'
                AND (
                    last_checked IS NULL
                    OR DATE_ADD(last_checked, INTERVAL maintenance_interval_days DAY) < %s
                )
            """, (today,))

        conn.commit()
        print("Inventory health check executed")

    except Exception as e:
        conn.rollback()
        print("Auto-check failed:", e)

    finally:
        conn.close()