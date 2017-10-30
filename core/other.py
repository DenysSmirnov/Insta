from flask import redirect, url_for, session, current_app as app
from functools import wraps
from werkzeug import secure_filename
import os.path
import re
import random
import boto3

def allowed_img(filename):
	ALLOWED_EXTENSIONS = set(['png', 'jpg']) # , 'jpeg', 'tiff', 'bmp'
	return '.' in filename and \
		filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_img(img, res='600', quality=95):
	from .base import resize
	path = secure_filename(img.filename.lower())
	if len(list(path)) <= 5:
		path = ''.join([random.choice(list('1234567890abc')) \
			for x in range(20)]) + '.' + path
	if app.config.get('RESIZE_ROOT'):
		full_path = os.path.join(app.config['RESIZE_ROOT'], path)
		img.save(full_path)
	else:
		img.save(path)
		s3 = boto3.resource(
		's3',
		aws_access_key_id=app.config.get('RESIZE_S3_ACCESS_KEY'),
		aws_secret_access_key=app.config.get('RESIZE_S3_SECRET_KEY')
		)
		s3.meta.client.upload_file(
		path, app.config['RESIZE_S3_BUCKET'], path)
	resized_url = resize(path, res, quality=quality).rsplit('/', 1)[1]
	# print('path: ', path)
	# print('full_path: ', full_path)
	# print('resized_url: ', resized_url)
	return resized_url

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session.get('username') is None:
			return redirect(url_for('main.login'))
		return f(*args, **kwargs)
	return decorated_function

def login_is_valid(login):
	match = re.match(r'^\b[a-z_][a-z0-9_.]{3,20}$', login)
	if match:
		return True

def text_is_valid(text):
	match = re.match(r'([#.^|$]{1,})|(\w+\|)|(\\\w)', text)
	if match:
		return False
	return True

def format_datetime(value, format='medium'):
	if format == 'full':
		format="%Y-%m-%d %H:%M:%S"
	elif format == 'medium':
		format="%d %B %Y"
	return value.strftime(format)