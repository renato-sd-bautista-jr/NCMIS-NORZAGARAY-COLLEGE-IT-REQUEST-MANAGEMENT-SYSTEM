import pymysql
import os

def get_db_connection():
    try:
        # If running on Railway
        if os.getenv("MYSQLHOST"):
            conn = pymysql.connect(
                host=os.getenv("maglev.proxy.rlwy.net"),
                user=os.getenv("root"),
                password=os.getenv("mYhPJsfLwPUcVMYfHeoWOpFSmUXXfFIG"),
                database=os.getenv("railway"),
                port=int(os.getenv("48540")),
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to Railway database")

        # If running locally (XAMPP)
        else:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="ncmis",
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to local XAMPP database")

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