FROM python:3.11-slim

WORKDIR /app

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj pliki aplikacji
COPY . .

# Zainstaluj zależności Python
RUN pip install --no-cache-dir \
    flask \
    flask-sqlalchemy \
    flask-cors \
    paho-mqtt \
    python-dotenv

# Otwórz port 5000
EXPOSE 5000

# Uruchom aplikację
CMD ["python", "run.py"]