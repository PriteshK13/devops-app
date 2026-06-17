FROM python:3.12-slim

WORKDIR /app

COPY frontend-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend-service/ /app/

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "app:app"]
