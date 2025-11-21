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
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'weather': self.weather,
            'timestamp': self.timestamp,
            'received_at': self.received_at.isoformat()
        }


class AlertRule(db.Model):
    """Reguły alertów definiowane przez użytkownika"""
    __tablename__ = 'alert_rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    condition_type = db.Column(db.String(50), nullable=False)  # 'temperature', 'humidity', etc.
    operator = db.Column(db.String(10), nullable=False)  # '>', '<', '>=', '<=', '=='
    threshold = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'condition_type': self.condition_type,
            'operator': self.operator,
            'threshold': self.threshold,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Alert(db.Model):
    """Wygenerowane alerty"""
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    message = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(20), default='warning')  # 'info', 'warning', 'critical'
    value = db.Column(db.Float, nullable=False)  # Wartość która wywołała alert
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    rule = db.relationship('AlertRule', backref='alerts')

    def to_dict(self):
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'city': self.city,
            'message': self.message,
            'severity': self.severity,
            'value': self.value,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }