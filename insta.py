#!/usr/bin/env python

from core.base import create_app

app = create_app('default')

if __name__ == '__main__':
	app.run()