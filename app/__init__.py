from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()

login_manager = LoginManager()
login_manager.session_protection = 'strong'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
