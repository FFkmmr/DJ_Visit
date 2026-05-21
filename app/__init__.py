import os
from flask import Flask
from config import get_config


def create_app():
    """Flask app factory"""
    app_dir = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__,
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'),
                static_url_path='/static')

    # Load config
    config_class = get_config()
    app.config.from_object(config_class)

    # Register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
