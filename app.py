from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import mysql.connector
import json
from collections import Counter
from typing import Annotated
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, InvalidTokenError
from enum import Enum
from datetime import date



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


def get_current_member_id(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
	try:
		decoded_token = jwt.decode(token.credentials, secret_key, algorithms=["HS256"])
		return decoded_token.get("member_id")
	except Exception:
		raise HTTPException(status_code=401, detail="無效的憑證")


@app.post("/api/booking")
async def create_or_update_booking(booking: BookingRequest,
								   member_id: int = Depends(get_current_member_id)):
	# 檢查登入狀態
	try:
		if member_id is None:
			return JSONResponse(
				status_code = 403,
				content = {
					"error": True,
  					"message": "未登入系統，無法進行預約!"
				} 
			)
		# 預約項目欄位是否完整
		# if not all([booking.attractionId, booking.date, booking.time, booking.price]):
		# 	return JSONResponse(
		# 		status_code = 400,
		# 		content = {
		# 			"error": True,
  		# 			"message": "預約失敗，請檢查全部選項是否已選取！"
		# 		} 
		# 	)

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
		cursor.execute("SELECT * FROM tp_order WHERE member_id = %s", (member_id,))
		existing = cursor.fetchone()

		# 檢查是否已有預約項目，若有，更新預約; 若無，新增當前預約
		if existing:
			cursor.execute("UPDATE tp_order SET attractionId =%s, tourDate =%s, dateTime =%s, price =%s, created_at=%s WHERE member_id =%s"
				  , (booking.attractionId, booking.date, booking.time, booking.price, datetime.now(),member_id))
		else: 
			cursor.execute("INSERT INTO tp_order(member_id, attractionId, tourDate, dateTime, price, created_at) VALUES(%s, %s, %s, %s, %s, %s)"
				  , (member_id, booking.attractionId, booking.date, booking.time, booking.price, datetime.now()))
			
		db_connect.commit()
		cursor.close()
		db_connect.close()		
			
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

