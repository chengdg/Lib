# -*- coding: utf-8 -*-

__author__ = 'chuter'

from .weixin_api import WeixinApi, WeixinHttpClient

weixin_http_client = WeixinHttpClient()

def get_weixin_api(mpuser_access_token):
	return WeixinApi(mpuser_access_token, weixin_http_client)