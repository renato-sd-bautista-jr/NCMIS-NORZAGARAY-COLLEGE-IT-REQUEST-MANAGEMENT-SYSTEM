from flask import Blueprint, render_template
from db import get_db_connection
import pymysql

maintenance_bp = Blueprint(
    "maintenance_bp",
    __name__,
    url_prefix="/maintenance"
)

@maintenance_bp.route("/history")
def maintenance_history_page():
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
 
    cur.execute("""
    SELECT
        mh.performed_at,
        mh.asset_type,
        mh.asset_id,
        mh.action,
        mh.old_status,
        mh.new_status,
        mh.risk_level,
        mh.health_score,
        mh.performed_by,
        mh.remarks,
        pc.pcname
    FROM maintenance_history mh
    LEFT JOIN pcinfofull pc ON mh.asset_id = pc.pcid
    ORDER BY mh.performed_at DESC
""")
        
        
    records = cur.fetchall()
    conn.close()

    return render_template(
        "maintenance_history1.html",
        records=records
    )
