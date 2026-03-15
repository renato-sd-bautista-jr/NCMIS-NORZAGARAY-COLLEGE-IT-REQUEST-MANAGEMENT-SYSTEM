import pymysql
import os

DATABASE_URL = os.getenv("MYSQL_PUBLIC_URL")

conn = pymysql.connect(
    host="maglev.proxy.rlwy.net",
    user="root",
    password="yourpassword",
    database="railway",
    port=48540
)