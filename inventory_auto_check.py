from db import get_db_connection
from datetime import date,datetime
import pymysql

def run_inventory_auto_check():
    conn = get_db_connection()
    today = date.today()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # Fetch all PCs
            cur.execute("SELECT * FROM pcinfofull")
            pcs = cur.fetchall()

            for pc in pcs:
                old_status = pc["status"]
                old_risk = pc["risk_level"]

                # Compute new health and risk
                health, risk = calculate_health_and_risk(pc)

                # Determine new status if risk is High
                new_status = old_status
                if risk == "High":
                    new_status = "Needs Checking"

                # Update PC info
                cur.execute("""
                    UPDATE pcinfofull
                    SET health_score = %s,
                        risk_level = %s,
                        status = %s
                    WHERE pcid = %s
                """, (health, risk, new_status, pc["pcid"]))

                # Insert into maintenance_history ONLY if something changed
                if old_status != new_status or old_risk != risk:
                    cur.execute("""
                        INSERT INTO maintenance_history
                        (pcid, asset_type, asset_id, action, old_status, new_status,
                        risk_level, health_score, performed_by, remarks)
                        VALUES (%s, 'PC', %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        pc["pcid"],
                        pc["pcid"],
                        "Auto Risk Update",
                        old_status,
                        new_status,
                        risk,
                        health,
                        "System",
                        f"Auto-updated on {today}"
                    ))

        conn.commit()
        print("Inventory auto-check and logging executed successfully")

    except Exception as e:
        conn.rollback()
        print("Auto-check failed:", e)

    finally:
        conn.close()

def parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None
def calculate_health_and_risk(pc):
    score = 100
    today = date.today()

    date_acquired = parse_date(pc.get("date_acquired"))
    last_checked = parse_date(pc.get("last_checked"))
    interval = pc.get("maintenance_interval_days") or 30
    status = pc.get("status") or ""

    # ---- Age penalty ----
    if date_acquired:
        age_years = (today - date_acquired).days / 365
        if age_years > 5:
            score -= 30
        elif age_years > 3:
            score -= 20
        elif age_years > 1:
            score -= 10

    # ---- Maintenance delay ----
    if last_checked:
        overdue_days = (today - last_checked).days - interval
        if overdue_days > 90:
            score -= 30
        elif overdue_days > 30:
            score -= 20
        elif overdue_days > 0:
            score -= 10
    else:
        score -= 20  # never checked

    # ---- Status penalty ----
    if status == "Needs Checking":
        score -= 15
    elif status == "In Used":
        score -= 5

    # ---- Clamp ----
    score = max(score, 0)

    # ---- Risk level ----
    if score < 50:
        risk = "High"
    elif score < 80:
        risk = "Medium"
    else:
        risk = "Low"

    return score, risk

    score = 100
    today = date.today()

    # ---- Age penalty ----
    if pc["date_acquired"]:
        age_years = (today - pc["date_acquired"]).days / 365
        if age_years > 5:
            score -= 30
        elif age_years > 3:
            score -= 20
        elif age_years > 1:
            score -= 10

    # ---- Maintenance delay ----
    if pc["last_checked"]:
        overdue_days = (today - pc["last_checked"]).days - pc["maintenance_interval_days"]
        if overdue_days > 90:
            score -= 30
        elif overdue_days > 30:
            score -= 20
        elif overdue_days > 0:
            score -= 10
    else:
        score -= 20  # never checked

    # ---- Status penalty ----
    if pc["status"] == "Needs Checking":
        score -= 15
    elif pc["status"] == "In Used":
        score -= 5

    # ---- Clamp score ----
    score = max(score, 0)

    # ---- Risk level ----
    if score < 50:
        risk = "High"
    elif score < 80:
        risk = "Medium"
    else:
        risk = "Low"

    return score, risk