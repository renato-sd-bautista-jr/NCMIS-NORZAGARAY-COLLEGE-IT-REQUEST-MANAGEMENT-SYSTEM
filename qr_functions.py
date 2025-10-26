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
                WHERE accession_id = %s
            """, (accession_id,))
            device = cursor.fetchone()
    finally:
        conn.close()

    if not device:
        return "Device not found", 404

    # Only encode minimal info for QR
    qr_data = f"DEVICE|{device['accession_id']}|{device['serial_no']}|{device['item_name']}"
    return send_qr(qr_data, size=200, filename=f"{device['item_name']}_QR.png")

@qrcode_bp.route('/get_all_device_qrs')
def get_all_device_qrs():
    # Return JSON metadata for all devices for frontend listing
    conn = get_db_connection()
    devices = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT accession_id, item_name, brand_model, serial_no, status FROM devices_full")
            devices = cursor.fetchall()
    finally:
        conn.close()

    # Convert serial key to standard key names for JS
    return jsonify([
        {
            "accession_id": d['accession_id'],
            "item_name": d['item_name'],
            "brand_model": d['brand_model'],
            "serial_number": d['serial_no'],
            "status": d['status']
        } for d in devices
    ])
