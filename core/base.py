from flask import Flask
from flask_pymongo import PyMongo
from flask_moment import Moment
from config import config
import flask_resize
import locale

moment = Moment()
mongo = PyMongo()
resize = flask_resize.Resize()
locale.setlocale(locale.LC_ALL, '')

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    moment.init_app(app)
    mongo.init_app(app)
    resize.init_app(app)

    from . import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app