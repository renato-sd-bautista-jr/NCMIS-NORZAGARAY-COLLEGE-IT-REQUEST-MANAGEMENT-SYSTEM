import os,pymysql

# def get_db_connection():
#     return pymysql.connect(
#         host='localhost',
#         user='root',
#         password='',
#         database='ncmis',
#        cursorclass=pymysql.cursors.DictCursor  # always returns dict rows
#     )



def get_db_connection():

    host = os.getenv("MYSQLHOST", "localhost")
    user = os.getenv("MYSQLUSER", "root")
    password = os.getenv("MYSQLPASSWORD", "")
    database = os.getenv("MYSQLDATABASE", "ncmis")
    port = int(os.getenv("MYSQLPORT", 3306))

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )