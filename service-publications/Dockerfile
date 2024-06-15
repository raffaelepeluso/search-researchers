FROM python:3.10-alpine

WORKDIR /app

COPY app.py test.py requirements.txt db_mappers.py /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m unittest test.py

EXPOSE 3002

CMD ["python","app.py"]