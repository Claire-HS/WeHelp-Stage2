import mysql.connector

def connect_db():
    return mysql.connector.connect(
        user="root",
        password="Ling0424J####",
        host="localhost",
        database="website",
    )
print("Database ready!") 

# 付款紀錄
def create_table():
    db_connect = connect_db()
    cursor = db_connect.cursor()
    create_table = """
        CREATE TABLE tp_payment (
            id INT PRIMARY KEY AUTO_INCREMENT, 
            order_number VARCHAR(255) UNIQUE,
            status INT,
            msg TEXT,
            currency VARCHAR(255), 
            amount INT,
            rec_trade_id VARCHAR(255),
            bank_transaction_id VARCHAR(255),
            paid_at DATETIME DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES tp_order(order_number)
        );
    """
    cursor.execute(create_table)
    db_connect.commit()
    cursor.close()
    db_connect.close()
    print("資料表 'tp_payment' 建立成功！")

# 執行程式
create_table()