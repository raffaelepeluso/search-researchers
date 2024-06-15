FROM python:3.12-alpine

WORKDIR /app
COPY  . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m unittest test_researcher_client_search.py
RUN python -m unittest test_researcher_parser.py

CMD ["python","app.py"]