# -*- coding: utf-8 -*-
import os
import falcon

import settings

def serve_static_resource(req, resp):
	"""
	返回static目录下的静态资源
	"""
	path = req.path
	if path.endswith('.css'):
		resp.content_type = 'text/css'
	if path.endswith('.js'):
		resp.content_type = 'text/javascript'
	if path.endswith('.map'):
		resp.content_type = 'text/javascript'
	if path.endswith('.png'):
		resp.content_type = 'image/png'
	
	resp.status = falcon.HTTP_200  # This is the default status
	
	if 'text' in resp.content_type:
		static_file_path = os.path.join(settings.PROJECT_HOME, path[1:])
		if os.path.exists(static_file_path):
			src = open(static_file_path)
			content = src.read()
			src.close()
		
			resp.body = content
		else:
			raise RuntimeError("Invalid static file : " + path) 
	elif 'png' in resp.content_type:
		static_file_path = os.path.join(settings.PROJECT_HOME, path[1:])
		if os.path.exists(static_file_path):
			import io
			resp.stream = io.open(static_file_path, 'rb')
	else:
		raise RuntimeError("Invalid static file : " + path)