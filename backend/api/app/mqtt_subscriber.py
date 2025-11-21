"""
MQTT Subscriber with Alert Engine Integration
"""

import paho.mqtt.client as mqtt
import json
import os
from app import db
from app.models import WeatherReading
from app.alerts import AlertEngine

class MQTTSubscriber:
    
    def __init__(self, app):
        self.app = app
        self.alert_engine = AlertEngine()
    
        # MQTT setup
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mqtt_username = os.getenv("MQTT_USERNAME")
        self.mqtt_password = os.getenv("MQTT_PASSWORD") 

        self.mqtt_connected = False 

        self.mqtt_client = mqtt.Client(client_id="weather_collection",
                                        callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.mqtt_connected = True
            print(f"✓ Connected to MQTT broker: {self.mqtt_broker}:{self.mqtt_port}")
            client.subscribe("weather/#")
            print("✓ Subscribed to weather topics...")
        else:
            print(f"✗ Failed to connect to MQTT broker, code {reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.mqtt_connected = False
        print("⚠ Disconnected from MQTT broker")

    def _on_message(self, client, userdata, message):
        """Callback when message received from MQTT broker"""
        try:
            payload = json.loads(message.payload.decode())
            city = payload.get('city')
            print(f"📩 Received message from {message.topic}: {city}")

            with self.app.app_context():
                # Zapisz odczyt do bazy
                reading = WeatherReading(
                    city=payload['city'],
                    temperature=payload['temperature'],
                    humidity=payload['humidity'],
                    pressure=payload['pressure'],
                    wind_speed=payload['wind_speed'],
                    weather=payload['weather'],
                    timestamp=payload['timestamp']
                )

                db.session.add(reading)
                db.session.commit()
                print(f"💾 Saved weather data for {city} to database")

                # ✨ NOWE: Sprawdź alerty dla tego odczytu
                alerts = self.alert_engine.check_reading(reading)
                if alerts:
                    print(f"Generated {len(alerts)} alert(s) for {city}")
                    for alert in alerts:
                        print(f"   - {alert.severity.upper()}: {alert.message}")
                else:
                    print(f"✓ No alerts triggered for {city}")

        except KeyError as e:
            print(f"✗ Missing required field in message: {e}")
        except Exception as e:
            print(f"✗ Error processing message: {e}")
            import traceback
            traceback.print_exc()

    def connect(self):
        """Connects to MQTT broker with retry logic"""
        import time
        
        max_retries = 10
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                if self.mqtt_username and self.mqtt_password:
                    self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)

                print(f"🔄 Attempt {attempt + 1}/{max_retries}: Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}...")
                self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
                self.mqtt_client.loop_start()
                print("✓ Successfully connected to MQTT broker!")
                return
                
            except ConnectionRefusedError as e:
                if attempt < max_retries - 1:
                    print(f"✗ Connection refused. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"✗ Failed to connect after {max_retries} attempts")
                    raise e

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        print("✓ Disconnected from MQTT broker")