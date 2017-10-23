import os
# from urllib.parse import quote_plus
# basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
	# Включение защиты против "Cross-site Request Forgery (CSRF)"
	CSRF_ENABLED = True
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'very secret key'
	MAX_CONTENT_LENGTH = 10 * 1024 * 1024
	NUM_PER_PAGE_MAIN = 10
	NUM_PER_PAGE = 12

	@staticmethod
	def init_app(app):
		pass


class ProductionConfig(Config):
	DEBUG = False
	MONGO_URI = os.environ.get('MONGODB_URI')
	RESIZE_S3_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
	RESIZE_S3_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
	RESIZE_S3_REGION = 'us-east-2'
	RESIZE_TARGET_DIRECTORY = 'upload'
	RESIZE_STORAGE_BACKEND = 's3'
	RESIZE_S3_BUCKET = 'insta-s3-bucket'
	UPLOAD_URL = 'https://s3.us-east-2.amazonaws.com/insta-s3-bucket/upload/'

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
	# DEVELOPMENT = True
	DEBUG = True
	MONGO_DBNAME = 'yyy'
	RESIZE_URL = ''
	RESIZE_ROOT = 'core/static/upload/'
	UPLOAD_URL = '/static/upload/resized-images/'
	NUM_PER_PAGE_MAIN = 5


config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'heroku': HerokuConfig,
	'default': DevelopmentConfig
}
