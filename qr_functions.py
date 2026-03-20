# qrcode_bp (qr_function.py or similar)
import io
import qrcode
from flask import Blueprint, send_file, jsonify, request, render_template, url_for
from db import get_db_connection
import pymysql
import json
from io import BytesIO  

qrcode_bp = Blueprint('qrcode_bp', __name__, template_folder='templates')

@qrcode_bp.route('/qrcodegenerator')
def qrcode_generator_page():
    return render_template('qrcodegenerator.html')
def generate_qr_image(data: str, size: int = 200):
    """
    Generate a QR code image as a BytesIO object.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img = img.resize((size, size))
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf
@qrcode_bp.route('/get_item_for_print/<string:item_type>/<int:item_id>')
def get_item_for_print(item_type, item_id):
    """
    Fetch item details for printing.
    item_type: 'device' or 'pc'
    item_id: accession_id (device) OR pcid (pc)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:

            if item_type == 'device':
                cursor.execute("""
                    SELECT 
                        accession_id,
                        item_name,
                        brand_model,
                        quantity,
                        acquisition_cost,
                        date_acquired,
                        accountable,
                        serial_no,
                        municipal_serial_no,
                        device_type,
                        department_id,
                        status,
                        last_checked,
                        maintenance_interval_days,
                        health_score,
                        risk_level
                    FROM devices_full
                    WHERE accession_id = %s
                """, (item_id,))
            
            elif item_type == 'pc':
                cursor.execute("""
                    SELECT 
                        pcid,
                        pcname,
                        location,
                        quantity,
                        acquisition_cost,
                        date_acquired,
                        accountable,
                        serial_no,
                        municipal_serial_no,
                        status,
                        monitor,
                        motherboard,
                        ram,
                        storage,
                        gpu,
                        psu,
                        casing,
                        last_checked,
                        maintenance_interval_days,
                        health_score,
                        risk_level
                    FROM pcinfofull
                    WHERE pcid = %s
                """, (item_id,))
                cursor.execute("""
                    SELECT 
                        pcid,
                        pcname,
                        location,
                        quantity,
                        acquisition_cost,
                        date_acquired,
                        accountable,
                        serial_no,
                        municipal_serial_no,
                        status,
                        monitor,
                        motherboard,
                        ram,
                        storage,
                        gpu,
                        psu,
                        casing,
                        last_checked,
                        maintenance_interval_days,
                        health_score
                    FROM pcinfofull
                    WHERE pcid = %s
                """, (item_id,))
            
            else:
                return jsonify({"error": "Invalid item type"}), 400

            item = cursor.fetchone()

    finally:
        conn.close()

    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item)
def send_qr(data: str, size: int = 200, filename: str = "qr.png"):
    """
    Return a Flask response sending the QR code image.
    """
    buf = generate_qr_image(data, size)
    return send_file(buf, mimetype='image/png', download_name=filename)


@qrcode_bp.route('/device_qr/<int:accession_id>')
def device_qr(accession_id):
    # Fetch device info
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT accession_id, item_name, brand_model, serial_no
                FROM devices_full
                WHERE status = 'Available' AND accession_id = %s 
            """, (accession_id,))
            device = cursor.fetchone()
    finally:
        conn.close()

    if not device:
        return "Device not found", 404

    # Only encode minimal info for QR
    qr_data = f"DEVICE|{device['accession_id']}|{device['serial_no']}|{device['item_name']}"
    return send_qr(qr_data, size=200, filename=f"{device['item_name']}_QR.png")



@qrcode_bp.route('/get_all_pc_qrs')
def get_all_pc_qrs():
    conn = get_db_connection()
    pcs = []

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:

            cursor.execute("""
                SELECT 
                    pcid,
                    pcname,
                    serial_no,
                    municipal_serial_no,
                    location,
                    status
                FROM pcinfofull
                WHERE status = 'Available'
                ORDER BY pcid DESC
               
            """)

            pcs = cursor.fetchall()

    finally:
        conn.close()

    return jsonify([
        {
            "pcid": pc['pcid'],
            "pcname": pc['pcname'],
            "serial_number": pc['serial_no'],
            "municipal_serial": pc['municipal_serial_no'],
            "location": pc['location'],
            "status": pc['status']
        }
        for pc in pcs
    ])

@qrcode_bp.route('/pc_qr/<int:pcid>')
def pc_qr(pcid):

    conn = get_db_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:

            cursor.execute("""
                SELECT pcid, pcname, serial_no, location
                FROM pcinfofull
                WHERE pcid = %s and status == 'Active'
            """, (pcid,))

            pc = cursor.fetchone()

    finally:
        conn.close()

    if not pc:
        return "PC not found", 404

    qr_data = f"PC|{pc['pcid']}|{pc['serial_no']}|{pc['pcname']}|{pc['location']}"

    return send_qr(qr_data, size=200, filename=f"{pc['pcname']}_QR.png")