import os
import cloudinary
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary from env var CLOUDINARY_URL
cloudinary.config(secure=True)

CLOUDINARY_VIDEOS = {
    'main_backgr': 'https://res.cloudinary.com/dox1auiyy/video/upload/dj_visit/main_backgr.mp4',
    'actor_backgr': 'https://res.cloudinary.com/dox1auiyy/video/upload/dj_visit/actor_backgr.mp4',
}


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


def get_config():
    """Get config based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig
