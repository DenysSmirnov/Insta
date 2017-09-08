import time
from datetime import *
from flask import (
	Flask, render_template, request, redirect,
	send_from_directory, url_for, session, flash, abort
)
from pymongo import MongoClient
from bson.objectid import ObjectId
# from bson.dbref import DBRef
from werkzeug import secure_filename
from functools import wraps
# from helpers import *
import re
# from jinja2 import Environment

app = Flask(__name__)
app.secret_key = 'ouFUu-erv/r?reRBGrn/Ur83-64+j!C4nN<#8)vjnss-btr-eDA6'

def get_image_collection():
    client = MongoClient()
    db = client.yyy
    col = db.images
    return col

def get_user_collection():
    client = MongoClient()
    db = client.yyy
    col = db.users
    return col

def save(image):
    col = get_image_collection()
    col.insert_one(image)

def save_avatar(username, avatar):
    col = get_user_collection()
    col.update_one({'name' : username},{'$set': {'avatar' : avatar}})
    col = get_image_collection()
    col.update_many({'author.name' : username},{'$set': {'author.avatar' : avatar}})

def add_comment(_id, comment):
    col = get_image_collection()
    col.update_one(
        {'_id' : ObjectId(_id)},{'$addToSet': {
        'comments' : {session['username']: comment}}}
    )

def del_comment(_id, comment):
    col = get_image_collection()
    col.update_one(
        {'_id' : ObjectId(_id)},{'$pull': {
        'comments' : {session['username']: comment}}}
    )

def add_like(_id):
    col = get_image_collection()
    data = col.find({'_id' : ObjectId(_id)})
    for item in data:
        if session['username'] in item['liked_users']:
            col.update_one(
                {'_id' : ObjectId(_id)},{'$pull': {
                'liked_users' : session['username']}}
            )
        else:
            col.update_one(
                {'_id' : ObjectId(_id)},{'$addToSet': {
                'liked_users' : session['username']}}
            )

def update_profile(fio, name, about, mail):
    col = get_user_collection()
    col.update_one({'name' : session['username']},{'$set':{
                'fio': fio,
                'name': name.lower(),
                'about': about,
                'mail': mail.lower()
                }
            })
    if name != session['username']:
        col.update_many({'following': session['username']}, {
            '$set': {'following.$' : name.lower()}
        })
        col.update_many({'followers': session['username']}, {
            '$set': {'followers.$' : name.lower()}
        })
        col = get_image_collection()
        col.update_many({'author.name': session['username']}, {
            '$set': {'author.name' : name.lower()}
        })
    # followers = get_following(name, 'followers')
    # followers  = list(followers)
    # print(followers)
    # col.update_one({'name': {'$in': followers}}, {'$set': { "following.$" : name }
    #   })

def follow(username):
    col = get_user_collection()
    data = col.find({'name' : session['username']})
    for item in data:
        if username in item['following']:
            col.update_one(
                {'name' : session['username']},{'$pull': {
                'following' : username}}
            )
            col.update_one(
                {'name' : username},{'$pull': {
                'followers' : session['username']}}
            )
        else:
            col.update_one(
                {'name' : session['username']},{'$addToSet': {
                'following' : username}}
            )
            col.update_one(
                {'name' : username},{'$addToSet': {
                'followers' : session['username']}}
            )

def allowed_img(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'tiff', 'bmp'])
    return '.' in filename and \
        filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_images(tag=None, _id=None, author=None, author_follow=None):
    col = get_image_collection()
    if tag:
        return col.find({'tags': tag})
    if _id:
        return col.find({'_id': ObjectId(_id)})
    if author:
        return col.find({'author.name': author}).sort([('_id', -1)])
    if author_follow:
        return col.find({'author.name': {'$in': author_follow}}).sort([('_id', -1)])
    return col.find().sort([('_id', -1)])

def get_users(username=None, names=None):
    col = get_user_collection()
    if username:
        return col.find({'name' : username}, {'password':0})
    if names:
        return col.find({'name': {'$in': names}}, {'name':1, 'avatar':1, '_id':0})

