import logging
import asyncio
from typing import AsyncGenerator, Optional

import mysql.connector
from mysql.connector import pooling
from fastapi import HTTPException

logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("myapp.log", encoding="utf-8"),
    ]
)

logger = logging.getLogger(__name__)


DB_CONFIG = dict(
    user="root",
    password="Ling0424J####",
    host="localhost",
    database="website",
    autocommit=False,      
    connection_timeout=5,  # socket 逾時（秒）
)

POOL_SIZE = 10

# ---------- 1) 建立全域連線池 ----------
try:
    db_pool: pooling.MySQLConnectionPool = pooling.MySQLConnectionPool(
        pool_name="fastapi_pool",
        pool_size=POOL_SIZE,
        pool_reset_session=True,      
        **DB_CONFIG,
    )
    logger.info("MySQL 連線池建立完成 (size=%s)", POOL_SIZE)
except mysql.connector.Error as exc:
    logger.exception("MySQL 連線池建立失敗：%s", exc)
    raise

# ---------- 2) 取得連線（同步函式，給 asyncio 執行緒池用） ----------
def _acquire_conn() -> mysql.connector.MySQLConnection:
    """從池子拿一條連線，確保可用；失敗就拋例外。"""
    conn = db_pool.get_connection()
    logger.debug("🟢 連線借出 %s", id(conn))
    try:
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=2)
        return conn
    except mysql.connector.Error:
        conn.close()
        raise

# ---------- 3) FastAPI Dependency ----------
async def get_db() -> AsyncGenerator[mysql.connector.MySQLConnection, None]:
    """
    在背景執行緒取出連線並包裝 timeout。
    """
    conn: Optional[mysql.connector.MySQLConnection] = None

    try:
        conn = await asyncio.wait_for(
            asyncio.to_thread(_acquire_conn), timeout=5
        )
        yield conn

        if not DB_CONFIG.get("autocommit", True):
            conn.commit()

    except asyncio.TimeoutError:
        logger.warning("取得資料庫連線逾時")
        raise HTTPException(
            status_code=503, detail="資料庫連線忙碌中，請稍候再試"
        )

    except mysql.connector.Error as exc:
        logger.exception("資料庫錯誤：%s", exc)
        # 失敗就 rollback，並回 503
        if conn and conn.is_connected() and not conn.autocommit:
            conn.rollback()
        raise HTTPException(
            status_code=503, detail="Database unavailable"
        )

    finally:
        if conn and conn.is_connected():
            logger.debug("🔵 連線釋放 %s", id(conn))
            conn.close()