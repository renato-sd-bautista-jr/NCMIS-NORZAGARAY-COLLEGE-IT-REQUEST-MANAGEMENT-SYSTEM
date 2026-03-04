from flask import Blueprint, jsonify, request, render_template, send_file
import pymysql
from db import get_db_connection
from io import BytesIO
import pandas as pd
from utils.permissions import check_permission

stock = Blueprint('stock_room_bp', __name__, template_folder='templates')


# -------------------------------
# 1️⃣ Render Stock Room Page


# -------------------------------
@stock.route('/stock-room')
@check_permission('stock_room', 'view')
def stock_room_page():
    return render_template('stockroom.html')



@stock.route('/get-stock-room', methods=['GET'])
@check_permission('stock_room', 'view')
def get_stock_room():

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        query = """
        -- 📦 DEVICES (grouped)
        SELECT 
    LOWER(TRIM(device_type)) AS category,
    LOWER(TRIM(item_name)) AS item_name,
    LOWER(TRIM(brand_model)) AS brand_model,
    SUM(quantity) AS total_quantity,
    'Device' AS source
FROM devices_full
WHERE 
    item_name IS NOT NULL 
    AND item_name != ''
    AND device_type IS NOT NULL
    AND device_type != ''
    AND quantity > 0
    AND device_type NOT REGEXP '^[0-9]+$'
GROUP BY 
    LOWER(TRIM(device_type)),
    LOWER(TRIM(item_name)),
    LOWER(TRIM(brand_model))

        UNION ALL

        -- 💻 PC PARTS (Motherboard example)
        SELECT 
            'Motherboard' AS category,
            motherboard AS item_name,
            motherboard AS brand_model,
            COUNT(*) AS total_quantity,
            'PC Part' AS source
        FROM pcinfofull
        WHERE motherboard IS NOT NULL AND motherboard != ''
        GROUP BY motherboard

        UNION ALL

        -- RAM
        SELECT 
            'RAM',
            ram,
            ram,
            COUNT(*),
            'PC Part'
        FROM pcinfofull
        WHERE ram IS NOT NULL AND ram != ''
        GROUP BY ram

        UNION ALL

        -- STORAGE
        SELECT 
            'Storage',
            storage,
            storage,
            COUNT(*),
            'PC Part'
        FROM pcinfofull
        WHERE storage IS NOT NULL AND storage != ''
        GROUP BY storage

        UNION ALL

        -- GPU
        SELECT 
            'GPU',
            gpu,
            gpu,
            COUNT(*),
            'PC Part'
        FROM pcinfofull
        WHERE gpu IS NOT NULL AND gpu != ''
        GROUP BY gpu

        UNION ALL

        -- PSU
        SELECT 
            'PSU',
            psu,
            psu,
            COUNT(*),
            'PC Part'
        FROM pcinfofull
        WHERE psu IS NOT NULL AND psu != ''
        GROUP BY psu

        UNION ALL

        -- CASING
        SELECT 
            'Casing',
            casing,
            casing,
            COUNT(*),
            'PC Part'
        FROM pcinfofull
        WHERE casing IS NOT NULL AND casing != ''
        GROUP BY casing

        ORDER BY category, item_name
        """

        cursor.execute(query)
        data = cursor.fetchall()

        return jsonify(data)

    except Exception as e:
        print(f"❌ Error fetching stock room: {e}")
        return jsonify([])

    finally:
        cursor.close()
        conn.close()

