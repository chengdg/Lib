# -*- coding: utf-8 -*-

#import sys
#import os
import settings
#import datetime as dt
import time
import logging
from .log import wapi_log, param_to_text
from eaglet.core import api_resource

"""
wapi_path = os.path.join(settings.PROJECT_HOME, '..', 'wapi')
for f in os.listdir(wapi_path):
	f_path = os.path.join(wapi_path, f)
	if os.path.isdir(f_path):
		init_file_path = os.path.join(f_path, '__init__.py')
		if not os.path.exists(init_file_path):
			continue

		module_name = 'wapi.%s' % f
		module = __import__(module_name, {}, {}, ['*',])
"""

class ApiNotExistError(Exception):
	pass


def wapi_call(method, app, resource, data, req=None):
	resource_name = resource
	key = '%s-%s' % (app, resource)
	#if settings.WAPI_LOGGER_ENABLED:
	# if settings.MODE == 'develop':
	# 	logging.info("called WAPI: {} {}/{}, param: {}".format(method, app, resource, param_to_text(data)))

	#start_at = dt.datetime.now()
	start_at = time.clock()

	resource = api_resource.APPRESOURCE2CLASS.get(key, None)
	if not resource:
		wapi_log(app, resource_name, method, data, (time.clock()-start_at), -1)
		raise ApiNotExistError('%s:%s' % (key, method))

	func = getattr(resource['cls'], method, None)
	if not func:
		wapi_log(app, resource_name, method, data, (time.clock()-start_at), -1)
		raise ApiNotExistError('%s:%s' % (key, method))

	response = func(data)
	wapi_log(app, resource_name, method, data, (time.clock()-start_at), 0)
	return response


def get(app, resource, data):
	return wapi_call('get', app, resource, data)


def post(app, resource, data):
	return wapi_call('post', app, resource, data)


def put(app, resource, data):
	return wapi_call('put', app, resource, data)


def delete(app, resource, data):
	return wapi_call('delete', app, resource, data)
