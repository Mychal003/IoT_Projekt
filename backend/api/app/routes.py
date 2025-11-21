"""
REST API ROUTES
Provides endpoints for weather data and alerts
"""

from flask import Blueprint, jsonify, request
from app import db
from app.models import WeatherReading
from sqlalchemy import desc

api_bp = Blueprint('api', __name__)


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
        # cities = db.session.query(WeatherReading.city).distinct().all()

        all_readings = WeatherReading.query.order_by(desc(WeatherReading.id)).all()
        cities_seen = set()
        latest_readings = []
        print("Fetching cities....")
        # for (city_name, ) in cities:
        #     print(f"{city_name}")

        # for city_row in cities:
        #     city_name = city_row[0] if city_row else None
        #     print(f"DEBUG: city_row={city_row}, city_name={city_name}")
        #     if not city_name:
        #         continue
        #     reading = WeatherReading.query.filter_by(city=city).order_by(
        #     desc(WeatherReading.id)).first()
        #     print(f"DEBUG: reading={reading}, type={type(reading)}")
        #     if reading:
        for reading in all_readings:
            if reading.city not in cities_seen:
                cities_seen.add(reading.city)
                latest_readings.append(reading.to_dict())

        return jsonify(latest_readings)


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'ok', 'service': 'weather-api'})




# @api_bp.route('/weather/history', methods=['GET'])
# def get_weather_history():
#     reading = WeatherReading.query





# @api_bp.route('/alerts', methods=['GET'])
# def get_alerty():
