import pymysql
import os

def get_db_connection():

    # If running on Railway
    if os.getenv("MYSQL_PUBLIC_URL"):
        return pymysql.connect(
            host=os.getenv("MYSQLHOST_PUBLIC") or "maglev.proxy.rlwy.net",
            user=os.getenv("MYSQLUSER") or "root",
            password=os.getenv("MYSQLPASSWORD") or "mYhPJsfLwPUcVMYfHeoWOpFSmUXXfFIG",
            database=os.getenv("MYSQLDATABASE") or "railway",
            port=int(os.getenv("MYSQLPORT") or 48540),
            cursorclass=pymysql.cursors.DictCursor
        )

    # If running locally (XAMPP)
    else:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="ncmis",
            cursorclass=pymysql.cursors.DictCursor
        )