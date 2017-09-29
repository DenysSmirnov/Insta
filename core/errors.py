# from core.base import app
from flask import render_template, request
from . import main

@main.errorhandler(404)
def page_not_found(error):
	return render_template('errors/404.html'), 404