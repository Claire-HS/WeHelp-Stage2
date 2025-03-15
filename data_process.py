import json
import mysql.connector


def connect_db():
    return mysql.connector.connect(
        user="root",
        password="Ling0424J",
        host="localhost",
        database="website",
)
# print("Database ready!")


def create_table():
    db_connect = connect_db()
    cursor = db_connect.cursor()
    create_table = """
    CREATE TABLE attractions (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255),
        category VARCHAR(255),
        description TEXT,
        address VARCHAR(255),
        transport TEXT,
        mrt VARCHAR(255),
        lat DOUBLE,
        lng DOUBLE,
        images TEXT
    );
    """
    cursor.execute(create_table)
    db_connect.commit()
    cursor.close()
    db_connect.close()
    print("資料表 'attractions' 建立成功！")

def insert_data():
    db_connect = connect_db()
    cursor = db_connect.cursor()
    insert_data = """
    INSERT INTO attractions (name, category, description, address, transport, mrt, lat, lng, images)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for item in formatted_data:
        data_tuple = (
            item["name"],
            item["category"],
            item["description"],
            item["address"],
            item["transport"],
            item["mrt"],
            item["lat"],
            item["lng"],
            json.dumps(item["images"])  
        )
        cursor.execute(insert_data, data_tuple)
    db_connect.commit()
    cursor.close()
    db_connect.close()
    print(f"已寫入 {len(formatted_data)} 筆資料！")





def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def process_data(data):
    formatted_data = []
    for item in data["result"]["results"]:
        formatted_item = {
            "name": item["name"],
            "category": item["CAT"],
            "description": item["description"],
            "address": item["address"],
            "transport": item["direction"],
            "mrt": item["MRT"],
            "lat": item["latitude"],
            "lng": item["longitude"],
            "images": ["https://" + url 
                       for url in item["file"].split("https://") 
                       if url.lower().endswith((".jpg", ".png"))
                       ],
        }
        formatted_data.append(formatted_item)
    return formatted_data





if __name__ == "__main__":
    file_path = "data/taipei-attractions.json"
    data = load_json(file_path)
    formatted_data = process_data(data)
    create_table()
    insert_data()
    # for i in formatted_data:
    #     print(i)



