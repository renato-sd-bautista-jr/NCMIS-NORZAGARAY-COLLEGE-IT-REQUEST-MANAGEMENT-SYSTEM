import pymysql
import os

def get_db_connection():
    try:
        # Running on Railway
        if os.getenv("MYSQLHOST"):
            conn = pymysql.connect(
                host=os.getenv("MYSQLHOST"),
                user=os.getenv("MYSQLUSER"),
                password=os.getenv("MYSQLPASSWORD"),
                database=os.getenv("MYSQLDATABASE"),
                port=int(os.getenv("MYSQLPORT")),
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to Railway database")

        # Running locally (XAMPP)
        else:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="ncmis",
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to local database")

        return conn

    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    #conn = pymysql.connect(
            #host="maglev.proxy.rlwy.net",
            #user="root",
            #password="mYhPJsfLwPUcVMYfHeoWOpFSmUXXfFIG",
            #database="railway",
            #port=48540