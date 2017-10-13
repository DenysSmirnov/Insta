import os
from urllib.parse import quote_plus


class Config(object):
	CSRF_ENABLED = True
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'very secret key'
	MAX_CONTENT_LENGTH = 10 * 1024 * 1024
	UPLOAD_URL = 'https://s3.us-east-2.amazonaws.com/insta-s3-bucket/upload/'
	RESIZE_TARGET_DIRECTORY = 'upload'
	RESIZE_STORAGE_BACKEND = 's3'
	RESIZE_S3_BUCKET = 'insta-s3-bucket'

	@staticmethod
	def init_app(app):
		pass


class ProductionConfig(Config):
	DEBUG = False
	MONGO_URI = os.environ.get('MONGODB_URI')
	RESIZE_S3_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
	RESIZE_S3_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
	RESIZE_S3_REGION = 'us-east-2'

	@classmethod
	def init_app(cls, app):
		Config.init_app(app)


class HerokuConfig(ProductionConfig):
	MONGO_URI = os.environ.get('MONGODB_URI')

	@classmethod
	def init_app(cls, app):
		ProductionConfig.init_app(app)
		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
	MONGO_DBNAME = 'yyy'


config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'heroku': HerokuConfig,
	'default': DevelopmentConfig
}
