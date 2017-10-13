# import os.path
from core.model import (
	get_users, get_images, add_comment, del_comment, del_post, save,
	add_like
)
from core.other import login_required, allowed_img, upload_img
from core.errors import page_not_found
from flask import ( 
	render_template, request, redirect, send_from_directory,
	url_for, session, flash, abort, current_app as app
)
from datetime import datetime
from . import main
from bson.json_util import dumps

@main.route('/explore/', methods=['POST', 'GET'])
@login_required
def explore():
	resize_url = app.config['UPLOAD_URL']
	tag = request.args.get('tag')
	images = get_images(tag)
	if request.method == 'POST':
		if request.form.get('startFrom'):
			last_id = request.form['startFrom']
			images = get_images(tag, last_id=last_id)
			return dumps(images)
	return render_template('explore.html', images=images,
		tag=tag, resize_url=resize_url)

@main.route('/detail/', methods=['POST', 'GET'])
@login_required
def detail():
	resize_url = app.config['UPLOAD_URL']
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
			return redirect(url_for('.detail', _id=_id))
		elif request.form.get('com_del'):
			comment = request.form['com_del']
			del_comment(_id, comment)
		elif request.form.get('post_del'):
			del_post(_id)
			return redirect(url_for('.home'))
	return render_template('detail.html', images=images, resize_url=resize_url)

@main.route('/', methods=['POST', 'GET'])
@login_required
def home():
	resize_url = app.config['UPLOAD_URL']
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
			return redirect(url_for('.home'))
		elif request.form.get('com_del'):
			comment = request.form['com_del']
			_id = request.form['id']
			del_comment(_id, comment)
		elif request.form.get('post_del'):
			_id = request.form['id']
			del_post(_id)
			return redirect(url_for('.home'))
		elif request.form.get('startFrom'):
			last_id = request.form['startFrom']
			images = get_images(author_follow=names, last_id=last_id)
			return dumps(images)
	return render_template('home.html', images=images,
		resize_url=resize_url)

@main.route('/add_post/', methods=['POST', 'GET'])
@login_required
def add_post():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		tags = request.form['tags'].split('#')
		final_tags = ['#' + tag.strip() for tag in tags if tag]
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