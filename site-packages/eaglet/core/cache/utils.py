# -*- coding: utf-8 -*-

__author__ = 'bert'

import os
from time import time
import logging
# Import the fastest implementation of
# pickle package. This should be removed
# when python3 come the unique supported
# python version
try:
    import cPickle as pickle
except ImportError:
    import pickle

import redis
import settings

from ..exceptionutil import unicode_full_stack
from eaglet.utils.stack_util import get_trace_back

from eaglet.core.zipkin import zipkin_client

if settings.REDIS_HOST:
	r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_CACHES_DB)
else:
	r = None

CACHE_QUERIES = []

def clear_queries():
	global CACHE_QUERIES
	CACHE_QUERIES = []

def get_queries():
	return CACHE_QUERIES


class Object(object):
	def __init__(self, name=""):
		self.name = name

	def to_dict(self):
		return self.__dict__

def modify_keys(function):
	def _modify_keys(*args, **kwargs):
		args = list(args)
		keys = args[0]
		if isinstance(keys, list):
			acture_keys = []
			for key in keys:
				acture_keys.append(settings.REDIS_CACHE_KEY+key)
			keys = acture_keys
		else:
			keys = settings.REDIS_CACHE_KEY + keys
		args[0] = keys
		args = tuple(args)
		return function(*args, **kwargs)
	return _modify_keys

@modify_keys
def set_cache(key, value, timeout=0):
	pickled_value = pickle.dumps(value)
	r.set(key, pickled_value)

@modify_keys
def get_cache(key):
	value = r.get(key)
	if not value:
		return value
	return pickle.loads(value)
	# return r.get(key)

@modify_keys
def get_many(keys):
	return [pickle.loads(value) if value else value for value in r.mget(keys)]

@modify_keys
def delete_cache(key):
	r.delete(key)
	#r.delete(':1:'+key)

@modify_keys
def delete_pattern(key):
	keys = r.keys(key)

def clear_db():
	r.flushdb()

def set_cache_wrapper(key, value, timeout=0):
	start = time()
	try:	
		return set_cache(key, value, timeout)
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		stop = time()
		duration = stop - start
		value_type = str(type(value)).replace('<', '&lt;').replace('>', '&gt;')
		query = 'set `cache`: {`%s`: `%s`)' % (key, value_type)
		if zipkin_client.zipkinClient:
			zipkin_client.zipkinClient.sendMessge(zipkin_client.TYPE_CALL_REDIS, duration, method='', resource=query, data='')
		
		CACHE_QUERIES.append({
			'source': 'redis',
			'query': query,
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})
		
@modify_keys
def get_keys(pattern):
	keys = r.keys(pattern)
	return keys

def get_cache_wrapper(key):
	start = time()
	success = False
	try:
		value = get_cache(key)
		if value:
			success = True
		return value
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		stop = time()
		duration = stop - start
		query = 'get `cache`: `%s` =&gt; %s' % (key, 'hit' if success else 'MISS!!')
		if zipkin_client.zipkinClient:
			zipkin_client.zipkinClient.sendMessge(zipkin_client.TYPE_CALL_REDIS, duration, method='', resource=query, data='')
		CACHE_QUERIES.append({
			'source': 'redis',
			'query': query,
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


def get_many_wrapper(keys):
	start = time()
	success = False
	try:
		value = get_many(keys)
		if value:
			success = True
		return value
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		stop = time()
		duration = stop - start
		query = 'get_many from `cache`: `%s` =&gt; %s' % (keys, 'hit' if success else 'MISS!!')
		if zipkin_client.zipkinClient:
			zipkin_client.zipkinClient.sendMessge(zipkin_client.TYPE_CALL_REDIS, duration, method='', resource=query, data='')
		CACHE_QUERIES.append({
			'source': 'redis',
			'query': query,
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


def delete_cache_wrapper():
	start = time()
	try:
		return delete_cache()
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		value = 'delete_cache_wrapper'
		stop = time()
		duration = stop - start
		value_type = str(type(value)).replace('<', '&lt;').replace('>', '&gt;')
		query = 'delete `cache`: {`%s`: `%s`)' % (key, value_type)
		if zipkin_client.zipkinClient:
			zipkin_client.zipkinClient.sendMessge(zipkin_client.TYPE_CALL_REDIS, duration, method='', resource=query, data='')
		
		CACHE_QUERIES.append({
			'source': 'redis',
			'query': query,
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


def delete_pattern_wrapper(pattern):
	start = time()
	try:
		return delete_pattern(pattern)
	except:
		if settings.DEBUG:
			raise
		else:
			return None
	finally:
		value = 'delete_pattern_wrapper'
		stop = time()
		duration = stop - start
		query = 'delete_pattern from `cache`: `%s`' % pattern
		if zipkin_client.zipkinClient:
			zipkin_client.zipkinClient.sendMessge(zipkin_client.TYPE_CALL_REDIS, duration, method='', resource=query, data='')

		CACHE_QUERIES.append({
			'source': 'redis',
			'query': query,
			'time': "%.3f" % duration,
			'stack': get_trace_back()
		})


if settings.MODE == 'develop':
	SET_CACHE = set_cache_wrapper
	GET_CACHE = get_cache_wrapper
	DELETE_CACHE = delete_cache_wrapper
	DELETE_PATTERN = delete_pattern_wrapper
	GET_MANY = get_many_wrapper
else:
	SET_CACHE = set_cache
	GET_CACHE = get_cache
	DELETE_CACHE = delete_cache
	DELETE_PATTERN = delete_pattern
	GET_MANY = get_many


def set(key, value, timeout=None):
	"""
	向cache中写入数据
	"""
	SET_CACHE(key, value, timeout)


def get_from_cache(key, on_miss=None):
	"""
	从cache获取数据，构建对象
	"""
	obj = GET_CACHE(key)
	if obj:
		return obj
	else:
		if on_miss:
			try:
				fresh_obj = on_miss()
				if not fresh_obj:
					return None
				value = fresh_obj['value']
				SET_CACHE(key, value)
				if 'keys' in fresh_obj:
					for fresh_key in fresh_obj['keys']:
						SET_CACHE(fresh_key, value)
				return value
			except:
				if settings.DEBUG:
					raise
				else:
					print unicode_full_stack()
					return None
get = get_from_cache


def get_many_from_cache(key_infos):
	keys = []
	key2onmiss = {}

	for key_info in key_infos:
		key = key_info['key']
		keys.append(key)
		key2onmiss[key] = key_info['on_miss']

	values = GET_MANY(keys)
	objs = {}
	for i in range(len(keys)):
		key = keys[i]
		value = values[i]
		if value:
			objs[key] = value

	for key in keys:
		if objs.get(key, None):
			continue

		on_miss = key2onmiss[key]
		if on_miss:
			fresh_obj = on_miss()
			if not fresh_obj:
				value = {}
			else:
				value = fresh_obj['value']
				SET_CACHE(key, value)
			objs[key] = value

	return objs


# redis 集合操作
def sadd(name, *values):
	return r.sadd(name, *values)


def sismember(name, value):
	return r.sismember(name, value)


def set_key_expire(name, time):
	r.expire(name, time)


def exists_key(name):
	return r.exists(name)
