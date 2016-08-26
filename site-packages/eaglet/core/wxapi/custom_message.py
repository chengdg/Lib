
# -*- coding: utf-8 -*-

__author__ = 'bert'

"""
客服消息

当用户主动发消息给公众号的时候（包括发送信息、点击自定义菜单click事件、订阅事件、
扫描二维码事件、支付成功事件、用户维权），微信将会把消息数据推送给开发者，开发者
在一段时间内（目前修改为48小时）可以调用客服消息接口，通过POST一个JSON数据包来发
送消息给普通用户，在48小时内不限制发送次数。此接口主要用于客服等有人工消息处理环
节的功能，方便开发者为用户提供更加优质的服务。 

具体文档参见：
http://mp.weixin.qq.com/wiki/index.php?title=%E5%8F%91%E9%80%81%E5%AE%A2%E6%9C%8D%E6%B6%88%E6%81%AF#.E5.8F.91.E9.80.81.E5.9B.BE.E6.96.87.E6.B6.88.E6.81.AF

微信中包含了6种类型的消息：
文本消息，图片消息，语音消息，视频消息，音乐消息，图文消息
"""

import json

#
# 根据客服消息实例，和接收该消息的openid，构建完整的json格式的客服消息字符串
# 例如：
# 文本消息示例：
# {
#    "touser":"OPENID",
#    "msgtype":"text",
#    "text":
#    {
#         "content":"Hello World"
#    }
# }
#
# 如果传入的参数类型非法会直接返回None
#
def build_custom_message_json_str(openid_send_to, custom_message_instance):
	if openid_send_to is None or custom_message_instance is None:
		return None

	#认为具有msg_type属性和get_msg_filed_dict方法的实例被认为
	#是客服消息类型

	if not hasattr(custom_message_instance, 'msg_type'):
		return None

	if not hasattr(custom_message_instance, 'get_msg_filed_dict'):
		return None

	msg_full_json = {}
	msg_full_json['touser'] = openid_send_to
	msg_full_json['msgtype'] = custom_message_instance.msg_type
	msg_full_json[custom_message_instance.msg_type] = custom_message_instance.get_msg_filed_dict()
	return json.dumps(msg_full_json)

class TextCustomMessage(object):
	msg_type = "text"

	def __init__(self, content):
		if content is None:
			raise ValueError(u"文本消息消息内容不能为空")

		content = content.strip()
		if len(content) == 0:
			raise ValueError(u"文本消息消息内容不能为空")			

		self.content = content		

	def get_msg_filed_dict(self):
		return {
			"content" : self.content
		}

class ImageCustomMessage(object):
	msg_type = "image"

	def __init__(self, media_id):
		if media_id is None:
			raise ValueError(u"图片消息的media_id不能为空")

		if len(media_id) == 0:
			raise ValueError(u"图片消息的media_id不能为空")

		self.media_id = media_id

	def get_msg_filed_dict(self):
		return {
			"media_id" : self.media_id
		}

class VoiceCustomMessage(object):
	msg_type = "voice"

	def __init__(self, media_id):
		if media_id is None:
			raise ValueError(u"语音消息的media_id不能为空")

		if len(media_id) == 0:
			raise ValueError(u"语音消息的media_id不能为空")

		self.media_id = media_id

	def get_msg_filed_dict(self):
		return {
			"media_id" : self.media_id
		}

# 文本消息示例：
#{
#    "touser":"OPENID",
#    "msgtype":"news",
#    "news":{
#        "articles": [
#         {
#             "title":"Happy Day",
#             "description":"Is Really A Happy Day",
#             "url":"URL",
#             "picurl":"PIC_URL"
#         },
#         {
#             "title":"Happy Day",
#             "description":"Is Really A Happy Day",
#             "url":"URL",
#             "picurl":"PIC_URL"
#         }
#         ]
#    }
#}
class NewsCustomMessage(object):
	msg_type = "news"

	def __init__(self, articles):
		if articles is None:
			raise ValueError(u"图文消息消息内容不能为空")

		if len(articles) == 0:
			raise ValueError(u"图文消息消息内容不能为空")			

		self.articles = articles		

	def get_msg_filed_dict(self):
		return {
			"articles" : self.articles
		}