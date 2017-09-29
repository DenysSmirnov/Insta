from flask import Flask
from flask_pymongo import PyMongo
from flask_moment import Moment
from core.other import format_datetime
import flask_resize
from config import config

moment = Moment()
mongo = PyMongo()
resize = flask_resize.Resize()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    moment.init_app(app)
    mongo.init_app(app)
    resize.init_app(app)

    from . import main as main_blueprint
    app.register_blueprint(main_blueprint)
    app.jinja_env.filters['datetime'] = format_datetime

    return app