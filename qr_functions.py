# qrcode_bp (qr_function.py or similar)
import io
import qrcode
from flask import Blueprint, send_file, jsonify, request, render_template, url_for
from db import get_db_connection
import pymysql

qrcode_bp = Blueprint('qrcode_bp', __name__, template_folder='templates')

@qrcode_bp.route('/qrcodegenerator')
def qrcode_generator_page():
    return render_template('qrcodegenerator.html')

# Dynamic PNG generator (no storage)
@qrcode_bp.route('/device_qr/<accession_id>')
def generate_device_qr(accession_id):
    """
    Return a PNG QR image built from device info; accession_id treated as string.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT df.accession_id, df.item_name, df.brand_model, df.serial_number,
                       df.quantity, df.device_type, df.status, d.department_name
                FROM devices_full df
                LEFT JOIN departments d ON df.department_id = d.department_id
                WHERE df.accession_id = %s
            """, (accession_id,))
            device = cur.fetchone()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # Build QR content — you can change to a URL if you want scannable link
        qr_content = (
            f"Accession ID: {device['accession_id']}\n"
            f"Item: {device['item_name']}\n"
            f"Brand: {device['brand_model']}\n"
            f"Serial: {device['serial_number']}\n"
            f"Department: {device.get('department_name','N/A')}\n"
            f"Status: {device['status']}"
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@qrcode_bp.route('/pc_qr/<pcid>')
def generate_pc_qr(pcid):
    """
    Return a PNG QR image built from PC info; pcid treated as string.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.pcid, p.pcname, p.department_id, d.department_name,
                    p.location, p.quantity, p.acquisition_cost, p.date_acquired,
                    p.accountable, p.serial_no, p.municipal_serial_no,
                    p.status, p.note, p.monitor, p.motherboard, p.ram,
                    p.storage, p.gpu, p.psu, p.casing, p.other_parts
                FROM pcs_full p
                LEFT JOIN departments d ON p.department_id = d.department_id
                WHERE p.pcid = %s
            """, (pcid,))
            pc = cur.fetchone()

        if not pc:
            return jsonify({"error": "PC not found"}), 404

        # 🧩 Build QR content (include main details; skip null/empty ones)
        qr_lines = [
            f"PC ID: {pc['pcid']}",
            f"PC Name: {pc['pcname']}",
            f"Department: {pc.get('department_name', 'N/A')}",
            f"Location: {pc.get('location', 'N/A')}",
            f"Quantity: {pc.get('quantity', 'N/A')}",
            f"Acquisition Cost: {pc.get('acquisition_cost', 'N/A')}",
            f"Date Acquired: {pc.get('date_acquired', 'N/A')}",
            f"Accountable: {pc.get('accountable', 'N/A')}",
            f"Serial No: {pc.get('serial_no', 'N/A')}",
            f"Municipal Serial No: {pc.get('municipal_serial_no', 'N/A')}",
            f"Status: {pc.get('status', 'N/A')}",
            f"Note: {pc.get('note', 'N/A')}",
            "",
            "🔧 Parts:",
            f"Monitor: {pc.get('monitor', 'N/A')}",
            f"Motherboard: {pc.get('motherboard', 'N/A')}",
            f"RAM: {pc.get('ram', 'N/A')}",
            f"Storage: {pc.get('storage', 'N/A')}",
            f"GPU: {pc.get('gpu', 'N/A')}",
            f"PSU: {pc.get('psu', 'N/A')}",
            f"Casing: {pc.get('casing', 'N/A')}",
            f"Other Parts: {pc.get('other_parts', 'N/A')}"
        ]

        # Join into a single string for the QR content
        qr_content = "\n".join(qr_lines)

        # 🟦 Generate QR code
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # 🧾 Convert to BytesIO and return as PNG
        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# Small view page so we can redirect and show the QR immediately after add
@qrcode_bp.route('/qrcode/view/<accession_id>')
def view_device_qr(accession_id):
    """
    Render a page showing the QR image (image src points to /device_qr/<id>).
    """
    return render_template('view_qr.html', accession_id=accession_id)

# Endpoint used by the QR list page (optional)
@qrcode_bp.route('/get_all_device_qrs')
def get_all_device_qrs():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT accession_id, item_name, brand_model, serial_number, status
                FROM devices_full
                ORDER BY accession_id DESC
            """)
            devices = cur.fetchall()
            return jsonify(devices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
