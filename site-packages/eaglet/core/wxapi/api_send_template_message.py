# -*- coding: utf-8 -*-

__author__ = 'paco bert'

import json
from eaglet.utils.url_helper import complete_get_request_url
import api_settings
from eaglet.core.wxapi.util import *
from custom_message import build_custom_message_json_str, TextCustomMessage

""""
	调用用户信息api:
	http请求方式: POST
	https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=ACCESS_TOKEN
	
	1.获得api请求地址

	2.获得请求结果  注：异常信息统交给WeixinApi

	3.格式化请求结果

	4.格式化post数据
	  {
           "touser":"OPENID",
           "template_id":"ngqIpbwh8bUfcSsECmogfXcV14J0tQlEpBO27izEYtY",
           "url":"http://weixin.qq.com/download",
           "topcolor":"#FF0000",
           "data":{
                   "first": {
                       "value":"您好，您已成功消费。",
                       "color":"#0A0A0A"
                   },
                   "keynote1":{
                       "value":"巧克力",
                       "color":"#CCCCCC"
                   },
                   "keynote2": {
                       "value":"39.8元",
                       "color":"#CCCCCC"
                   },
                   "keynote3":{
                       "value":"2014年9月16日",
                       "color":"#CCCCCC"
                   },
                   "remark":{
                       "value":"欢迎再次购买。",
                       "color":"#173177"
                   }
           }
       }
		
	发货通知：
		{{first.DATA}} 

		快递公司：{{delivername.DATA}}
		快递单号：{{ordername.DATA}}
		 {{remark.DATA}}

"""

DELIVER_MESSAGE = """{
           "touser":"%s",
           "template_id":"%s",
           "url":"%s",
           "topcolor":"%s",
           "data":{
                   "first": {
                       "value":"%s",
                       "color":"%s"
                   },
                   "delivername":{
                       "value":"%s",
                       "color":"%s"
                   },
                   "ordername": {
                       "value":"%s",
                       "color":"%s"
                   }
                   "remark":{
                       "value":"%s",
                       "color":"%s"
                   }
           }
       }

"""


SEND_MASS_MSG_URI = 'cgi-bin/message/template/send'
class WeixinTemplateMessageSendApi(object):
	# def __init__(self):
	# 	print(222222222222222222222222222222222)

	def get_get_request_url_and_api_info(self, mpuser_access_token=None, varargs=()):
		if len(varargs) >= 3 and len(varargs) == 0:
			raise ValueError(u'WeixinTemplateMessageSendApi.get_get_request_url error, param illegal')

		if mpuser_access_token is None:
			raise ValueError(u'WeixinTemplateMessageSendApi get_get_request_url_and_api_info：mpuser_access_token is None')
		return self._complete_weixin_api_get_request_url(mpuser_access_token), u'发送模板消息'

	def parse_response(self, api_response):
		return api_response

	###############################################################################
	#	args 参数：args =（sendto_openid, custom_msg_instance	
	###############################################################################
	def parese_post_param_json_str(self, args):
		if len(args) == 0:
			raise ValueError(u'WeixinTemplateMessageSendApi param MassMessage illegal')			

		return args[0]

	def request_method(self):
		return api_settings.API_POST

	def _complete_weixin_api_get_request_url(self, mpuser_access_token):
		param_dict = {}
		param_dict['access_token'] = mpuser_access_token.access_token
		return complete_get_request_url(
				api_settings.WEIXIN_API_PROTOCAL, 
				api_settings.WEIXIN_API_DOMAIN,
				SEND_MASS_MSG_URI,
				param_dict
				)

	def is_retry(self, args):
		if len(args) == 2:
			return True if args[1] is True else False
		return False