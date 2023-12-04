import requests
import sqlite3
from datetime import datetime
import logging
import sys
import os
from dotenv import load_dotenv
from dingding import DingDing
from bs4 import BeautifulSoup

load_dotenv()


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(sys.path[0] + "/currency_query.log", encoding='utf-8')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_exchange_rate_BOC():
    try:
        r = requests.post(
            'https://srh.bankofchina.com/search/whpj/search_cn.jsp',
            data={'pjname': '美元'}
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        return round(float(soup.select('table')[1].select('tr')[1].select('td')[1].text) / 100, 4)
    except Exception as e:
        logger.error(f"获取汇率失败: {e}")


def main():
    logger.info('begin query')
    con = sqlite3.connect(sys.path[0] + '/currency_data.db')
    cur = con.cursor()
    cur.execute("select `rate` from rate_log order by `date` desc limit 1")
    rate_old = cur.fetchone()[0]
    rate = get_exchange_rate_BOC()
    if rate:
        logger.info(f"现汇(美元)买入价: {rate}")
        cur.execute(
            "replace into rate_log (`date`, `rate`) VALUES (?, ?)",
            (datetime.now().strftime('%Y-%m-%d'), rate),
        )
        con.commit()
        if rate > rate_old:
            diff_value = round(rate - rate_old, 4)
            robot.send_markdown("汇率上涨", f"### 汇率上涨\n> 当前汇率: {rate} (+{diff_value})")
        elif rate < rate_old:
            diff_value = round(rate_old - rate, 4)
            robot.send_markdown("汇率下跌", f"### 汇率下跌\n> 当前汇率: {rate} (-{diff_value})")


if __name__ == '__main__':
    logger = get_logger()
    robot = DingDing(os.getenv("ACCESS_TOKEN"))
    robot.set_secret(os.getenv("SECRET"))
    try:
        main()
    except Exception as err:
        logger.error(f"query error: {err}")
        robot.send_text(f"查询汇率出错: {err}")
