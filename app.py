from flask import render_template, request, redirect, url_for, session, Flask, flash, Blueprint

from login import login_bp
from userborrow import userborrow_bp
from qr_functions import qrcode_bp
from manage_user import manage_user_bp
from dashboard import dashboard_bp
from manage_item import manage_item_bp
from report import report_bp
from manage_pc import manage_pc_bp
from manage_department import manage_department_bp
from manage_inventory import manage_inventory_bp
from notification import notification_bp



app = Flask(__name__)
app.secret_key = 'a2f1e4f8f60b4f81a8d32dd0b3c2ce90'
app.register_blueprint(login_bp)
app.register_blueprint(report_bp)
app.register_blueprint(userborrow_bp)
app.register_blueprint(manage_pc_bp)
app.register_blueprint(qrcode_bp)
app.register_blueprint(manage_item_bp)
app.register_blueprint(manage_user_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(manage_department_bp)
app.register_blueprint(manage_inventory_bp)
app.register_blueprint(notification_bp)




@app.route('/')
def index():
    return redirect(url_for('login_bp.login'))

if __name__ == '__main__':
    app.run(debug=True)