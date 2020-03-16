from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from config import Config
from Helper import Log


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    Log.Initialize(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

#    from app.authentication import bp as auth_bp
#    app.register_blueprint(auth_bp, url_prefix='/authentication')

    from app.dispatcher_auth import bp as dispatcher_auth_bp
    app.register_blueprint(dispatcher_auth_bp, url_prefix='/auth')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.ns_management import bp as ns_bp
    app.register_blueprint(ns_bp, url_prefix='/NS')

    from app.experiment import bp as experiment_bp
    app.register_blueprint(experiment_bp, url_prefix='/experiment')

    from app.execution import bp as execution_bp
    app.register_blueprint(execution_bp, url_prefix='/execution')

    Log.I('5Genesis startup')
    return app


from app import models
