FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sber_cert.pem /usr/local/share/ca-certificates/sber_cert.crt
RUN chmod 644 /usr/local/share/ca-certificates/sber_cert.crt && \
    update-ca-certificates



# Копируем код
COPY . .
ENV PYTHONPATH=/app

# Запускаем сервер
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]