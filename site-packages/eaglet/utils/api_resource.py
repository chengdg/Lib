# -*- coding: utf-8 -*-
import json
import urllib
import urlparse

import requests
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.core.zipkin import zipkin_client
from time import time

DEFAULT_TIMEOUT = 10
DEFAULT_RETRY_COUNT = 3
CALL_SERVICE_WATCHDOG_TYPE = 'call_service'


# def conn_try_again(function):
# 	RETRIES = 0
# 	# 重试的次数
# 	count = {"num": RETRIES}
#
# 	def wrapped(*args, **kwargs):
# 		try:
# 			return function(*args, **kwargs)
# 		except Exception as e:
# 			if count['num'] < DEFAULT_RETRY_COUNT:
# 				count['num'] += 1
# 				return wrapped(*args, **kwargs)
# 			else:
# 				return False, None
#
# 	return wrapped



class RequestFailure(Exception):
	pass


# class HTTPFailure(RequestFailure):
# 	pass


class ServerResponseFailure(RequestFailure):
	"""
	服务器返回非200响应
	"""
	pass


class ServiceProcessFailure(RequestFailure):
	"""
	服务器返回200响应，但非正常的自定义code（200、500）
	"""
	pass


# HTTP请求异常
HTTPFailure = requests.exceptions.RequestException


def url_add_params(url, **params):
	""" 在网址中加入新参数 """
	pr = urlparse.urlparse(url)
	query = dict(urlparse.parse_qsl(pr.query))
	query.update(params)
	prlist = list(pr)
	prlist[4] = urllib.urlencode(query)
	return urlparse.ParseResult(*prlist).geturl()


class APIResourceClient(object):
	def __init__(self, host, resource):
		self.host = host
		self.resource = resource
		self.resp = None

	def get(self, params):
		return self.__request(self.host, self.resource, params, 'get')

	def put(self, params):
		return self.__request(self.host, self.resource, params, 'put')

	def post(self, params):
		return self.__request(self.host, self.resource, params, 'post')

	def delete(self, params):
		return self.__request(self.host, self.resource, params, 'delete')

	# def put(self, options):
	# 	self.__request(options['host'], options['resource'], options['params'], 'put')
	#
	# def post(self, options):
	# 	self.__request(options['host'], options['resource'], options['params'], 'post')
	#
	# def delete(self, options):
	# 	self.__request(options['host'], options['resource'], options['params'], 'delete')

	# def put(self, resource, data):
	# 	self.__request(options['resource'], options['data'], 'put')
	#
	# def post(self, resource, data):
	# 	self.__request(options['resource'], options['data'], 'post')
	#
	# def delete(self, resource, data):
	# 	self.__request(options['resource'], options['data'], 'delete')

	def __request(self, host, resource, params, method):

		# 构造url
		"""

		@return is_success,code,data
		"""
		path = resource.replace('.', '/')
		url = 'http://%s/%s/' % (host, path)

		# todo zipkin支持
		#
		if hasattr(zipkin_client, 'zipkinClient') and zipkin_client.zipkinClient:
			zid = zipkin_client.zipkinClient.zid
			zindex = zipkin_client.zipkinClient.zindex
			fZindex = zipkin_client.zipkinClient.fZindex
			zdepth = zipkin_client.zipkinClient.zdepth
		else:
			zid = 1
			zindex = 1
			fZindex = 1
			zdepth = 1

		url = url_add_params(url, zid=zid, zindex=zindex, f_zindex=str(fZindex) + '_' + str(zindex), zdepth=zdepth+1)



		resp = None
		start = time()
		try:
			# 访问资源
			if method == 'get':
				resp = requests.get(url, params, timeout=DEFAULT_TIMEOUT)
			elif method == 'post':
				resp = requests.post(url, params, timeout=DEFAULT_TIMEOUT)
			else:
				# url = (url + '?_method=' + method) if ('_method' not in url) else url
				url = url_add_params(url, _method=method)
				resp = requests.post(url, params, timeout=DEFAULT_TIMEOUT)

				self.resp = resp

			# 解析响应
			if resp.status_code == 200:
				json_data = json.loads(resp.text)
				data = json_data['data']
				code = json_data['code']
				if code == 200 or code == 500:

					self.__log(True, url, params, resp)
					print('--------',url,params,resp,resp.text,resp.status_code)
					return True, code, data
				else:
					raise ServiceProcessFailure

			else:

				raise ServerResponseFailure

		except (HTTPFailure, RequestFailure) as e:
			traceback = unicode_full_stack()
			self.__log(False, url, params, resp, str(type(e)), traceback)
			return False, 0, {}
		except BaseException as e:
			traceback = unicode_full_stack()
			self.__log(False, url, params, resp, str(type(e)), traceback)
			return False, 0, {}
		finally:

			stop = time()
			duration = stop - start

			if hasattr(zipkin_client, 'zipkinClient') and zipkin_client.zipkinClient:
				zipkin_client.zipkinClient.sendMessge(zipkin_client.TYPE_CALL_SERVICE, duration, method='', resource='',
				                                      data='')

	def __log(self, is_success, url, params, resp, failure_type='', traceback=''):
		if failure_type:
			failure_type = 'APIResourceClient_ERROR:' + failure_type
		msg = {
			'is_success': is_success,
			'url': url,
			'params': params,
			'failure_type': failure_type,
			'traceback': traceback
		}

		resp = self.resp

		if resp:
			msg['http_code'] = resp.status_code
			msg['resp_text'] = resp.text
		else:
			msg['http_code'] = ''
			msg['resp_text'] = ''

		if is_success:
			watchdog.info(msg, CALL_SERVICE_WATCHDOG_TYPE)
		else:
			watchdog.alert(msg, CALL_SERVICE_WATCHDOG_TYPE)
