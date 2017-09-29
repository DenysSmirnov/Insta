from flask import session, abort
from bson.objectid import ObjectId
# from bson.dbref import DBRef
from .base import mongo

def get_images(tag=None, _id=None, author=None, author_follow=None):
	col = mongo.db.images
	if tag:
		return col.find({'tags': tag})
	if _id:
		return col.find({'_id': ObjectId(_id)})
	if author:
		return col.find({'author.name': author}).sort([('_id', -1)])
	if author_follow:
		return col.find({'author.name': {'$in': author_follow}}).\
			sort([('_id', -1)])#.limit(10)
	return col.find().sort([('_id', -1)])

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
		else:
			col.update_one(
				{'name' : session['username']},{'$addToSet': {
				'following' : username}}
			)
			col.update_one(
				{'name' : username},{'$addToSet': {
				'followers' : session['username']}}
			)

def add_comment(_id, comment):
	mongo.db.images.update_one(
		{'_id' : ObjectId(_id)},{'$addToSet': {
		'comments' : {session['username']: comment}}}
	)

def del_comment(_id, comment):
	mongo.db.images.update_one(
		{'_id' : ObjectId(_id)},{'$pull': {
		'comments' : {session['username']: comment}}}
	)

def del_post(_id):
	mongo.db.images.delete_one({'_id' : ObjectId(_id)})

def add_like(_id):
	col = mongo.db.images
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