def get_following(username, s):
    '''
    s - string (followers or following) 
    '''
    col = get_user_collection()
    user = col.find({'name' : username}, {s:1, '_id':0})
    if not user.count():
        abort(404)
    else:
        for item in user:
            names = item[s]
        return col.find({'name': {'$in': names}}, {'password':0})

def format_datetime(value, format='medium'):
    if format == 'full':
        format="%Y-%m-%d %H:%M:%S"
    elif format == 'medium':
        format="%d %B %Y"
    elif format == 'delta':
    	format="%d"
    	delta = datetime.now() - value
    	# if delta > 60:
    	#n = datetime.now().strftime('%d')
    	#s = delta.strptime("%d days, %H:%M:%S.%f")
    	# print(delta)
    	#print(n)
    	return delta
    	# return value.strptime(str(delta.days), format)
    return value.strftime(format)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def login_is_valid(login):
	match = re.match(r'^\b[a-z_][a-z0-9_.]{3,20}$', login)
	if match:
		return True

def date(images):
	for img in images:
		# if img['created_time']:
		img_time = img.get('created_time')
		# time.strftime('%d %B %Y', time.localtime(img['created_time']))
		# delta = (datetime.now() - img_time).strftime('%d %m %Y')
	# print(img_time)
	# print(delta, 'назад')
	# time.strftime('%d %m %Y', delta)

		# db_time = time.strftime(r"%d.%m.%Y %H:%M:%S", img['created_time'])
	# 	# created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(img['created_time']))
	

@app.route('/register/', methods=['GET', 'POST'])
def register():
	name = None
	password = None
	if request.method == 'POST':
		col = get_user_collection()
		name = request.form.get('name')
		password = request.form.get('password')
		if login_is_valid(name):
			i = col.find({'name': name}).count()
			if i == 0:
				col.insert_one({
					'name': name,
					'password': password,
					'followers': [],
					'following': [],
					'avatar': 'no_avatar.png'
				})
				return redirect(url_for('login'))
			else:
				flash('Имя уже занято')
		else:
			flash('Недопутимое имя пользователя!')
	return render_template('user/register.html', name=name, password=password)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		col = get_user_collection()
		name = request.form.get('name')
		password = request.form.get('password')
		users = col.find({
			'name': name,
			'password': password
		})
		users = list(users)
		if len(users) == 0:
			flash('Пользователь с таким логином/паролем не найден')
		else:
			user = users[0]
			session['username'] = user['name']
			return redirect(url_for('home'))
	return render_template('user/login.html')

@app.route('/logout/')
def logout():
	del session['username']
	return redirect(url_for('home'))

@app.route('/accounts/edit/', methods=['GET', 'POST'])
@login_required
def edit_account():
	userdata = get_users(session['username'])
	if request.method == 'POST':
		fio = request.form.get('fio')
		name = request.form.get('name')
		about = request.form.get('about')
		mail = request.form.get('mail')
		update_profile(fio, name, about, mail)
		session['username'] = name.lower()
		return redirect(url_for('user', username=name))
	return render_template('forms/edit_account.html', userdata=userdata)

@app.route('/accounts/password/change/', methods=['GET', 'POST'])
@login_required
def change_password():
	if request.method == 'POST':
		OldPassword = request.form.get('cppOldPassword')
		NewPassword = request.form.get('cppNewPassword')
		ConfirmPassword = request.form.get('cppConfirmPassword')
		if OldPassword and NewPassword and ConfirmPassword:
			if NewPassword == ConfirmPassword:
				col = get_user_collection()
				userdata = col.find({
					'name' : session['username']}, {'password':1, '_id':0})
				for data in userdata:
					if OldPassword == data['password']:
						col.update_one({'name' : session['username']},{
							'$set': {'password' : NewPassword}})
						# flash('Пароль успешно изменен! Авторизуйтесь.')
						time.sleep(2)
					else:
						flash('Введен неверный пароль!')
						return redirect(url_for('change_password'))
			else:
				flash('Пароли не совпадают!')
				return redirect(url_for('change_password'))
		else:
			flash('Заполнены не все поля формы!')
			return redirect(url_for('change_password'))
		return redirect(url_for('login'))
	return render_template('forms/change_password.html')	

