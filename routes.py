"""
Flask routes for the weather forecasting application
"""
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
import logging
import requests

from models import WeatherData, Prediction, ModelPerformance

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)


@main_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return render_template('dashboard.html')


@main_bp.route('/predict')
def predict_page():
    """Prediction interface page"""
    return render_template('predict.html')


# API Routes

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Generate weather predictions with OpenWeatherMap 5-day forecast
    Expected JSON: {
        'latitude': float,
        'longitude': float,
        'days': int (fixed at 5)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Missing required fields: latitude, longitude'}), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        days = 5  # Fixed to 5 days for OpenWeatherMap forecast
        
        # Validate ranges
        if not (-90 <= latitude <= 90):
            return jsonify({'error': 'Invalid latitude. Must be between -90 and 90'}), 400
        if not (-180 <= longitude <= 180):
            return jsonify({'error': 'Invalid longitude. Must be between -180 and 180'}), 400
        
        # Get location name (optional)
        location_name = data.get('location_name', f'Lat: {latitude}, Lon: {longitude}')
        
        # Get OpenWeatherMap forecast
        from config import Config
        api_key = Config.OPENWEATHER_API_KEY
        
        if not api_key:
            return jsonify({'error': 'OpenWeatherMap API key not configured'}), 500
        
        # Fetch 5-day forecast from OpenWeatherMap
        base_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code != 200:
            error_msg = response.json().get("message", "Could not retrieve forecast data")
            return jsonify({'error': f'Weather API error: {error_msg}'}), 500
        
        forecast_data = response.json()
        city = forecast_data.get("city", {})
        forecasts = forecast_data.get("list", [])
        
        # Process forecasts - group by day and take midday forecast (12:00) or closest
        daily_forecasts = {}
        for forecast in forecasts:
            dt = datetime.fromtimestamp(forecast["dt"])
            date_key = dt.strftime('%Y-%m-%d')
            
            # Prefer forecasts around noon (12:00)
            if date_key not in daily_forecasts or dt.hour == 12:
                daily_forecasts[date_key] = {
                    'dt': forecast['dt'],
                    'timestamp': dt,
                    'forecast': forecast
                }
        
        # Sort by date and take first 5 days
        sorted_forecasts = sorted(daily_forecasts.items(), key=lambda x: x[1]['timestamp'])[:5]
        
        # Format predictions
        predictions = []
        for idx, (date_key, data) in enumerate(sorted_forecasts):
            forecast = data['forecast']
            main = forecast['main']
            wind = forecast['wind']
            clouds = forecast['clouds']
            weather = forecast['weather'][0]
            
            predictions.append({
                'day_offset': idx,
                'date': data['timestamp'].strftime('%A, %b %d'),
                'full_datetime': data['timestamp'].strftime('%A, %b %d %H:%M'),
                'temperature': round(main['temp'], 1),
                'feels_like': round(main['feels_like'], 1),
                'temp_min': round(main['temp_min'], 1),
                'temp_max': round(main['temp_max'], 1),
                'humidity': main['humidity'],
                'pressure': main['pressure'],
                'wind_speed': round(wind['speed'], 1),
                'wind_deg': wind['deg'],
                'cloudiness': clouds['all'],
                'visibility': forecast.get('visibility', 'N/A'),
                'weather_description': weather['description'].title(),
                'weather_icon': weather['icon'],
                'precipitation': forecast.get('rain', {}).get('3h', 0) + forecast.get('snow', {}).get('3h', 0)
            })
        
        logger.info(f'Generated forecast for {location_name}')
        
        return jsonify({
            'success': True,
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'name': city.get('name', location_name),
                'country': city.get('country', ''),
                'sunrise': datetime.fromtimestamp(city.get('sunrise', 0)).strftime('%H:%M:%S') if city.get('sunrise') else 'N/A',
                'sunset': datetime.fromtimestamp(city.get('sunset', 0)).strftime('%H:%M:%S') if city.get('sunset') else 'N/A',
            },
            'predictions': predictions,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except ValueError as e:
        logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Prediction error: {str(e)}')
        return jsonify({'error': 'Failed to generate predictions'}), 500


@api_bp.route('/weather/current', methods=['GET'])
def get_current_weather():
    """
    Get current weather data from OpenWeatherMap
    Query params: latitude, longitude
    """
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        
        from config import Config
        api_key = Config.OPENWEATHER_API_KEY
        
        if not api_key:
            return jsonify({'error': 'OpenWeatherMap API key not configured'}), 500
        
        # Fetch current weather from OpenWeatherMap
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            error_msg = response.json().get("message", "Could not retrieve weather data")
            return jsonify({'error': f'Weather API error: {error_msg}'}), 500
        
        weather_data = response.json()
        
        return jsonify({
            'success': True,
            'data': {
                'timestamp': datetime.utcnow().isoformat(),
                'latitude': latitude,
                'longitude': longitude,
                'location_name': weather_data.get('name', ''),
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure'],
                'wind_speed': weather_data['wind']['speed'],
                'weather_description': weather_data['weather'][0]['description'],
                'weather_icon': weather_data['weather'][0]['icon']
            }
        })
        
    except Exception as e:
        logger.error(f'Error fetching current weather: {str(e)}')
        return jsonify({'error': 'Failed to fetch weather data'}), 500


@api_bp.route('/weather/historical', methods=['GET'])
def get_historical_weather():
    """
    Get historical weather data
    Query params: latitude, longitude, start_date, end_date
    """
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Query database
        query = WeatherData.query.filter(
            WeatherData.latitude.between(latitude - 0.5, latitude + 0.5),
            WeatherData.longitude.between(longitude - 0.5, longitude + 0.5)
        )
        
        if start_date:
            query = query.filter(WeatherData.timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(WeatherData.timestamp <= datetime.fromisoformat(end_date))
        
        data = query.order_by(WeatherData.timestamp.desc()).limit(1000).all()
        
        return jsonify({
            'success': True,
            'count': len(data),
            'data': [d.to_dict() for d in data]
        })
        
    except Exception as e:
        logger.error(f'Error fetching historical data: {str(e)}')
        return jsonify({'error': 'Failed to fetch historical data'}), 500


@api_bp.route('/predictions/history', methods=['GET'])
def get_prediction_history():
    """
    Get prediction history
    Query params: latitude, longitude, limit
    """
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        limit = request.args.get('limit', 100, type=int)
        
        query = Prediction.query
        
        if latitude and longitude:
            query = query.filter(
                Prediction.latitude.between(latitude - 0.5, latitude + 0.5),
                Prediction.longitude.between(longitude - 0.5, longitude + 0.5)
            )
        
        predictions = query.order_by(Prediction.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': [p.to_dict() for p in predictions]
        })
        
    except Exception as e:
        logger.error(f'Error fetching prediction history: {str(e)}')
        return jsonify({'error': 'Failed to fetch predictions'}), 500


@api_bp.route('/models/performance', methods=['GET'])
def get_model_performance():
    """Get model performance metrics"""
    try:
        model_name = request.args.get('model_name')
        
        query = ModelPerformance.query
        if model_name:
            query = query.filter_by(model_name=model_name)
        
        metrics = query.order_by(ModelPerformance.timestamp.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'count': len(metrics),
            'metrics': [m.to_dict() for m in metrics]
        })
        
    except Exception as e:
        logger.error(f'Error fetching model performance: {str(e)}')
        return jsonify({'error': 'Failed to fetch model performance'}), 500


@api_bp.route('/train', methods=['POST'])
def train_model():
    """
    Trigger model training
    Expected JSON: {
        'model_type': str,
        'event_type': str (optional)
    }
    """
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'ensemble')
        event_type = data.get('event_type')
        
        # This would trigger async training in production
        # For now, return a placeholder response
        
        return jsonify({
            'success': True,
            'message': 'Training initiated',
            'model_type': model_type,
            'event_type': event_type,
            'status': 'queued'
        })
        
    except Exception as e:
        logger.error(f'Error initiating training: {str(e)}')
        return jsonify({'error': 'Failed to initiate training'}), 500
