"""
REST API ROUTES
Provides endpoints for weather data and alerts
"""

from flask import Blueprint, jsonify, request
from app import db
from app.models import WeatherReading, Alert, AlertRule
from app.alerts import AlertEngine
from sqlalchemy import desc

api_bp = Blueprint('api', __name__)
alert_engine = AlertEngine()


# ============ WEATHER ENDPOINTS ============

@api_bp.route('/weather/current', methods=['GET'])
def get_current_weather():
    
    city = request.args.get('city')
    
    if city:
        reading = WeatherReading.query.filter_by(city=city).order_by(
            desc(WeatherReading.id)
        ).first()

        if not reading:
            return jsonify({'error': f'No data found for city {city}'}), 404

        return jsonify(reading.to_dict())

    else:
        all_readings = WeatherReading.query.order_by(desc(WeatherReading.id)).all()
        cities_seen = set()
        latest_readings = []
        
        for reading in all_readings:
            if reading.city not in cities_seen:
                cities_seen.add(reading.city)
                latest_readings.append(reading.to_dict())

        return jsonify(latest_readings)


@api_bp.route('/weather/history', methods=['GET'])
def get_weather_history():
    """Pobiera historię odczytów dla danego miasta"""
    city = request.args.get('city')
    limit = request.args.get('limit', 100, type=int)
    
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
    
    readings = WeatherReading.query.filter_by(city=city)\
        .order_by(desc(WeatherReading.timestamp))\
        .limit(limit)\
        .all()
    
    return jsonify([r.to_dict() for r in readings])


# ============ ALERT ENDPOINTS ============

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Pobiera alerty"""
    city = request.args.get('city')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    
    query = Alert.query
    
    if city:
        query = query.filter_by(city=city)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'total': len(alerts),
        'unread_count': Alert.query.filter_by(is_read=False).count()
    })


@api_bp.route('/alerts/<int:alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    """Oznacza alert jako przeczytany"""
    success = alert_engine.mark_alert_as_read(alert_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Alert marked as read'})
    else:
        return jsonify({'error': 'Alert not found'}), 404


@api_bp.route('/alerts/mark-all-read', methods=['PUT'])
def mark_all_alerts_read():
    """Oznacza wszystkie alerty jako przeczytane"""
    city = request.args.get('city')
    
    query = Alert.query.filter_by(is_read=False)
    if city:
        query = query.filter_by(city=city)
    
    count = query.update({'is_read': True})
    db.session.commit()
    
    return jsonify({'success': True, 'marked_count': count})


# ============ ALERT RULES ENDPOINTS ============

@api_bp.route('/alert-rules', methods=['GET'])
def get_alert_rules():
    """Pobiera wszystkie reguły alertów"""
    city = request.args.get('city')
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    query = AlertRule.query
    
    if city:
        query = query.filter_by(city=city)
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    rules = query.order_by(desc(AlertRule.created_at)).all()
    
    return jsonify([rule.to_dict() for rule in rules])


@api_bp.route('/alert-rules', methods=['POST'])
def create_alert_rule():
    """Tworzy nową regułę alertu"""
    data = request.json
    
    # Walidacja
    required_fields = ['name', 'city', 'condition_type', 'operator', 'threshold']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Sprawdź poprawność operatora
    valid_operators = ['>', '<', '>=', '<=', '==']
    if data['operator'] not in valid_operators:
        return jsonify({'error': f'Invalid operator. Must be one of: {valid_operators}'}), 400
    
    # Sprawdź poprawność typu warunku
    valid_conditions = ['temperature', 'humidity', 'pressure', 'wind_speed']
    if data['condition_type'] not in valid_conditions:
        return jsonify({'error': f'Invalid condition_type. Must be one of: {valid_conditions}'}), 400
    
    rule = AlertRule(
        name=data['name'],
        city=data['city'],
        condition_type=data['condition_type'],
        operator=data['operator'],
        threshold=float(data['threshold']),
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(rule)
        db.session.commit()
        return jsonify(rule.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/alert-rules/<int:rule_id>', methods=['PUT'])
def update_alert_rule(rule_id):
    """Aktualizuje regułę alertu"""
    rule = AlertRule.query.get(rule_id)
    
    if not rule:
        return jsonify({'error': 'Rule not found'}), 404
    
    data = request.json
    
    # Aktualizuj pola jeśli są podane
    if 'name' in data:
        rule.name = data['name']
    if 'threshold' in data:
        rule.threshold = float(data['threshold'])
    if 'is_active' in data:
        rule.is_active = data['is_active']
    if 'operator' in data:
        valid_operators = ['>', '<', '>=', '<=', '==']
        if data['operator'] not in valid_operators:
            return jsonify({'error': f'Invalid operator'}), 400
        rule.operator = data['operator']
    
    try:
        db.session.commit()
        return jsonify(rule.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/alert-rules/<int:rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id):
    """Usuwa regułę alertu"""
    rule = AlertRule.query.get(rule_id)
    
    if not rule:
        return jsonify({'error': 'Rule not found'}), 404
    
    try:
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Rule deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/alert-rules/<int:rule_id>/toggle', methods=['PUT'])
def toggle_alert_rule(rule_id):
    """Włącza/wyłącza regułę alertu"""
    rule = AlertRule.query.get(rule_id)
    
    if not rule:
        return jsonify({'error': 'Rule not found'}), 404
    
    rule.is_active = not rule.is_active
    db.session.commit()
    
    return jsonify(rule.to_dict())


# ============ UTILITY ENDPOINTS ============

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'weather-api'})


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Pobiera statystyki systemu"""
    total_readings = WeatherReading.query.count()
    total_alerts = Alert.query.count()
    unread_alerts = Alert.query.filter_by(is_read=False).count()
    active_rules = AlertRule.query.filter_by(is_active=True).count()
    cities = db.session.query(WeatherReading.city).distinct().count()
    
    return jsonify({
        'total_readings': total_readings,
        'total_alerts': total_alerts,
        'unread_alerts': unread_alerts,
        'active_rules': active_rules,
        'cities_monitored': cities
    })