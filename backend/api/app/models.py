"""
Database Models
Stores weather data and alerts
"""

from app import db
from datetime import datetime


class WeatherReading(db.Model):
    __tablename__ = 'weather_readings'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    weather = db.Column(db.String(30))
    timestamp = db.Column(db.Integer, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)


    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'weather': self.weather,
            'timestamp': self.timestamp,
            'received_at': self.received_at.isoformat()
        }


