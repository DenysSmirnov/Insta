from core.other import *
from core.model import *
from flask import (
	render_template, request, redirect, url_for, session, 
	send_from_directory, flash, abort, current_app as app
)
import os.path
from datetime import datetime
from werkzeug import secure_filename
from bson.json_util import dumps
from . import main

@main.route('/register/', methods=['GET', 'POST'])
def register():
	name = None
	password = None
	if request.method == 'POST':
		name = request.form.get('name')
		password = request.form.get('password')
		if login_is_valid(name):
			new_user = user_check_and_create(name, password)
			if new_user:
				return redirect(url_for('.login'))
			else:
				flash('Имя уже занято')
		else:
			flash('Недопутимое имя пользователя!')
	return render_template('user/register.html', name=name, password=password)

@main.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		name = request.form.get('name')
		password = request.form.get('password')
		users = {'name': name, 'password': password}
		users = get_users(data=users)
		users = list(users)
		if len(users) == 0:
			flash('Пользователь с таким логином/паролем не найден')
		else:
			user = users[0]
			session['username'] = user['name']
			return redirect(url_for('main.home'))
	return render_template('user/login.html')

@main.route('/logout/')
def logout():
	if session.get('username'):
		del session['username']
		return redirect(url_for('main.home'))
	else:
		return redirect(url_for('main.login'))

@main.route('/accounts/edit/', methods=['GET', 'POST'])
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
		return redirect(url_for('main.user', username=name))
	return render_template('forms/edit_account.html', userdata=userdata)

@main.route('/accounts/password/change/', methods=['GET', 'POST'])
@login_required
def change_password():
	if request.method == 'POST':
		OldPassword = request.form.get('cppOldPassword')
		NewPassword = request.form.get('cppNewPassword')
		ConfirmPassword = request.form.get('cppConfirmPassword')
		if OldPassword and NewPassword and ConfirmPassword:
			if NewPassword == ConfirmPassword:
				data = {'name': session['username']}
				userdata = get_users(data=data)
				for item in userdata:
					if OldPassword == item['password']:
						update_password(NewPassword)
					else:
						flash('Введен неверный пароль!')
						return redirect(url_for('.change_password'))
			else:
				flash('Пароли не совпадают!')
				return redirect(url_for('.change_password'))
		else:
			flash('Заполнены не все поля формы!')
			return redirect(url_for('.change_password'))
		return redirect(url_for('main.login'))
	return render_template('forms/change_password.html')

@main.route('/add_post/', methods=['POST', 'GET'])
@login_required
def add_post():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		tags = request.form['tags'].replace(' ', '#').split('#')
		final_tags = ['#' + tag.strip().lower() for tag in tags if tag]
		img = request.files['upload']
		if img and allowed_img(img.filename):
			path = upload_img(img)
			user = get_users(username=session['username'])
			for item in user:
				avatar = item['avatar']
				_id = item['_id']
			now = datetime.utcnow()
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
			return redirect(url_for('.home'))
		elif not img:
			flash('Необходимо выбрать фото!')
		elif not allowed_img(img.filename):
			flash("Допустимый формат фото: 'png', 'jpg'")
	return render_template('forms/add_post.html')

@main.route('/<username>/', methods=['POST', 'GET'])
@login_required
def user(username):
	images = get_images(author=username)
	userdata = get_users(username)
	if images.count() == 0 and userdata.count() == 0:
		abort(404)
	user_image_count = images.count()

	if request.method == 'POST':
		if request.form.get('follow'):
			follow(username)
			return redirect(url_for('.user', username=username))
		elif request.form.get('avatar'):
			avatar = request.files['upload']
			if avatar and allowed_img(avatar.filename):
				resized_url = upload_img(avatar, res='152x152', quality=85)
				save_avatar(username, resized_url)
		elif request.form.get('startFrom'):
			last_id = request.form['startFrom']
			images = get_images(author=username, last_id=last_id)
			return dumps(images)
	return render_template('user.html', images=images, userdata=userdata, \
		user_image_count=user_image_count)

@main.route('/<username>/followers/')
@login_required
def user_followers(username):
	users = get_following(username, 'followers')
	return render_template('follow/followers.html', users=users)

@main.route('/<username>/following/')
@login_required
def user_following(username):
	users = get_following(username, 'following')
	return render_template('follow/following.html', users=users)

@main.route('/ajax_/', methods=['POST'])
def ajax():
	functions = dict(ufol=follow, addCom=add_comment,
		like=add_like, delPost=del_post, delCom=del_comment)
	if request.form:
		args = []
		for key, value in dict(request.form).items():
			args += value
		data = functions[key](*args)
		return str(data)
	data = dict(uname=session['username'],
		numPerPage=app.config['NUM_PER_PAGE_MAIN'],
		uploadUrl=app.config['UPLOAD_URL'])
	return dumps(data)