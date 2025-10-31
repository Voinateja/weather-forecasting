"""
Configuration module for the AI-Driven Climate Forecasting Application
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///weather_forecast.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    
    # Paths
    MODEL_PATH = os.environ.get('MODEL_PATH') or './models/saved_models'
    DATA_PATH = os.environ.get('DATA_PATH') or './data'
    LOGS_PATH = os.environ.get('LOGS_PATH') or './logs'
    
    # Application Settings
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Prediction Settings
    FORECAST_DAYS = int(os.environ.get('FORECAST_DAYS', 7))
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.75))
    
    # Model Parameters
    LSTM_UNITS = 128
    LSTM_LAYERS = 2
    DROPOUT_RATE = 0.2
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 0.001
    
    # Weather Event Thresholds (based on WMO standards)
    HEATWAVE_THRESHOLD = 35  # Celsius
    STORM_WIND_THRESHOLD = 63  # km/h (17.5 m/s)
    FLOOD_PRECIPITATION_THRESHOLD = 50  # mm per day
    
    # Data Collection
    UPDATE_INTERVAL = 3600  # seconds (1 hour)
    HISTORICAL_YEARS = 5  # years of historical data


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_weather_forecast.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
