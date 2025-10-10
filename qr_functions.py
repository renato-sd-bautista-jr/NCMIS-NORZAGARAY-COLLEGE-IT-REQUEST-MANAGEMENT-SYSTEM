import io
import base64
import qrcode
from flask import Blueprint, send_file, jsonify, request, render_template

# Create the blueprint properly (fixed name mismatch)
qrcode_bp = Blueprint('qrcode_bp', __name__, template_folder='templates')

# -------------------------------
# 1️⃣ Route: Render QR Generator Page
# -------------------------------
@qrcode_bp.route('/qrcodegenerator')
def qrcode_generator_page():
    """Render the QR Code Generator HTML page."""
    return render_template('qrcodegenerator.html')


# -------------------------------
# 2️⃣ Generate QR from JSON data
# -------------------------------
@qrcode_bp.route('/generate_qr', methods=['POST'])
def generate_qr():
    """
    Accepts JSON data and returns a generated QR code image.
    Example payload:
    {
        "name": "Laptop Dell XPS",
        "category": "Electronics",
        "serial": "XPS12345"
    }
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Build QR code content
        qr_content = (
            f"Name: {data.get('name', 'N/A')}\n"
            f"Category: {data.get('category', 'N/A')}\n"
            f"Serial: {data.get('serial', 'N/A')}"
        )

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        # Generate image in memory
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)

        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,
            download_name="qr_code.png"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# 3️⃣ Generate QR from query string (?text=...)
# -------------------------------
@qrcode_bp.route('/qr', methods=['GET'])
def qr_from_query():
    """
    Example usage:
    /qr?text=HelloWorld
    """
    text = request.args.get('text')
    if not text:
        return jsonify({"error": "Missing 'text' parameter"}), 400

    img = qrcode.make(text)
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


# -------------------------------
# 4️⃣ Bulk QR generation (returns base64)
# -------------------------------
@qrcode_bp.route('/generate_bulk_qr', methods=['POST'])
def generate_bulk_qr():
    """
    Accepts a list of items and returns their QR data as base64 strings.
    Example payload:
    [
        {"name": "Monitor", "serial": "MN123"},
        {"name": "Keyboard", "serial": "KB456"}
    ]
    """
    data_list = request.get_json(silent=True)
    if not data_list or not isinstance(data_list, list):
        return jsonify({"error": "Invalid input — expected a JSON array"}), 400

    qr_results = []
    for item in data_list:
        qr_content = (
            f"Name: {item.get('name', 'N/A')}\n"
            f"Serial: {item.get('serial', 'N/A')}"
        )
        img = qrcode.make(qr_content)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        qr_results.append({
            "item": item,
            "qr_image": f"data:image/png;base64,{qr_base64}"
        })

    return jsonify(qr_results)
