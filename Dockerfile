FROM python:3.8.16-alpine3.17

RUN apk add -U tzdata
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN apk del tzdata

ADD currency_query_CMB.py .
ADD currency_data.db .
ADD .env .

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
RUN pip install requests
RUN pip install dingding
RUN pip install python-dotenv

CMD ["python", "./currency_query_CMB.py"]
