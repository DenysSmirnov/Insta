from flask import session, abort, current_app as app
from bson.objectid import ObjectId
from .base import mongo

def get_images(tag=None, _id=None, author=None,
	author_follow=None, last_id=None):
	col = mongo.db.images
	limit_main = app.config['NUM_PER_PAGE_MAIN']
	limit = app.config['NUM_PER_PAGE']
	if tag and last_id:
		return col.find({'tags': tag, '_id': {'$lt': ObjectId(last_id)}},\
			{'_id':1, 'path':1}).sort([('_id', -1)]).limit(limit)
	if author and last_id:
		return col.find({'author.name': author, '_id': {'$lt': ObjectId(last_id)}},\
			{'_id':1, 'path':1}).sort([('_id', -1)]).limit(limit)
	if author_follow and last_id:
		return col.find({'author.name': {'$in': author_follow}, '_id': {'$lt': ObjectId(last_id)}}).\
			sort([('_id', -1)]).limit(limit_main)
	if last_id:
		return col.find({'_id': {'$lt': ObjectId(last_id)}},\
			{'_id':1, 'path':1}).sort([('_id', -1)]).limit(limit)
	if tag:
		return col.find({'tags': tag}).sort([('_id', -1)]).limit(limit)
	if _id:
		return col.find({'_id': ObjectId(_id)})
	if author:
		return col.find({'author.name': author}).sort([('_id', -1)]).limit(limit)
	if author_follow:
		return col.find({'author.name': {'$in': author_follow}}).\
			sort([('_id', -1)]).limit(limit_main)
	return col.find({},{'_id':1, 'path':1}).sort([('_id', -1)]).limit(limit) # explore/ all

def get_users(username=None, names=None, data=None):
	col = mongo.db.users
	if username:
		return col.find({'name' : username}, {'password':0})
	if names:
		return col.find({'name': {'$in': names}}, {'name':1, 'avatar':1, '_id':0})
	if data:
		return col.find(data)

def get_following(username, s):
	'''
	s - string (followers or following) 
	'''
	col = mongo.db.users
	user = col.find({'name' : username}, {s:1, '_id':0})
	if not user.count():
		abort(404)
	else:
		for item in user:
			names = item[s]
		return col.find({'name': {'$in': names}}, {'password':0})

def save(image):
	mongo.db.images.insert_one(image)

def save_avatar(username, avatar):
	mongo.db.users.update_one({'name' : username},{'$set': {'avatar' : avatar}})
	mongo.db.images.update_many({'author.name' : username},{'$set': {'author.avatar' : avatar}})

def follow(username):
	col = mongo.db.users
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
			return 0
		else:
			col.update_one(
				{'name' : session['username']},{'$addToSet': {
				'following' : username}}
			)
			col.update_one(
				{'name' : username},{'$addToSet': {
				'followers' : session['username']}}
			)
			return 1

def add_comment(_id, comment):
	mongo.db.images.update_one(
		{'_id' : ObjectId(_id)},{'$addToSet': {
		'comments' : {session['username']: comment}}}
	)
	return 1

def del_comment(_id, comment):
	mongo.db.images.update_one(
		{'_id' : ObjectId(_id)},{'$pull': {
		'comments' : {session['username']: comment}}}
	)
	return 1

def del_post(_id):
	col = mongo.db.images
	data = col.find({'_id' : ObjectId(_id)})
	for item in data:
		if item['author']['name'] == session['username']:
			col.delete_one({'_id' : ObjectId(_id)})
			return 1
		else:
			print('Подделка запроса на удаление поста!')
			return 0

def add_like(_id):
	col = mongo.db.images
	data = col.find({'_id' : ObjectId(_id)})
	for item in data:
		if session['username'] in item['liked_users']:
			col.update_one(
				{'_id' : ObjectId(_id)},{'$pull': {
				'liked_users' : session['username']}}
			)
			return 0
		else:
			col.update_one(
				{'_id' : ObjectId(_id)},{'$addToSet': {
				'liked_users' : session['username']}}
			)
			return 1

def update_profile(fio, name, about, mail):
	col = mongo.db.users
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
		col = mongo.db.images
		col.update_many({'author.name': session['username']}, {
			'$set': {'author.name' : name.lower()}
		})

def update_password(password):
	mongo.db.users.update_one({'name' : session['username']},{
		'$set': {'password' : password}})

def user_check_and_create(name, password):
	col = mongo.db.users
	i = col.find({'name': name}).count()
	if i == 0:
		col.insert_one({
			'name': name,
			'password': password,
			'followers': [],
			'following': [],
			'avatar': 'no_avatar.png'
		})
		return True
	else:
		return False

def search(exp):
	data = mongo.db.users.find({
		'$or': [{'name' : {'$regex': exp, '$options': '$i'}},
		{'fio' : {'$regex': exp, '$options': '$i'}}]},
		{'name':1, 'fio':1, 'avatar':1, '_id':0})

	data2 = mongo.db.images.find({
		'tags': {'$regex': exp, '$options': '$i'}}, {'tags': 1, '_id':0})
	cursor = [data, data2]
	return cursor