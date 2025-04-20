from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import mysql.connector
import json
from collections import Counter
from typing import Annotated
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, InvalidTokenError
from enum import Enum
from datetime import date
import random
import string
from tappay import call_tappay





app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

db_connect = mysql.connector.connect(
    user="root",
    password="Ling0424J####",
    host="localhost",
    database="website",
)

secret_key = "H$L511_O527%S"

# Token 檢查工具（FastAPI 內建）
bearer_scheme = HTTPBearer()


class Signup(BaseModel):
	name: str
	email: str
	password: str

class Signin(BaseModel):
	email: str
	password: str

class TimeSel(str, Enum):
	morning = "morning"
	afternoon = "afternoon"

class BookingRequest(BaseModel):
    attractionId: int
    date: date
    time: TimeSel
    price: int

class Member(BaseModel):
	member_id: int

class Attraction(BaseModel):
	id: int
	name: str
	address: str
	image: str 

class Contact(BaseModel):
	name: str
	email: EmailStr
	phone: str

class Trip(BaseModel):
	attraction: Attraction
	date: date
	time: TimeSel

class OrderData(BaseModel):
	price: int
	trip: Trip
	contact: Contact

class OrderRequest(BaseModel):
	prime: str
	order: OrderData



# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


@app.get("/api/attractions")
async def search_pages(
    page: Annotated[int, Query(..., ge=0, description="頁碼，必填，最小值為0")],
    keyword: str | None = Query(default=None, description="關鍵字，選填")
):
	try:
		cursor = db_connect.cursor(dictionary=True)
	
		limit = 12 
		offset = page * limit 
		
		if keyword: 
			# 計算search結果的筆數
			cursor.execute("SELECT COUNT(*) AS total_count FROM attractions WHERE mrt=%s OR name LIKE %s ORDER BY id ASC ",(keyword,f"%{keyword}%"))
			match_count = cursor.fetchone()
			result_count = match_count["total_count"]

			total_pages = (result_count // limit) + (1 if result_count % limit > 0 else 0)
			next_page = page + 1 if page + 1 < total_pages else None
			
			# 關鍵字完全比對捷運站名稱、或模糊比對景點名稱，每頁最多顯示12筆搜尋結果
			sql = """
                    SELECT *
                    FROM 
                        (SELECT * FROM attractions WHERE mrt=%s OR name LIKE %s ORDER BY id ASC) 
                            AS TableWithKeyword 
                    ORDER BY TableWithKeyword.id ASC
					LIMIT %s 
					OFFSET %s
                """

			cursor.execute(sql,(keyword,f"%{keyword}%",limit,offset))
			match_attractions = cursor.fetchall()
			# print("match_attractions=",match_attractions)
			cursor.close()

			for item in match_attractions:
				if isinstance(item["images"], str):
					item["images"] = json.loads(item["images"])
			return {
                "nextPage": next_page,
                "data": match_attractions
            } 
		else: 
            # find total
			cursor.execute("SELECT COUNT(*) AS total FROM attractions")
			data_count = cursor.fetchone()["total"]
			
			total_pages = (data_count // limit) + (1 if data_count % limit > 0 else 0)
			next_page = page + 1 if page + 1 < total_pages else None
		
            # find goal data
			cursor.execute("SELECT * FROM attractions ORDER BY id ASC LIMIT %s OFFSET %s",(limit,offset))
			attractions = cursor.fetchall()
			
			cursor.close()
			
			for item in attractions:
				if isinstance(item["images"], str):
					item["images"] = json.loads(item["images"])
					
			return {
                "nextPage": next_page,
                "data": attractions
            } 
				
	except:
		return JSONResponse(
            status_code = 500,
            content = {
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )



@app.get("/api/attraction/{attractionID}")
async def search_attractionID(request: Request, attractionID: Annotated[int,None]):
	try:
		cursor = db_connect.cursor(dictionary=True)
		cursor.execute("SELECT id, name, category, description, address, transport, mrt, lat, lng, images FROM attractions WHERE id = %s",(attractionID,))
		attraction = cursor.fetchone()
		cursor.close()

		if attraction is None:
			return JSONResponse(
				status_code = 400,
				content = {
					"error": True,
                	"message": "景點編號不正確"
				}
			)
	except:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)
	else:
		attraction["images"] = json.loads(attraction["images"])
		return{"data": attraction}


@app.get("/api/mrts")
async def mrt_attractions(request: Request):
	try:
		cursor = db_connect.cursor()
		cursor.execute("SELECT mrt FROM attractions WHERE mrt IS NOT NULL")
		mrts = cursor.fetchall()
		cursor.close()
		# print(mrts)
		mrt_stations = [mrt[0] for mrt in mrts]
		# print(mrt_stations)
		mrt_station_counts = Counter(mrt_stations)
		# print(mrt_station_counts)
		sorted_mrt_stations = [station[0] for station in mrt_station_counts.most_common()]
	except:
		return JSONResponse(
            status_code = 500,
            content = {
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )
	else:
		return {"data": sorted_mrt_stations}
	

@app.post("/api/user")
async def signup(user: Signup):
	try:
		cursor = db_connect.cursor()
		cursor.execute("SELECT * FROM tp_member WHERE BINARY email=%s", (user.email,))
		existing_user = cursor.fetchone()
		if existing_user:
			return JSONResponse(
				status_code = 400,
				content = {
					"error": True,
  					"message": "Email 已註冊過帳戶"
				}
			)
		else:
			cursor.execute("INSERT INTO tp_member(name, email, password) VALUES(%s, %s, %s)", (user.name, user.email, user.password))
			db_connect.commit()
			cursor.close()
	except:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)
	else: 
		return JSONResponse(
			status_code = 200,
			content = {
				"ok": True
			} 
		)

@app.put("/api/user/auth")
async def signin(user: Signin):
	try:
		cursor = db_connect.cursor()
		cursor.execute("SELECT * FROM tp_member WHERE BINARY email=%s AND password=%s", (user.email, user.password))
		member_checked = cursor.fetchone()
		cursor.close()
		if member_checked:
			user_payload = {
				"member_id": member_checked[0],   
				"member_name": member_checked[1],
				"member_email": member_checked[2],
				"iat": datetime.now(timezone.utc),  # JWT 頒發時間
				"exp": datetime.now(timezone.utc) + timedelta(days=7)  # JWT 過期時間
			}

			token = jwt.encode(user_payload, secret_key, algorithm="HS256")

			return JSONResponse(
				status_code = 200,
				content = {
					"token": token
				}
			)
	except:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)	
	else:
		return JSONResponse(
			status_code = 400,
			content = {
				"error": True,
  				"message": "電子信箱或密碼錯誤"
			}
		)	

@app.get("/api/user/auth")
async def get_user_info(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
	try:
		decoded_token = jwt.decode(token.credentials, secret_key, algorithms=["HS256"])

		member_info = {
			"id": decoded_token["member_id"],
            "name": decoded_token["member_name"],
            "email": decoded_token["member_email"]
		}

		return JSONResponse(
			status_code = 200,
			content = {
				"data" : member_info
			}
		)
	except (ExpiredSignatureError, InvalidTokenError):
		return {"data": None}


def get_current_member(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Member:
	try:
		decoded_token = jwt.decode(token.credentials, secret_key, algorithms=["HS256"])
		return Member(
			member_id = decoded_token.get("member_id"),
		)
	except Exception:
		raise HTTPException(status_code=401, detail="無效的憑證") 

@app.post("/api/booking")
async def create_or_update_booking(booking: BookingRequest,
								   member: Member = Depends(get_current_member)):
	# 檢查登入狀態
	try:
		if member.member_id is None:
			return JSONResponse(
				status_code = 403,
				content = {
					"error": True,
  					"message": "未登入系統，無法進行預約!"
				} 
			)
		# 驗證時段價格
		elif booking.time == "morning" and booking.price != 2000:
			return JSONResponse(
				status_code = 400,
				content = {
					"error": True,
  					"message": "預約失敗，行程價格有誤！"
				} 
			)
		elif booking.time == "afternoon" and booking.price != 2500:
			return JSONResponse(
				status_code = 400,
				content = {
					"error": True,
  					"message": "預約失敗，行程價格有誤！"
				} 
			)
			
		cursor = db_connect.cursor()
		# 目前限制最多一筆預約(未付款)
		cursor.execute("SELECT * FROM tp_booking WHERE member_id = %s", (member.member_id,))
		existing = cursor.fetchone()

		# 檢查是否已有預約項目，若有，更新預約; 若無，新增當前預約
		if existing:
			cursor.execute("UPDATE tp_booking SET attractionId =%s, tourDate =%s, dateTime =%s, price =%s, created_at=%s WHERE member_id =%s"
				  , (booking.attractionId, booking.date, booking.time, booking.price, now_utc(), member.member_id))
		else: 
			cursor.execute("INSERT INTO tp_booking(member_id, attractionId, tourDate, dateTime, price, created_at) VALUES(%s, %s, %s, %s, %s, %s)"
				  , (member.member_id, booking.attractionId, booking.date, booking.time, booking.price, now_utc()))
			
		db_connect.commit()
		cursor.close()	
			
		return JSONResponse(
			status_code = 200,
			content = {
				"ok": True
			} 
		)
	except:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)


@app.get("/api/booking")
async def get_booking(member: Member = Depends(get_current_member)):
	try:
		if member.member_id is None:
			return JSONResponse(
				status_code = 403,
				content = {
					"error": True,
  					"message": "未登入系統，無法查詢!"
				} 
			)
		else:
			cursor = db_connect.cursor()
			cursor.execute("SELECT attractionId, tourDate, dateTime, price FROM tp_booking WHERE member_id=%s", (member.member_id,))
			unpaid_booking = cursor.fetchone()
			if unpaid_booking is None:
				return JSONResponse(
					status_code = 200,
					content = {
						"data": None
					}
				)
			
			attraction_id, date, time, price = unpaid_booking
			attraction_id = unpaid_booking[0]
			cursor.execute("SELECT name, address, images FROM attractions WHERE id=%s", (attraction_id,))
			attraction_data = cursor.fetchone()
			cursor.close()
			name, address, images_str = attraction_data
			images_list = json.loads(images_str)  
			first_image_url = images_list[0]

			response_data = {
				"data": {
					"attraction": {
						"id": attraction_id,
						"name": name,
						"address": address,
						"image": first_image_url
					},
					"date": date.strftime('%Y-%m-%d'),
					"time": time,
					"price": price
				}
			}

			return JSONResponse(
				status_code = 200,
				content =response_data
			)
	except:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

@app.delete("/api/booking")
async def del_booking(member: Member = Depends(get_current_member)):
	try:
		if member.member_id is None:
			return JSONResponse(
				status_code = 403,
				content = {
					"error": True,
  					"message": "未登入系統，無效操作!"
				} 
			)
		else:
			cursor = db_connect.cursor()
			cursor.execute("DELETE FROM tp_booking WHERE member_id=%s", (member.member_id,))
			db_connect.commit()
			cursor.close()
			
			return JSONResponse(
				status_code = 200,
				content = {
					"ok": True
				} 
			)	
	except:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)
	
def generate_order_number():
	now = datetime.now().strftime("%Y%m%d%H%M")
	rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
	order_number = f"TP{now}-{rand}"
	return order_number

def now_utc():
	return datetime.now(timezone.utc)


@app.post("/api/orders")
async def create_order(data: OrderRequest, 
					   member: Member = Depends(get_current_member)):
	try:
		if member.member_id is None:
			return JSONResponse(
				status_code = 403,
				content = {
					"error": True,
  					"message": "未登入系統，無效操作!"
				} 
			)
		
		# 檢查欄位空值
		elif any(
			not value for value in [
				data.prime,
        		data.order.price,
				data.order.trip.attraction.id,
				data.order.trip.date,
				data.order.trip.time,
				data.order.contact.name,
				data.order.contact.email,
				data.order.contact.phone
			]
		):
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "訂單建立失敗，請確認所有欄位都有填寫!"
				}
    		)
		
		# 驗證時段價格
		elif data.order.trip.time == "morning" and data.order.price != 2000:
			return JSONResponse(
				status_code = 400,
				content = {
					"error": True,
  					"message": "訂單建立失敗，訂單金額不正確！"
				} 
			)
		elif data.order.trip.time == "afternoon" and data.order.price != 2500:
			return JSONResponse(
				status_code = 400,
				content = {
					"error": True,
  					"message": "訂單建立失敗，訂單金額不正確！"
				} 
			)
		
		else: 
			# 建立正式訂單
			order_number = generate_order_number()
			cursor = db_connect.cursor()
			cursor.execute("""
				  INSERT INTO tp_order(
				  member_id, order_number, order_price, paymentStatus,
				  attractionId, tourDate, dateTime,
				  contact_name, contact_email, contact_phone) 
				  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				  """, (
					member.member_id, order_number, data.order.price, "UNPAID",
		 			data.order.trip.attraction.id, data.order.trip.date, data.order.trip.time,
					data.order.contact.name, data.order.contact.email, data.order.contact.phone))

			# 刪除原預約項目 (目前限制每人最多存在一筆未結單預約)
			cursor.execute("DELETE FROM tp_booking WHERE member_id = %s", (member.member_id,))

			# 付款
			payment_result = call_tappay( prime = data.prime,
							   order_number = order_number,
							   amount = data.order.price,
							   name = data.order.contact.name,
							   phone = data.order.contact.phone,
							   email = data.order.contact.email
							)

			# 儲存付款紀錄
			order_number = payment_result.get("order_number", order_number)
			bank_transaction_id = payment_result.get("bank_transaction_id", None)
			rec_trade_id = payment_result.get("rec_trade_id", None)
			currency = payment_result.get("currency", None)
			amount = payment_result.get("amount", None)
			paid_at = payment_result.get("transaction_time_millis")
			formatted_paid_at = None

			if payment_result["status"] == 0:
				payment_status = "PAID"
			else:
				payment_status = "UNPAID"
			
			if paid_at:
				dt = datetime.fromtimestamp(paid_at / 1000)
				formatted_paid_at  = dt.strftime('%Y-%m-%d %H:%M:%S.%f')

			cursor.execute("""
				  INSERT INTO tp_payment(
				  order_number, status, msg, currency, amount, rec_trade_id, bank_transaction_id, paid_at
				  ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
				  """, (order_number , payment_result["status"], payment_result["msg"],
						currency, amount, rec_trade_id, bank_transaction_id, formatted_paid_at
						)
				)

			# 付款成功，更新訂單狀態
			msg_text = None
			if payment_result["status"] == 0:
				cursor.execute("UPDATE tp_order SET paymentStatus=%s, paid_at=%s WHERE order_number=%s", (payment_status, formatted_paid_at ,payment_result["order_number"]))
				msg_text = "付款成功"
			else:
				msg_text = "付款失敗： "+ payment_result["msg"]

			order_response = {
				"number": order_number,
				"payment": {
					"status": payment_result["status"],
					"message": msg_text 
				}
			}
			
			db_connect.commit()
			cursor.close()

			return JSONResponse(
				status_code = 200,
				content = {
					"data": order_response
				}
			)
				
	except Exception as e:
		return JSONResponse(
			status_code = 500,
			content = {
				"error": True,
				"message": "伺服器內部錯誤，請稍後再試。",
				"detail": str(e)
			}
		)

		

