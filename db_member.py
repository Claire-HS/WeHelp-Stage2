import mysql.connector

def connect_db():
    return mysql.connector.connect(
        user="root",
        password="Ling0424J####",
        host="localhost",
        database="website",
)
print("Database ready!") 

def create_table():
    db_connect = connect_db()
    cursor = db_connect.cursor()
    create_table = """
    CREATE TABLE tp_member (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255)
    );
    """
    cursor.execute(create_table)
    db_connect.commit()
    cursor.close()
    db_connect.close()
    print("資料表 'tp_member' 建立成功！")

# 執行程式
create_table()
    