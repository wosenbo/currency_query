import requests
import sqlite3
from datetime import datetime
import base64
import hmac
import hashlib
import time
from urllib.parse import urljoin, quote_plus
import json
import logging
import sys
import os
from dotenv import load_dotenv
from dingding import DingDing


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(sys.path[0] + '/currency_query.log', encoding='utf-8')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    conn = sqlite3.connect(sys.path[0] + "/currency_data.db")
    cursor = conn.cursor()
    try:
        rate_old = cursor.execute(
            "select rate from rate_log order by `date` desc limit 1"
        ).fetchone()[0]
        result = requests.get("https://m.cmbchina.com/api/rate/getfxrate").json()
        if result["status"] != 0:
            raise Exception(f"汇率接口异常: {result['status']}")
        for row in result["data"]:
            if row["ZCcyNbr"] == "美元":
                rate = round(float(row["ZRthBid"]) / 100, 4)
                logger.info(f"现汇(美元)买入价: {rate}")
                cursor.execute(
                    "replace into rate_log (`date`, rate) values (?, ?)",
                    (datetime.now().strftime("%Y-%m-%d"), rate),
                )
                conn.commit()
                if rate > rate_old:
                    diff_value = round(rate - rate_old, 4)
                    robot.send_markdown("汇率上涨", f"### 汇率上涨\n> 当前汇率: {rate} (+{diff_value})")
                elif rate < rate_old:
                    diff_value = round(rate_old - rate, 4)
                    robot.send_markdown("汇率下跌", f"### 汇率下跌\n> 当前汇率: {rate} (-{diff_value})")
                break
    except Exception as e:
        logger.error(f"查询失败: {e}")


logger = get_logger()

if __name__ == "__main__":
    load_dotenv()
    robot = DingDing(os.getenv("ACCESS_TOKEN"))
    robot.set_secret(os.getenv("SECRET"))
    main()
