"""
Alert Engine
Sprawdza warunki pogodowe i generuje alerty
    względem zdefiniowanych reguł

"""

from app import db
from app.models import Alert, AlertRule, WeatherReading
from datetime import datetime, timedelta


class AlertEngine:
    """Silnik alertów - sprawdza reguły i generuje alerty"""
    
    def __init__(self):
        self.operators = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '==': lambda a, b: a == b
        }
    
    def check_reading(self, reading: WeatherReading):
        """
        Sprawdza odczyt pogodowy względem wszystkich aktywnych reguł
        i generuje alerty jeśli warunki są spełnione
        """
        rules = AlertRule.query.filter_by(
            city=reading.city,
            is_active=True
        ).all()
        
        generated_alerts = []
        # Sprawdź każdą regułę pod kątem odczytu pogodowego
        for rule in rules:
            if self._should_trigger_alert(reading, rule):
                alert = self._create_alert(reading, rule)
                if alert:
                    generated_alerts.append(alert) # Dodaj wygenerowany alert do listy
        
        return generated_alerts
    
    def _should_trigger_alert(self, reading: WeatherReading, rule: AlertRule) -> bool:
        """Sprawdza czy reguła powinna wywołać alert"""
        
        # Pobierz wartość z odczytu
        value = self._get_value_from_reading(reading, rule.condition_type)
        if value is None:
            return False
        
        # Konwertuj temperaturę z Kelvinów
        if rule.condition_type == 'temperature':
            value = value - 273.15
        
        # (żeby nie spamować alertami)
        recent_cutoff = datetime.utcnow() - timedelta(minutes=30)
        recent_alert = Alert.query.filter(
            Alert.rule_id == rule.id,
            Alert.created_at >= recent_cutoff
        ).first()
        
        if recent_alert:
            return False
        
        # Sprawdź warunek
        operator_func = self.operators.get(rule.operator)
        if not operator_func:
            return False
        
        return operator_func(value, rule.threshold)
    
    def _get_value_from_reading(self, reading: WeatherReading, condition_type: str):
        """Pobiera odpowiednią wartość z odczytu pogodowego"""
        value_map = {
            'temperature': reading.temperature,
            'humidity': reading.humidity,
            'pressure': reading.pressure,
            'wind_speed': reading.wind_speed
        }
        return value_map.get(condition_type)
    
    def _create_alert(self, reading: WeatherReading, rule: AlertRule) -> Alert:
        """Tworzy nowy alert"""
        
        value = self._get_value_from_reading(reading, rule.condition_type)
        if rule.condition_type == 'temperature':
            value = value - 273.15
        
        # Generuj wiadomość
        message = self._generate_message(rule, value, reading.city)
        
        # Określ poziom ważności
        severity = self._determine_severity(rule, value)
        
        alert = Alert(
            rule_id=rule.id,
            city=reading.city,
            message=message,
            severity=severity,
            value=value,
            is_read=False
        )
        
        try:
            db.session.add(alert)
            db.session.commit()
            print(f"✓ Alert wygenerowany: {message}")
            return alert
        except Exception as e:
            print(f"✗ Błąd podczas tworzenia alertu: {e}")
            db.session.rollback()
            return None
    
    def _generate_message(self, rule: AlertRule, value: float, city: str) -> str:
        """Generuje czytelną wiadomość alertu"""
        
        unit_map = {
            'temperature': '°C',
            'humidity': '%',
            'pressure': 'hPa',
            'wind_speed': 'm/s'
        }
        
        condition_names = {
            'temperature': 'Temperatura',
            'humidity': 'Wilgotność',
            'pressure': 'Ciśnienie',
            'wind_speed': 'Prędkość wiatru'
        }
        
        unit = unit_map.get(rule.condition_type, '')
        condition_name = condition_names.get(rule.condition_type, rule.condition_type)
        
        return (f"{rule.name}: {condition_name} w {city} wynosi {value:.1f}{unit}, "
                f"co przekracza próg {rule.threshold}{unit}")
    
    def _determine_severity(self, rule: AlertRule, value: float) -> str:
        """Określa poziom ważności alertu"""
        
        
        if rule.condition_type == 'temperature':
            if value > 35 or value < -20:
                return 'critical'
            elif value > 30 or value < -10:
                return 'warning'
            else:
                return 'info'
        
        elif rule.condition_type == 'humidity':
            if value < 20 or value > 90:
                return 'critical'
            elif value < 30 or value > 80:
                return 'warning'
            else:
                return 'info'
        
        elif rule.condition_type == 'wind_speed':
            if value > 20:
                return 'critical'
            elif value > 15:
                return 'warning'
            else:
                return 'info'
        
        return 'info'
    
    def get_unread_alerts(self, city: str = None, limit: int = 50):
        """Pobiera nieprzeczytane alerty"""
        query = Alert.query.filter_by(is_read=False)
        
        if city:
            query = query.filter_by(city=city)
        
        return query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    def mark_alert_as_read(self, alert_id: int) -> bool:
        """Oznacza alert jako przeczytany"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_read = True
            db.session.commit()
            return True
        return False


#domyslne reguły
DEFAULT_ALERT_RULES = [
    {
        'name': 'Ekstremalna temperatura - gorąco',
        'condition_type': 'temperature',
        'operator': '>',
        'threshold': 30.0,
    },
    {
        'name': 'Ekstremalna temperatura - zimno',
        'condition_type': 'temperature',
        'operator': '<',
        'threshold': -10.0,
    },
    {
        'name': 'Bardzo niska wilgotność',
        'condition_type': 'humidity',
        'operator': '<',
        'threshold': 30.0,
    },
    {
        'name': 'Bardzo wysoka wilgotność',
        'condition_type': 'humidity',
        'operator': '>',
        'threshold': 80.0,
    },
    {
        'name': 'Silny wiatr',
        'condition_type': 'wind_speed',
        'operator': '>',
        'threshold': 15.0,
    },
]