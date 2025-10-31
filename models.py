"""
Database models for weather forecasting application
"""
from datetime import datetime
from app import db


class WeatherData(db.Model):
    """Store historical and real-time weather data"""
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(200))
    
    # Weather parameters
    temperature = db.Column(db.Float)  # Celsius
    humidity = db.Column(db.Float)  # Percentage
    pressure = db.Column(db.Float)  # hPa
    wind_speed = db.Column(db.Float)  # km/h
    wind_direction = db.Column(db.Float)  # degrees
    precipitation = db.Column(db.Float)  # mm
    cloud_cover = db.Column(db.Float)  # Percentage
    visibility = db.Column(db.Float)  # km
    
    # Data source
    source = db.Column(db.String(50))  # NOAA, OpenWeatherMap, ECMWF
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'precipitation': self.precipitation,
            'cloud_cover': self.cloud_cover,
            'visibility': self.visibility,
            'source': self.source
        }


class Prediction(db.Model):
    """Store model predictions"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    prediction_date = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(200))
    
    # Event predictions
    event_type = db.Column(db.String(50))  # heatwave, storm, flood
    probability = db.Column(db.Float)  # 0-1
    confidence = db.Column(db.Float)  # 0-1
    
    # Predicted weather parameters
    predicted_temperature = db.Column(db.Float)
    predicted_precipitation = db.Column(db.Float)
    predicted_wind_speed = db.Column(db.Float)
    
    # Model information
    model_name = db.Column(db.String(100))
    model_version = db.Column(db.String(50))
    
    # Additional metadata (renamed to avoid SQLAlchemy conflict)
    additional_info = db.Column(db.Text)  # JSON string for additional info
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'prediction_date': self.prediction_date.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'event_type': self.event_type,
            'probability': self.probability,
            'confidence': self.confidence,
            'predicted_temperature': self.predicted_temperature,
            'predicted_precipitation': self.predicted_precipitation,
            'predicted_wind_speed': self.predicted_wind_speed,
            'model_name': self.model_name,
            'model_version': self.model_version
        }


class ModelPerformance(db.Model):
    """Track model performance metrics"""
    __tablename__ = 'model_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(50))
    
    # Performance metrics
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    rmse = db.Column(db.Float)
    mae = db.Column(db.Float)
    
    # Event-specific metrics
    event_type = db.Column(db.String(50))
    
    # Validation info
    validation_samples = db.Column(db.Integer)
    validation_period_start = db.Column(db.DateTime)
    validation_period_end = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'model_name': self.model_name,
            'model_version': self.model_version,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'rmse': self.rmse,
            'mae': self.mae,
            'event_type': self.event_type,
            'validation_samples': self.validation_samples
        }