@app.route('/<username>/', methods=['POST', 'GET'])
@login_required
def user(username):
	images = get_images(author=username)
	userdata = get_users(username)
	if images.count() == 0 and userdata.count() == 0:
		abort(404)
	col = get_image_collection()
	user_image_count = col.find({'author.name': username}).count()
	
	if request.method == 'POST':
		if request.form.get('follow'):
			follow(username)
			return redirect(url_for('user', username=username))
		if request.form.get('avatar'):
			avatar = request.files['upload']
			if avatar and allowed_img(avatar.filename):
				avatar.save(
				'static/avatars/' + secure_filename(avatar.filename.lower())
				)
				save_avatar(username, avatar.filename)
	return render_template(
		'user.html', images=images, userdata=userdata, 
		user_image_count=user_image_count
	)

@app.route('/<username>/followers/', methods=['POST', 'GET'])
@login_required
def user_followers(username):
	users = get_following(username, 'followers')
	if request.method == 'POST':
		if request.form.get('follow'):
			name = request.form['u_fol']
			follow(name)
			return redirect(url_for('user_followers', username=username))
	return render_template('follow/followers.html', users=users)

@app.route('/<username>/following/', methods=['POST', 'GET'])
@login_required
def user_following(username):
	users = get_following(username, 'following')
	if request.method == 'POST':
		if request.form.get('follow'):
			name = request.form['u_fol']
			follow(name)
			return redirect(url_for('user_following', username=username))
	return render_template('follow/following.html', users=users)

@app.route('/add_post/', methods=['POST', 'GET'])
@login_required
def add_post():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		tags = request.form['tags'].split('#')
		final_tags = ['#' + tag.strip() for tag in tags if tag]
		img = request.files['upload']
		if img and allowed_img(img.filename):
			path = secure_filename(img.filename.lower())
			img.save('static/' + path)
			user = get_users(username=session['username'])
			for item in user:
				avatar = item['avatar']
				_id = item['_id']
			now = datetime.now()
			# now = time.mktime(datetime.now().timetuple())
			save({
				'title': title,
				'created_time': now,
				'description': description,
				'tags': final_tags,
				'path': path,
				'author': {
					'name': session['username'],
					'avatar': avatar,
					'user_id': _id
				},
				'liked_users': []
			})
			return redirect(url_for('home'))
		elif not img:
			flash('Необходимо выбрать фото!')
		elif not allowed_img(img.filename):
			flash("Допустимый формат фото: 'png', 'jpg', 'jpeg', 'tiff', 'bmp'")
	return render_template('forms/add_post.html')

@app.route('/explore/', methods=['POST', 'GET'])
@login_required
def explore():
	tag = request.args.get('tag')
	images = get_images(tag)
	return render_template('explore.html', images=images, tag=tag)

@app.route('/detail/', methods=['POST', 'GET'])
@login_required
def detail():
	_id = request.args.get('_id')
	if _id and len(_id) == 24:
		images = get_images(_id=_id)
		if images.count() == 0:
			abort(404)
	else:
		abort(404)
	if request.method == 'POST':
		if request.form.get('comment'):
			comment = request.form['comment'].strip()
			if comment != '':
				add_comment(_id, comment)
		elif request.form.get('like'):
			add_like(_id)
			return redirect(url_for('detail', _id=_id))
		elif request.form.get('com_del'):
			comment = request.form['com_del']
			del_comment(_id, comment)
	return render_template('detail.html', images=images)

@app.route('/', methods=['POST', 'GET'])
@login_required
def home():
	user = get_users(session['username'])
	for items in user:
		names = items['following']
	names.append(session['username'])
	images = get_images(author_follow=names)

	if request.method == 'POST':
		if request.form.get('comment'):
			comment = request.form['comment'].strip()
			if comment != '':
				_id = request.form['id']
				add_comment(_id, comment)
		elif request.form.get('like'):
			_id = request.form['like']
			add_like(_id)
			return redirect(url_for('home'))
		elif request.form.get('com_del'):
			comment = request.form['com_del']
			_id = request.form['id']
			del_comment(_id, comment)
	return render_template('home.html', images=images)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

app.jinja_env.filters['datetime'] = format_datetime
if __name__ == '__main__':
	app.run()