FROM python:3.12-alpine

WORKDIR /app
COPY  . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m unittest test.py

EXPOSE  3001

CMD ["python","app.py"]