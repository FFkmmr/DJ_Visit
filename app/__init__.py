import os
from flask import Flask
from config import get_config
from app.extensions import limiter, csrf


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

    # Allow large video uploads (up to 2 GB)
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

    # CSRF only on the login form; JSON API endpoints are session-protected
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    limiter.init_app(app)
    csrf.init_app(app)

    # Register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
