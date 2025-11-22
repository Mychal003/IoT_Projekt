# System Monitoringu Pogody z Alertami

Aplikacja do monitorowania pogody w czasie rzeczywistym z systemem automatycznych alertów.

## Wymagania

- Docker Desktop (uruchomiony)
- Python 3.11+
- Node.js 18+
- Klucz API do OpenWeatherMap

## Szybki start

### 1. Uruchom kontenery Docker

```bash
docker-compose up -d
```

Poczekaj 15-20 sekund aż kontenery się uruchomią.

### 2. Włącz MQTT w RabbitMQ

```bash
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_mqtt
```

Poczekaj kolejne 5 sekund.

### 3. Zainicjalizuj alerty

```bash
cd backend/api
python init_alerts.py
cd ../..
```

### 4. Uruchom Weather Collector

W nowym terminalu:

```bash
cd backend/collector
python weather_collector.py
```

### 5. Uruchom Frontend

W kolejnym nowym terminalu:

```bash
cd frontend
npm install  # tylko przy pierwszym uruchomieniu
npm run dev
```

### 6. Otwórz aplikację

http://localhost:3000

## Sprawdzenie czy działa

```bash
# Sprawdź status API
curl http://localhost:5000/api/health

# Sprawdź czy są reguły alertów
curl http://localhost:5000/api/alert-rules

# Sprawdź dane pogodowe
curl http://localhost:5000/api/weather/current
```

## Częste problemy

### Problem: Błąd 404 na endpointach /api/alerts lub /api/alert-rules

**Przyczyna:** Nowe pliki nie zostały załadowane do kontenera Docker.

**Rozwiązanie:**

```bash
# 1. Zatrzymaj kontenery
docker-compose down

# 2. Przebuduj kontenery z nowymi plikami
docker-compose build --no-cache

# 3. Uruchom ponownie
docker-compose up -d

# 4. Poczekaj 15 sekund
# Windows PowerShell:
Start-Sleep -Seconds 15
# Linux/Mac:
sleep 15

# 5. Włącz MQTT
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_mqtt

# 6. Poczekaj 5 sekund i zainicjalizuj alerty
Start-Sleep -Seconds 5  # lub: sleep 5
cd backend/api
python init_alerts.py
```

### Problem: Flask nie łączy się z RabbitMQ

**Objawy:** W logach widzisz "Connection refused" w pętli.

**Rozwiązanie:**

RabbitMQ potrzebuje czasu na uruchomienie. Po `docker-compose up -d` zawsze poczekaj 15-20 sekund.

```bash
docker-compose up -d
Start-Sleep -Seconds 20  # lub: sleep 20
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_mqtt
Start-Sleep -Seconds 5   # lub: sleep 5
docker restart flask-api
```

### Problem: Brak alertów mimo ekstremalnych temperatur

**Przyczyna:** Reguły alertów nie zostały zainicjalizowane.

**Rozwiązanie:**

```bash
# Sprawdź czy są reguły w bazie
docker exec -it flask-api python -c "from app import create_app, db; from app.models import AlertRule; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Liczba regul: {AlertRule.query.count()}')"

# Jeśli wynik to 0, zainicjalizuj reguły
cd backend/api
python init_alerts.py
```

### Problem: "Failed to fetch" w przeglądarce

**Przyczyna:** Flask API nie działa lub nie zwraca prawidłowych endpointów.

**Rozwiązanie:**

```bash
# Sprawdź czy Flask działa
docker ps
# Powinieneś zobaczyć flask-api i rabbitmq

# Sprawdź logi
docker logs flask-api

# Jeśli widzisz same błędy Connection refused:
docker restart flask-api
Start-Sleep -Seconds 10
docker logs flask-api
```

## Struktura projektu

```
projekt/
├── backend/
│   ├── api/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── alerts.py       # Alert Engine
│   │   │   ├── models.py       # Modele bazy danych
│   │   │   ├── mqtt_subscriber.py
│   │   │   └── routes.py       # REST API
│   │   ├── init_alerts.py      # Skrypt inicjalizacji
│   │   └── run.py
│   └── collector/
│       └── weather_collector.py
├── frontend/
│   └── src/
│       ├── App.tsx
│       └── components/
│           ├── AlertPanel.tsx
│           └── AlertRuleManager.tsx
└── docker-compose.yml
```

