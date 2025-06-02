FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

ENV PYTHONPATH=/app
ENV RABBITMQ_URL=${RABBITMQ_URL}

# Comando para correr el worker
CMD ["python", "src/main.py"]
