from flask import Blueprint, jsonify, request, render_template, send_file
import pymysql
from db import get_db_connection
from io import BytesIO
import pandas as pd
from utils.permissions import check_permission

transaction_bp = Blueprint('transaction_bp', __name__, template_folder='templates')


@transaction_bp.route('/transactions')
@check_permission('transaction', 'view')
def transaction_page():
    """Render the transaction history page."""
    # additional data fetching can be inserted here later
    return render_template('transaction.html')
