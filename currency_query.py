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

load_dotenv()

DING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=" + os.getenv("ACCESS_TOKEN")
DING_SECRET = os.getenv("SECRET")


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(sys.path[0] + "/currency_query.log", encoding='utf-8')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def send_notification(msg):
    timestamp = int(round(time.time()*1000))
    data_enc = f"{timestamp}\n{DING_SECRET}".encode('utf-8')
    secret_enc = DING_SECRET.encode('utf-8')
    hmac_code = hmac.new(secret_enc, data_enc, digestmod=hashlib.sha256).digest()
    sign = quote_plus(base64.b64encode(hmac_code))
    url = f"{DING_WEBHOOK}&timestamp={timestamp}&sign={sign}"
    params = {'msgtype': 'text', 'text': {'content': msg}}
    try:
        r = requests.post(url, json=params)
        res = r.json()
        if res['errcode'] != 0:
            raise Exception(json.dumps(res))
        logger.info("通知成功")
    except Exception as e:
        logger.error(f"通知出错: {e}")


def main():
    logger.info('begin query')
    cur.execute("select `rate` from rate_log order by `date` desc limit 1")
    last_rate = cur.fetchone()[0]
    r = requests.get('https://api.apilayer.com/currency_data/live?base=USD&symbols=CNY', headers={'apikey': os.getenv("API_KEY")})
    data = r.json()
    if data['success']:
        current_rate = data['quotes']['USDCNY']
        cur.execute("replace into rate_log (`date`, `rate`) VALUES (?, ?)", (datetime.now().strftime('%Y-%m-%d'), current_rate))
        con.commit()
        if current_rate > last_rate:
            send_notification(f"[汇率监控] 🟥 上涨：{last_rate} -> {current_rate}")
        elif current_rate < last_rate:
            send_notification(f"[汇率监控] 🟩 下跌：{last_rate} -> {current_rate}")
    else:
        raise Exception(r.text)


if __name__ == '__main__':
    logger = get_logger()
    con = sqlite3.connect(sys.path[0] + '/currency_data.db')
    cur = con.cursor()
    try:
        main()
    except Exception as err:
        logger.error(f"query error: {err}")
        send_notification("查询汇率出错")
