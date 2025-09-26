import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='ncmis',
       cursorclass=pymysql.cursors.DictCursor  # always returns dict rows
    )