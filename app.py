"""
Main Flask application entry point for AI-Driven Climate Forecasting
"""
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import logging
from config import config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Setup logging
    setup_logging(app)
    
    # Create necessary directories
    create_directories(app)
    
    # Register blueprints
    from routes import api_bp, main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if not os.path.exists(app.config['LOGS_PATH']):
        os.makedirs(app.config['LOGS_PATH'])
    
    log_file = os.path.join(app.config['LOGS_PATH'], 'app.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.logger.info('Application started')


def create_directories(app):
    """Create necessary directories if they don't exist"""
    directories = [
        app.config['MODEL_PATH'],
        app.config['DATA_PATH'],
        app.config['LOGS_PATH'],
        os.path.join(app.config['DATA_PATH'], 'raw'),
        os.path.join(app.config['DATA_PATH'], 'processed')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            app.logger.info(f'Created directory: {directory}')


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
