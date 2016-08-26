# -*- coding: utf-8 -*-

import json
import urllib
import urlparse
import uuid

import requests
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.core.zipkin import zipkin_client
from eaglet.core.zipkin.zipkin_client import ZipkinClient
from time import time

DEFAULT_TIMEOUT = 10
DEFAULT_RETRY_COUNT = 3
CALL_SERVICE_WATCHDOG_TYPE = 'call_service_resource'


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

def url_add_params(url, **params):
	""" 在网址中加入新参数 """
	pr = urlparse.urlparse(url)
	query = dict(urlparse.parse_qsl(pr.query))
	query.update(params)
	prlist = list(pr)
	prlist[4] = urllib.urlencode(query)
	return urlparse.ParseResult(*prlist).geturl()


class Inner(object):
	def __init__(self, service):
		self.service = service
		self.__resp = None

	def get(self, options):
		return self.__request(options['resource'], options['data'], 'get')

	def put(self, options):
		return self.__request(options['resource'], options['data'], 'put')

	def post(self, options):
		return self.__request(options['resource'], options['data'], 'post')

	def delete(self, options):
		return self.__request(options['resource'], options['data'], 'delete')

	def __request(self, resource, params, method):
		# 构造url
		"""

		@return is_success,code,data
		"""

		host = 'api.weapp.com'

		resource_path = resource.replace('.', '/')

		base_url = 'http://%s/%s/%s/' % (host, self.service, resource_path)

		# zipkin支持
		if hasattr(zipkin_client, 'zipkinClient') and zipkin_client.zipkinClient:
			zid = zipkin_client.zipkinClient.zid
			zindex = zipkin_client.zipkinClient.zindex
			fZindex = zipkin_client.zipkinClient.fZindex
			zdepth = zipkin_client.zipkinClient.zdepth
			zipkinClient = zipkin_client.zipkinClient
		else:
			zid = str(uuid.uuid1())
			zindex = 1
			fZindex = 1
			zdepth = 1
			zipkinClient = zipkin_client.ZipkinClient(self.service, zid, zdepth, fZindex)
			

			

		url = url_add_params(base_url, zid=zid, zindex=zindex, f_zindex=str(fZindex) + '_' + str(zindex),
		                     zdepth=zdepth + 1)

		start = time()
		try:
			# 访问资源
			if method == 'get':
				resp = requests.get(url, params, timeout=DEFAULT_TIMEOUT)
			elif method == 'post':
				resp = requests.post(url, params, timeout=DEFAULT_TIMEOUT)
			else:
				# 对于put、delete方法，变更为post方法，且querystring增加_method=put或_method=delete
				url = url_add_params(url, _method=method)
				resp = requests.post(url, params, timeout=DEFAULT_TIMEOUT)

			self.__resp = resp

			# 解析响应
			if resp.status_code == 200:

				json_data = json.loads(resp.text)
				code = json_data['code']

				if code == 200 or code == 500:
					self.__log(True, url, params, method)
					return json_data

				else:
					self.__log(False, url, params, method, 'ServiceProcessFailure', 'BUSINESS_CODE:' + str(code))
					return None

			else:
				self.__log(False, url, params, method, 'ServerResponseFailure',
				           'HTTP_STATUS_CODE:' + str(resp.status_code))
				return None

		except requests.exceptions.RequestException as e:
			self.__log(False, url, params, method, str(type(e)), unicode_full_stack())
			return None
		except BaseException as e:
			self.__log(False, url, params, method, str(type(e)), unicode_full_stack())
			return None
		finally:
			stop = time()
			duration = stop - start
			zipkinClient.sendMessge(zipkin_client.TYPE_CALL_SERVICE, duration, method=method, resource='', data='')

	def __log(self, is_success, url, params, method, failure_type='', failure_msg=''):
		msg = {
			'is_success': is_success,
			'url': url,
			'params': params,
			'method': method,
			'failure_type': failure_type,
			'failure_msg': failure_msg,

		}

		resp = self.__resp

		if resp:
			msg['http_code'] = resp.status_code
			msg['resp_text'] = resp.text
		else:
			msg['http_code'] = ''
			msg['resp_text'] = ''

		if is_success:
			watchdog.info(msg, CALL_SERVICE_WATCHDOG_TYPE, server_name=self.service)
		else:
			watchdog.alert(msg, CALL_SERVICE_WATCHDOG_TYPE, server_name=self.service)


class Resource(object):
	@staticmethod
	def use(service):
		return Inner(service)