## API Endpoints

### Pogoda
- `GET /api/weather/current` - Aktualna pogoda
- `GET /api/weather/history?city=Warszawa` - Historia odczytów

### Alerty
- `GET /api/alerts` - Lista alertów
- `GET /api/alerts?city=Warszawa` - Alerty dla miasta
- `GET /api/alerts?unread_only=true` - Tylko nieprzeczytane
- `PUT /api/alerts/{id}/read` - Oznacz jako przeczytane
- `PUT /api/alerts/mark-all-read` - Oznacz wszystkie

### Reguły alertów
- `GET /api/alert-rules` - Lista reguł
- `POST /api/alert-rules` - Utwórz regułę
- `PUT /api/alert-rules/{id}` - Aktualizuj regułę
- `DELETE /api/alert-rules/{id}` - Usuń regułę
- `PUT /api/alert-rules/{id}/toggle` - Włącz/wyłącz regułę

### Statystyki
- `GET /api/stats` - Statystyki systemu

## Domyślne reguły alertów

Po uruchomieniu `init_alerts.py` dla każdego miasta tworzone są:

1. Ekstremalna temperatura - gorąco (> 30°C)
2. Ekstremalna temperatura - zimno (< -10°C)
3. Bardzo niska wilgotność (< 30%)
4. Bardzo wysoka wilgotność (> 80%)
5. Silny wiatr (> 15 m/s)

## Zarządzanie kontenerami

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logi
docker logs flask-api -f
docker logs rabbitmq -f

# Restart pojedynczego kontenera
docker restart flask-api

# Wejście do kontenera
docker exec -it flask-api bash
```

## Dodawanie nowych miast

1. Edytuj `backend/collector/weather_collector.py`:

```python
self.cities = [
    "Warszawa", 
    "Yakutsk",
    "Nowe_Miasto"  # dodaj tutaj
]
```

2. Restart collectora

3. Zainicjalizuj reguły dla nowego miasta:

```bash
cd backend/api
python init_alerts.py
```

## Czyszczenie bazy danych

```bash
# UWAGA: To usuwa WSZYSTKIE dane

docker-compose down
docker volume rm $(docker volume ls -q | grep weather)
docker-compose up -d

# Poczekaj i zainicjalizuj od nowa
Start-Sleep -Seconds 20
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_mqtt
cd backend/api
python init_alerts.py
```

## Troubleshooting

### Sprawdź czy wszystko działa

```bash
# 1. Docker
docker ps
# Powinny być: flask-api, rabbitmq

# 2. Flask API
curl http://localhost:5000/api/health
# Powinno zwrócić: {"status":"ok","service":"weather-api"}

# 3. RabbitMQ Management UI
# Otwórz: http://localhost:15672
# Login: kalo, Hasło: kalo

# 4. Baza danych
docker exec -it flask-api python
```

W Pythonie:
```python
from app import create_app, db
from app.models import AlertRule, Alert, WeatherReading

app = create_app()
with app.app_context():
    print(f"Reguł: {AlertRule.query.count()}")
    print(f"Alertów: {Alert.query.count()}")
    print(f"Odczytów: {WeatherReading.query.count()}")
exit()
```

### Alerty nie są generowane

Sprawdź logi Flask - powinny być komunikaty o sprawdzaniu alertów:

```bash
docker logs flask-api -f
```

Szukaj linii:
```
Received message from weather/warszawa: Warszawa
Save weather data for Warszawa to database
Generated X alert(s) for Warszawa
```

Jeśli brakuje linii o alertach, Alert Engine nie działa. Przebuduj kontenery.

### Frontend nie działa

```bash
# Sprawdź czy Vite działa
cd frontend
npm run dev

# Sprawdź console w przeglądarce (F12)
# Szukaj błędów CORS lub 404
```

## Konfiguracja

### Backend (.env w backend/api)

```
FLASK_ENV=development
DATABASE_URL=sqlite:///weather.db
MQTT_BROKER=rabbitmq
MQTT_PORT=1883
MQTT_USERNAME=kalo
MQTT_PASSWORD=kalo
```

### Collector (.env w backend/collector)

```
OPENWEATHER_API_KEY=twoj_klucz_api
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=kalo
MQTT_PASSWORD=kalo
```