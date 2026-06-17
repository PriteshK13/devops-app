FROM python:3.12-slim

WORKDIR /app

COPY chatbot-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chatbot-service/ /app/

EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
