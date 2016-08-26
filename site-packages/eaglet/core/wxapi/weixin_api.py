# -*- coding: utf-8 -*-

__author__ = 'bert'

import json

import api_settings
import weixin_error_codes as errorcodes

#from eaglet.core.jsonresponse import decode_json_str
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.utils.url_helper import complete_get_request_url
#from core.weixin_media_saver import save_weixin_user_head_img

from eaglet.core import watchdog

#from weixin.user.access_token import update_access_token
from eaglet.core.wxapi.util import ObjectAttrWrapedInDict

"""
微信Api

微信平台针对认证后的服务号提供api接口，具体列表和文档登录微信公众
平台后点击左侧导航栏中服务下的我的服务可以看到

该模块对微信平台提供的api接口进行描述，便于在程序中进行微信api的访问
每一个api的调用该模块根据微信平台api的协议进行相应请求的组织，然后
通过weixin_http_client（默认使用WeixinHttpClient）进行实际请求返回处理结果

如果需要测试，给定weixin_http_client的stub或者mock的实现即可

目前提供的api接口有：

get_user_info
	获取用户基本信息
	文档参见http://mp.weixin.qq.com/wiki/index.php?title=%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF

get_qrcode
	通过ticket换取二维码，返回二维码图片(jpg格式)内容
	文档参见http://mp.weixin.qq.com/wiki/index.php?title=%E7%94%9F%E6%88%90%E5%B8%A6%E5%8F%82%E6%95%B0%E7%9A%84%E4%BA%8C%E7%BB%B4%E7%A0%81

create_qrcode_ticket
	创建二维码ticket
	文档参见http://mp.weixin.qq.com/wiki/index.php?title=%E7%94%9F%E6%88%90%E5%B8%A6%E5%8F%82%E6%95%B0%E7%9A%84%E4%BA%8C%E7%BB%B4%E7%A0%81	

send_custom_msg
	发送客服消息
	文档参见http://mp.weixin.qq.com/wiki/index.php?title=%E5%8F%91%E9%80%81%E5%AE%A2%E6%9C%8D%E6%B6%88%E6%81%AF

upload_media
	上传多媒体文件
	文档参见http://mp.weixin.qq.com/wiki/index.php?title=%E4%B8%8A%E4%BC%A0%E4%B8%8B%E8%BD%BD%E5%A4%9A%E5%AA%92%E4%BD%93%E6%96%87%E4%BB%B6

download_media
	下载多媒体文件
	文档参见http://mp.weixin.qq.com/wiki/index.php?title=%E4%B8%8A%E4%BC%A0%E4%B8%8B%E8%BD%BD%E5%A4%9A%E5%AA%92%E4%BD%93%E6%96%87%E4%BB%B6

目前只实现了get_user_info接口

每个接口调用如果发生异常会抛出WeixinApiError, 可通过该异常示例的
error_response属性来获取微信的api反馈信息，error_response包含的信息有：
errorcode: 错误代码
errmsg: 错误信息
detail: 异常详情


如果发现access_token失效则需要提供最新的access_token，重新获取WeixinApi实例

-----------------------------------------------------------------------------------------

整体构架及微信api增加步骤：
	1.api_settings 增加 类似'get_user_info': 'core.wxapi.user_info_api.WeixinUserApi'
	2.api类规范如下：
		a.  该方法返回访问该api的请求方式：post or get
			def request_method(self):
			return 'get'

	 	b. 该方法返回当前要访问的api的地址和该api的描述
			def get_get_request_url_and_api_info(self, mpuser_access_token, varargs):
				pass

		c.  该方法处理请求的结果并组织相应结构返回结果
			def parse_response(self, api_response):
				pass
		d. 	该方法针对post方式组织post数据	
			def parse_post_param_json(self, varargs):
				pass
	
"""

def decode_json_str(str):
	return json.loads(str)

class WeixinApiResponse(object):
	def __init__(self, weixin_response):
		if type(weixin_response) != dict:
			self.response_json = self.__parse_response(weixin_response_text)
		else:
			self.response_json = weixin_response

		self.errcode = self.response_json.get('errcode', errorcodes.SUCCESS_CODE)
		self.errmsg = self.response_json.get('errmsg', '')

	def is_failed(self):
		return self.response_json.get('errcode', errorcodes.SUCCESS_CODE) != errorcodes.SUCCESS_CODE
		
	def get_errormsg_in_zh(self):
		return errorcodes.code2msg.get(self.errcode, self.errmsg) 

	def __parse_response(self, response_text):
		response_text = response_text.strip()
		return decode_json_str(response_text)

class WeixinApiError(Exception):
	def __init__(self, weixin_error_response):
		self.error_response = weixin_error_response

	def __unicode__(self):
		if hasattr(self.error_response, 'detail'):
			detail = self.error_response.detail
		else:
			detail = ''

		if hasattr(self.error_response, 'errcode'):
			errcode = self.error_response.errcode
		else:
			errcode = ''

		if hasattr(self.error_response, 'errmsg'):
			errmsg = self.error_response.errmsg
		else:
			errmsg = ''	

		return u"errcode:{}\nerrmsg:{}\ndetail:{}".format(
			errcode,
			errmsg,
			detail
			)

	def __str__(self):
		return self.__unicode__().encode('utf-8')

