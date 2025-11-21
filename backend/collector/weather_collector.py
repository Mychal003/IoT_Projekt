"""
Wheater Data Collector
Collects real wheater data from OpenWheater API
and publishes to MQTT broker
"""
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import requests
import json
import os
import time

load_dotenv()


class WeatherCollector:
    """Collects whater data and publishes to MQTT"""


    def __init__(self, use_mqtt=True):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY not set in .env file!")

        self.base_url  = "https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"
    
        # Cities to monitor
        self.cities = [
            {"name": "Warszawa", "lat": 52.15, "lon": 21},
            {"name": "Yakutsk", "lat": 62.03, "lon": 129.73}
]

        # MQTT setup
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mqtt_username = os.getenv("MQTT_USERNAME")
        self.mqtt_password = os.getenv("MQTT_PASSWORD")    

        self.use_mqtt = use_mqtt
        self.mqtt_connected = False  

        if self.use_mqtt:
            import uuid
            unique_client_id = f"wheater_collector_{uuid.uuid4().hex[:8]}"
            self.mqtt_client = mqtt.Client(client_id=unique_client_id,
                                        callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            print(f"Using MQTT client_id: {unique_client_id}")


    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.mqtt_connected = True
            print(f"Connected to MQTT broker: {self.mqtt_broker}:{self.mqtt_port}")
        else:
            print(f"Failed to connect to MQTT broker, code {reason_code}")



    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.mqtt_connected = False
        print("Disconnected from MQTT broker")
    

    def connect_mqtt(self, subscribe=False):
        """Connects to MQTT broker"""

        print(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}...")

        
        if self.mqtt_username and self.mqtt_password:
            self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)

        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()

        # Czekanie na polaczenie
        for _ in range(10):
            if self.mqtt_connected:
                if subscribe:
                    print("Subscribing to weather/# (receiving message)...")
                    self.mqtt_client.subscribe("weather/#")
                return True
            time.sleep(2)

        raise ConnectionError("Could not connect to MQTT broker.")

    def fetch_weather(self, city_name="Warszawa"):
        """Fetch weather data for the given city"""

        # Znalezienie pozadanego miasta 
        city = next((c for c in self.cities if c["name"] == city_name), None)
        if not city:
            raise ValueError(f"City '{city_name}' not found in the city list.")

        url = self.base_url.format(city_name=city_name, api_key=self.api_key)
        response = requests.get(url)
        print(f"Full URL: {url}")
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch weather data: {response.status_code}")

        data = response.json()

        # Informacje jakie chce pozyskac z pogody
        result = {
            "city": city_name,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "weather": data["weather"][0]["description"],
            "timestamp": data["dt"]
        }

        return result
    
    def publish_weather(self, city_name="Warszawa"):
        """Fetch and publish weather data to MQTT"""

        data = self.fetch_weather(city_name)
        topic = f"weather/{city_name.lower()}"
        payload = json.dumps(data, ensure_ascii=False)

        if self.mqtt_connected:
            self.mqtt_client.publish(topic, payload)
            print(f"Published weather data for {city_name} to topic: {topic}")
        else:
            print("Cannot publish — MQTT not connected")




if __name__ == "__main__":
    collector = WeatherCollector()
    print(f"API KEY loaded: {collector.api_key[:8]}...")
    collector.connect_mqtt()
    weather_data = collector.fetch_weather("Warszawa")
    try:
        while True:
            collector.publish_weather("Warszawa")
            collector.publish_weather("Yakutsk")
            time.sleep(10)
            print(json.dumps(weather_data, indent=4, ensure_ascii=False))
    except KeyboardInterrupt:
        collector.mqtt_client.loop_stop()
        collector.mqtt_client.disconnect()
    