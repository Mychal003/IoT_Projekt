"""
MQTT Subscriber
"""

import paho.mqtt.client as mqtt
import json
import os
from app import db
from app.models import WeatherReading

class MQTTSubscriber:
    
    def __init__(self, app):
        self.app = app
    
    # MQTT setup
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mqtt_username = os.getenv("MQTT_USERNAME")
        self.mqtt_password = os.getenv("MQTT_PASSWORD") 

        self.mqtt_connected = False 

        self.mqtt_client = mqtt.Client(client_id="wheater_collection",
                                        callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.mqtt_connected = True
            print(f"Connected to MQTT broker: {self.mqtt_broker}:{self.mqtt_port}")
            client.subscribe("weather/#")
            print("Subscribe to weather topic...")
        else:
            print(f"Failed to connect to MQTT broker, code {reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.mqtt_connected = False
        print("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, message):
        """Callcback when message received from MQTT broker"""
        try:
            payload = json.loads(message.payload.decode())
            print(f"Received message from {message.topic}: {payload.get('city')}")


            with self.app.app_context():
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
                print(f"Save weather data for {payload['city']} to database")

        except Exception as e:
            print(f"Error processing message: {e}")


    def connect(self):
        if self.mqtt_username and self.mqtt_password:
            self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)

        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()

    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()