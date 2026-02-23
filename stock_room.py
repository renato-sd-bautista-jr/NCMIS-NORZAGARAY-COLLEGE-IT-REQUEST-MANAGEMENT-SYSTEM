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
    """Render the Stock Room HTML page."""
    return render_template('stockroom.html')
