from flask import render_template, request, redirect, url_for, session, Flask, flash, Blueprint,g

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
from sidebar import get_user_access




app = Flask(__name__)
app.secret_key = 'a2f1e4f8f60b4f81a8d32dd0b3c2ce90'
app.register_blueprint(login_bp)
app.register_blueprint(report_bp)
app.register_blueprint(userborrow_bp)
app.register_blueprint(manage_pc_bp)
app.register_blueprint(qrcode_bp)
app.register_blueprint(manage_user_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(manage_department_bp)
app.register_blueprint(manage_inventory_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(manage_item_bp, url_prefix='/manage_inventory')


# ✅ Context processor to make user access available globally in templates
@app.context_processor
def inject_user_access():
    user_id = session.get('user_id')
    if not user_id:
        return {'user_access': {}}  # default empty access if not logged in
    return {'user_access': get_user_access(user_id)}



@app.context_processor
def inject_user_permissions():
    """Make user data and permissions available in all templates"""
    user = session.get('user')
    if user:
        return {
            'permissions': user.get('permissions', {}),
            'is_admin': user.get('is_admin', 0)
        }
    return {'permissions': {}, 'is_admin': 0}
@app.before_request
def load_user_permissions():
    if 'user' in session:
        user = session['user']
        if isinstance(user.get('permissions'), str):
            try:
                user['permissions'] = json.loads(user['permissions'])
            except json.JSONDecodeError:
                user['permissions'] = {}
        g.permissions = user.get('permissions', {})
    else:
        g.permissions = {}

@app.route('/')
def index():
    return redirect(url_for('login_bp.login'))

if __name__ == '__main__':
    app.run(debug=True)