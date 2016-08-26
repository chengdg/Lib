# -*- coding: utf-8 -*-

import settings
import eaglet.peewee as peewee
import json
import copy
from datetime import datetime
import time

from eaglet.core.cache import utils as cache_utils
import logging

class QueryMonitorMiddleware(object):
	def process_request(self, request, response):
		#import resource
		#resource.indent = 0
		
		print 'empty peewee.QUERIES'
		peewee.QUERIES = []
		cache_utils.clear_queries()

	def process_response(self, request, response, resource):
		if settings.DEBUG:
			if response.body:
				try:
					obj = json.loads(response.body)
					obj['queries'] = copy.copy(peewee.QUERIES)
					redis_queries = cache_utils.get_queries()
					obj['queries'].extend(copy.copy(redis_queries))
					response.body = json.dumps(obj)
				except:
					pass


class RedisMiddleware(object):
	def process_request(self, request, response):
		if request.params.get('__nocache', None):
			access_token_keys = cache_utils.get_keys('access_token*')
			access_token_dict = {}

			for access_token_key in access_token_keys:
				access_token_dict[access_token_key] = cache_utils.GET_CACHE(access_token_key)
			
			cache_utils.clear_db()

			for key,value in access_token_dict.items():
				cache_utils.SET_CACHE(key, value)


