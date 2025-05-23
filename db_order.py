import mysql.connector

def connect_db():
    return mysql.connector.connect(
        user="root",
        password="Ling0424J####",
        host="localhost",
        database="website",
    )
print("Database ready!") 

# 正式訂單
def create_table():
    db_connect = connect_db()
    cursor = db_connect.cursor()
    create_table = """
        CREATE TABLE tp_order (
            id INT PRIMARY KEY AUTO_INCREMENT, 
            member_id INT,
            order_number VARCHAR(255) UNIQUE,
            order_price INT,
            paymentStatus VARCHAR(255) CHECK (paymentStatus IN ("PAID", "UNPAID")),
            attractionId INT,
            tourDate DATE,
            dateTime VARCHAR(255),
            contact_name VARCHAR(255),
            contact_email VARCHAR(255),
            contact_phone VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP DEFAULT NULL
        );
    """
    cursor.execute(create_table)
    db_connect.commit()
    cursor.close()
    db_connect.close()
    print("資料表 'tp_order' 建立成功！")

# 執行程式
create_table()