"""
微信Api错误信息，包含以下属性：
errorcode : 错误代码，全部错误代码请参见weixin_error_codes
errmsg : 错误信息
detail : 异常堆栈
"""
class WeixinErrorResponse(ObjectAttrWrapedInDict):
	def __init__(self, src_dict):
		super(WeixinErrorResponse, self).__init__(src_dict)

		if not hasattr(self, 'detail'):
			self.detail = ''

def build_system_exception_response():
	response_dict = {}
	response_dict['errcode'] = errorcodes.SYSTEM_ERROR_CODE
	response_dict['errmsg'] = errorcodes.code2msg[errorcodes.SYSTEM_ERROR_CODE]
	response_dict['detail'] = unicode_full_stack()
	return WeixinErrorResponse(response_dict)

import api_settings
import new
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
def call_api(weixin_api, api_instance_class):

	def _call_api(*agrs):
		# 获得该api的请求方式： get or post
		try:
			request_method = api_instance_class.request_method()
		except:
			raise ValueError(u'request method illegality')
	
		request_url, api_desc = api_instance_class.get_get_request_url_and_api_info(weixin_api.mpuser_access_token, agrs)
		api_response = None
		try:
			# get 
			if request_method == api_settings.API_GET:
				api_response = weixin_api.weixin_http_client.get(request_url)
			# post	
			if request_method == api_settings.API_POST:
				post_param_json_str = api_instance_class.parese_post_param_json_str(agrs)
				
				if hasattr(api_instance_class, 'is_for_form') and api_instance_class.is_for_form:
					is_for_form = True
				else:
					try:
						post_param_json_str = decode_json_str(post_param_json_str)
					except:
						pass
					is_for_form = False
					
				api_response = weixin_api.weixin_http_client.post(request_url, post_param_json_str, is_for_form)
		except:
			#weixin_api._raise_system_error(api_desc, weixin_api.mpuser_access_token.mpuser.owner_id)
			weixin_api._raise_system_error(api_desc)

		result = api_response
		print 'api call result>>>>>>>>>>>>>>>>>:',result
		"""
			TODO:
				记录微信api调用记录
		"""

		# try:
		# 	#watchdog_info('call weixin api: {} , result:{}'.format(api_instance_class.__class__.__name__, result))

		# 	from weixin.message.message_handler.tasks import record_call_weixin_api
		# 	if hasattr(result, 'errcode'):
		# 		success = False
		# 		#watchdog_error('call weixin api: {} , result:{}'.format(api_instance_class.__class__.__name__, result))	
		# 	else:
		# 		success = True
		# 	record_call_weixin_api.delay(api_instance_class.__class__.__name__, success)
		# except:
		# 	pass
		
		if hasattr(result, 'errcode'):
			try:
				result_code = int(result['errcode'])
			except:
				result_code = result['errcode']
			
			# if result_code == errorcodes.API_NOT_AUTHORIZED_CODE:
			# 	mpuser_access_token = weixin_api.mpuser_access_token
			# 	#mpuser_access_token.is_active = False
			# 	mpuser_access_token.is_certified = False
			# 	mpuser_access_token.save()
			
			# try:
			# 	if result_code == errorcodes.INVALID_ACCESS_TOKEN_CODE or result_code == errorcodes.ILLEGAL_ACCESS_TOKEN_CODE or result_code == errorcodes.ACCESS_TOKEN_EXPIRED_CODE:
			# 		update_access_token(weixin_api.mpuser_access_token)	
			# except:
			# 	notify_message = u"weixin_api update_access_token error {}".format(unicode_full_stack())
			# 	watchdog_error(notify_message)

		if weixin_api._is_error_response(api_response):
			# if weixin_api._is_error_dueto_access_token(api_response):
			# 	if api_instance_class.is_retry(agrs):
			# 		weixin_api._raise_request_error(api_response, api_desc, weixin_api.mpuser_access_token.mpuser.owner_id)
			# 	else:
			# 		#如果由于access_token的问题，那么先更新access_token后重试
			# 		if (update_access_token(weixin_api.mpuser_access_token)):
			# 			return _call_api(*agrs)
			# 		else:
			# 			weixin_api._raise_request_error(api_response, api_desc, weixin_api.mpuser_access_token.mpuser.owner_id)
			# else:
			#weixin_api._raise_request_error(api_response, api_desc, weixin_api.mpuser_access_token.mpuser.owner_id)
			weixin_api._raise_request_error(api_response, api_desc)
			
		return api_instance_class.parse_response(api_response)

	return _call_api

