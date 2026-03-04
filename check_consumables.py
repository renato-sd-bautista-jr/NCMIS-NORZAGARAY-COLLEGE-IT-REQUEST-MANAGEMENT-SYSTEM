from db import get_db_connection
import pymysql

conn = get_db_connection()
with conn.cursor(pymysql.cursors.DictCursor) as cur:
    cur.execute("SELECT COUNT(*) AS cnt FROM devices_full WHERE device_type='Consumable'")
    print(cur.fetchone())
    cur.execute("SELECT accession_id,item_name FROM devices_full WHERE device_type='Consumable' LIMIT 5")
    print(cur.fetchall())
conn.close()
