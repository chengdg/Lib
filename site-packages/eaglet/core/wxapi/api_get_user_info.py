# -*- coding: utf-8 -*-

__author__ = 'paco bert'

from eaglet.utils.url_helper import complete_get_request_url
import api_settings
from eaglet.core.wxapi.util import ObjectAttrWrapedInDict
""""
	调用用户信息api:
	http请求方式: GET
	https://api.weixin.qq.com/cgi-bin/user/info?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN

	1.获得api请求地址

	2.获得请求结果  注：异常信息统交给WeixinApi

	3.格式化请求结果
"""
USER_INFO_URL = "cgi-bin/user/info"

class WeixinUserInfo(ObjectAttrWrapedInDict):
	def __init__(self, src_dict):
		super(WeixinUserInfo, self).__init__(src_dict)

"""
	参数varargs ： (openid,lang),openid:微信对每个会员的唯一标识；lang：语言
"""
class WeixinUserApi(object):

	def get_get_request_url_and_api_info(self, mpuser_access_token=None, varargs=()):
		if len(varargs) ==0 or len(varargs) > 2:
			raise ValueError(u'WeixinUserInfo.get_get_request_url error, param illegal')

		if mpuser_access_token is None:
			raise ValueError(u'WeixinUserInfo get_get_request_url_and_api_info：mpuser_access_token is None')
		return self._complete_weixin_api_get_request_url(mpuser_access_token, varargs), u'获取用户信息 openid %s' % varargs[0]

	def parse_response(self, api_response):
		user_info = WeixinUserInfo(api_response)
		if hasattr(user_info, 'headimgurl'):
			pass
		else:
			user_info.headimgurl = ''
		return user_info

	def parese_post_param_json_str(self, *varargs):
		pass

	def request_method(self):
		return api_settings.API_GET

	def _complete_weixin_api_get_request_url(self, mpuser_access_token, varargs):
		param_dict = {}
		param_dict['access_token'] = mpuser_access_token.access_token
		param_dict['openid'] = varargs[0]
		param_dict['lang'] = 'zh_CN'
		return complete_get_request_url(
			api_settings.WEIXIN_API_PROTOCAL, 
			api_settings.WEIXIN_API_DOMAIN,
			USER_INFO_URL,
			param_dict
			)

	def is_retry(self, args):
		if len(args) == 2:
			return True if args[1] is True else False
		return False