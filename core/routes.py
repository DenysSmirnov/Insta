from core.model import get_users, get_images, search
from core.other import login_required, text_is_valid
from core.errors import page_not_found
from flask import ( 
	render_template, request, redirect, session,
	send_from_directory, abort
)
from . import main
from bson.json_util import dumps

@main.route('/explore/', methods=['POST', 'GET'])
@login_required
def explore():
	tag = request.args.get('tag')
	images = get_images(tag)
	if request.method == 'POST':
		if request.form.get('startFrom'):
			last_id = request.form['startFrom']
			images = get_images(tag, last_id=last_id)
			return dumps(images)
	return render_template('explore.html', images=images,tag=tag)

@main.route('/detail/')
@login_required
def detail():
	_id = request.args.get('_id')
	if _id and len(_id) == 24:
		images = get_images(_id=_id)
		if images.count() == 0:
			abort(404)
	else:
		abort(404)
	return render_template('detail.html', images=images)

@main.route('/', methods=['POST', 'GET'])
@login_required
def home():
	user = get_users(session['username'])
	for items in user:
		names = items['following']
	names.append(session['username'])
	images = get_images(author_follow=names)
	if request.method == 'POST':
		if request.form.get('startFrom'):
			last_id = request.form['startFrom']
			images = get_images(author_follow=names, last_id=last_id)
			return dumps(images)
	return render_template('home.html', images=images)

@main.route('/search/', methods=['POST'])
def ajax_search():
	if request.form.get("referal"):
		text = request.form["referal"].strip()
		if text and text_is_valid(text):
			data = search(text)
			if data[0].count() > 0 or data[1].count() > 0:
				return dumps(cursor for cursor in data)
		return ''