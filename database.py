import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="odontologia_aquino",
        port=3306
    )
