
from flask import Blueprint, send_file, jsonify, request, render_template

# Create the blueprint properly (fixed name mismatch)
report_bp = Blueprint('report_bp', __name__, template_folder='templates')

# -------------------------------
# 1️⃣ Route: Render QR Generator Page
# -------------------------------
@report_bp.route('/reportgenerator')
def qrcode_generator_page():
    """Render the QR Code Generator HTML page."""
    return render_template('qrcodegenerator.html')

@report_bp.route('/reportlist')
def qrcode_list():
    return render_template('qrcodegenerator.html')

