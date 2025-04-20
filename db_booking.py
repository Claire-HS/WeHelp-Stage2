import mysql.connector

def connect_db():
    return mysql.connector.connect(
        user="root",
        password="Ling0424J####",
        host="localhost",
        database="website",
    )
print("Database ready!") 

# 會員待訂清單，確認訂購後轉tp_order，並刪除待訂項目。 
def create_table():
    db_connect = connect_db()
    cursor = db_connect.cursor()
    create_table = """
        CREATE TABLE tp_booking (
            id INT PRIMARY KEY AUTO_INCREMENT, 
            member_id INT,
            attractionId INT,
            tourDate DATE,
            dateTime VARCHAR(255),
            price INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    cursor.execute(create_table)
    db_connect.commit()
    cursor.close()
    db_connect.close()
    print("資料表 'tp_booking' 建立成功！")

# 執行程式
create_table()