class WeixinApi(object):
	def __init__(self, mpuser_access_token, weixin_http_client):
		if mpuser_access_token is None or mpuser_access_token.access_token is None:
			raise ValueError(u'缺少授权信息')

		#mpuser = mpuser_access_token.mpuser
		# if not mpuser.is_service or not mpuser.is_certified:
		# 	raise ValueError(u'只有授权过的服务号才可以使用Api')

		# if not mpuser_access_token.is_active:
		# 	raise ValueError(u'授权已经过期')			
		self.mpuser_access_token = mpuser_access_token
		self.weixin_http_client = weixin_http_client

	def __getattr__(self, name):
		if not name in api_settings.API_CLASSES.keys():
			raise ValueError(u'api_settings 里不存在该方法{}对应 api'.format(name))
		
		if not hasattr(self.__dict__, name):
			handler_path = api_settings.API_CLASSES[name]

			try:
				handler_module, handler_classname = handler_path.rsplit('.', 1)
			except ValueError:
				raise exceptions.ImproperlyConfigured('%s isn\'t a message handler module' % handler_path)
			from importlib import import_module
			try:
				module = import_module(handler_module)
			except ImportError, e:
			 	raise ValueError('Error importing message handler %s: "%s"' % (handler_module, e))

			try:
				handler_api_class = getattr(module, handler_classname)
			except:
				raise ValueError('u error class')

			try:
				api_class_instance = handler_api_class()
			except:
				raise ValueError('u class can not be instance')

			self.__dict__[name] = call_api(self, api_class_instance)

		return self.__dict__[name]		
		

	# def upload_media(self):
	# 	pass

	# def download_media(self):
	# 	pass

	def _notify_api_request_error(self, apierror, api_name='' ,user_id=0):
		notify_msg = u"微信api调用失败，api:{}\n错误信息:{}".format(api_name, apierror.__unicode__())
		watchdog.error(notify_msg,user_id=user_id)

	def _raise_request_error(self, response, api_name='' , user_id=0):
		error_response = WeixinErrorResponse(response)

		if error_response.errcode in (errorcodes.ILLEGAL_ACCESS_TOKEN_CODE, 
			errorcodes.ACCESS_TOKEN_EXPIRED_CODE, errorcodes.INVALID_ACCESS_TOKEN_CODE):
			#inactive_mpuser_access_token(self.mpuser_access_token)
			pass

		apierror = WeixinApiError(error_response)

		self._notify_api_request_error(apierror, api_name, user_id)

		#raise apierror

	def _raise_system_error(self, api_name='', user_id=0):
		system_error_response = build_system_exception_response()
		apierror = WeixinApiError(system_error_response)

		self._notify_api_request_error(apierror, api_name, user_id)

		#raise apierror

	def _is_error_response(self, response):
		if type(response) == dict:
			return response.get('errcode', errorcodes.SUCCESS_CODE) != errorcodes.SUCCESS_CODE
		else:
			return False

	def _is_error_dueto_access_token(self, response):
		if type(response) == dict:
			return response.get('errcode', errorcodes.SUCCESS_CODE) in (errorcodes.ILLEGAL_ACCESS_TOKEN_CODE, 
				errorcodes.ACCESS_TOKEN_EXPIRED_CODE, errorcodes.INVALID_ACCESS_TOKEN_CODE)
		else:
			return False		

import json
import urllib2

class WeixinHttpClient(object):
	def __init__(self):
		super(WeixinHttpClient, self).__init__()

	def get(self, url):
		weixin_response = urllib2.urlopen(url)
		try:
			return self._parse_response(weixin_response.read().decode('utf-8'))
		except:
			return self._parse_response(weixin_response.read())
		finally:
			if weixin_response:
				try:
					weixin_response.close()
				except:
					pass

	def post(self, url, post_param_json, is_for_form=False):
		if is_for_form:
			# 在 urllib2 上注册 http 流处理句柄
			register_openers()
			# 开始对文件 "DSC0001.jpg" 的 multiart/form-data 编码
			# "xx" 是参数的名字，一般通过 HTML 中的 <input> 标签的 name 参数设置
			# headers 包含必须的 Content-Type 和 Content-Length
			# datagen 是一个生成器对象，返回编码过后的参数
			#{"media": open("d://1.jpg", "rb")}
			datagen, headers = multipart_encode(post_param_json)
			# 创建请求对象
			request = urllib2.Request(url, datagen, headers)
			# 实际执行请求并取得返回
			weixin_response = urllib2.urlopen(request)#.read()

		else:
			req = urllib2.Request(url)
			opener = urllib2.build_opener()
			weixin_response = opener.open(req, json.dumps(post_param_json, ensure_ascii=False).encode('utf-8'))

		try:
			return self._parse_response(weixin_response.read().decode('utf-8'))
		finally:
			if weixin_response:
				try:
					weixin_response.close()
				except:
					pass

	def upload(self, url, upload_str_data):
		pass

	def download(self, url):
		pass

	def _parse_response(self, response_text):
		response_text = response_text.strip()

		if response_text.startswith(u'{') and response_text.endswith(u'}'):
			try:
				return decode_json_str(response_text)
			except:
				return response_text
		else:
			return response_text

weixin_http_client = WeixinHttpClient()
def weixin_api(mpuser_access_token):
	return WeixinApi(mpuser_access_token, weixin_http_client)