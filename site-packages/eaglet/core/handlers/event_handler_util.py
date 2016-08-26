# -*- coding: utf-8 -*-
"""@package webapp.handlers.event_handler_util
与service有关的接口

 * handle(request, event)：向原来的消息队列中添加消息

@todo 将service调用相关的函数移到services中。

"""
from __future__ import absolute_import
import time
from datetime import datetime
import urlparse

import settings
from core.service import celery
from core.service import celeryconfig
from core.watchdog.utils import watchdog_fatal

#if settings.MODE == 'develop' and celeryconfig.CELERY_ALWAYS_EAGER:
if celeryconfig.CELERY_ALWAYS_EAGER:
	print("CELERY_ALWAYS_EAGER=True, use 'services.celery.send_task_test' instead")
	from .celery_util import send_task_test as send_task
else:
	from celery.execute import send_task

import redis
redis_cli = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_SERVICE_DB)

def extract_data(request, extra_data={}):
	request_url = request.get_full_path()
	get = {}
	
	query = urlparse.urlparse(request.get_full_path()).query
	for key,value in urlparse.parse_qs(query).items():
		get[key] = value[0]
	cookies = {}
	cookies.update(request.COOKIES)
	if hasattr(request, 'context_dict'):
		context_dict = request.context_dict
	else:
		context_dict = None

	post = {}
	post.update(request.POST)
	data = {
		'full_path': request.get_full_path(),
		'url': request_url,
		'method': request.method,
		'GET': get,
		'POST': post,
		'COOKIES': cookies,
		'visit_data': datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"),
		'context_dict': context_dict,
		'data': {
			'app_id': request.app.id if (hasattr(request, 'app') and request.app) else -1,
			'user_id': request.user.id if request.user.is_authenticated() else -1,
			'social_account_id': request.social_account.id if (hasattr(request, 'social_account') and request.social_account) else -1,
			'member_id': request.member.id if (hasattr(request, 'member') and request.member) else -1,
			'is_user_from_mobile_phone': request.user.is_from_mobile,
			'is_user_from_weixin': request.user.is_from_weixin,
			'user_profile_id': request.user_profile.id if request.user_profile else -1,
			'webppuser_id': request.webapp_user.id if (hasattr(request, 'webapp_user') and request.webapp_user) else -1
		},
		'event_specific_data': extra_data
	}
	return data

EVENT_FILTER = set(['page_visit', 'shared_url_page_visit'])

def ensure_redis():
	try:
		redis_cli.ping()
		return redis_cli
	except:
		try:
			redis_cli = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_SERVICE_DB)
			redis_cli.ping()
			return redis_cli
		except:
			return None

	return None


"""
注册event：在 REGISTERED_EVENTS 中添加event和对应service函数全名(包括包名的)。
"""
REGISTERED_EVENTS = {
	#'page_visit': 'services.page_visit_service.tasks.record_page_visit',
	#'post_save_order': 'services.post_save_order_service.tasks.post_save_order',
	#'shared_url_page_visit': 'services.shared_url_page_visit_service.tasks.shared_url_page_visit',
	#'post_pay_order': 'services.post_pay_order_service.tasks.post_pay_order',
	#'oauth_shared_url': 'services.oauth_shared_url_service.tasks.oauth_shared_url',
	'example': 'services.example_service.tasks.example_log_service',
	#'finish_promotion': 'services.finish_promotion_service.tasks.finish_promotion',
	#'start_promotion': 'services.start_promotion_service.tasks.start_promotion',
	#'cancel_order': 'services.cancel_order_service.tasks.cancel_order',
}


def handle(request, event):	
	"""
	“调用”services的统一接口

	@param request 如果是Request对象，需要包括event_data；也可以是dict()对象，直接作为event_data。

	"""
	if hasattr(request, 'event_data'):
		event_data = request.event_data
	else:
		event_data = request
	result = None

	if settings.EVENT_DISPATCHER == 'dummy':
		print("found sepecial event '{}'".format(event))
		return result

	if celeryconfig.CELERY_ALWAYS_EAGER and REGISTERED_EVENTS.has_key(event):
		# 如果event是测试的service，以Celery方式处理
		task_name = REGISTERED_EVENTS[event]
		print("found sepecial event '{}'".format(event))
		result = send_task(task_name, args=[None, event_data])
		print("called service: name:'{}', result:{}".format(task_name, result))
	else:
		from services import service_manager
		if hasattr(request, 'event_data'):
			if settings.EVENT_DISPATCHER == 'local':
				# 本地模式：直接调用service函数
				service_manager.call_service(event, request.event_data)
			elif settings.EVENT_DISPATCHER == 'redis':
				is_processed = False
				# 如果没有处理，则用老的方式处理event
				if not is_processed:
					redis_cli = ensure_redis()
					if redis_cli:
						# 将request.event_data数据存入redis
						if event in EVENT_FILTER:
							redis_event = '%s_%s' % (event, str(int(time.time() * 1000)))
							send_message_to_redis(redis_event, request.event_data)
						else:
							redis_cli.rpush(event, request.event_data)
					else:
						notify_msg = u"redis服务不能访问, %s:%s:%s" % (settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_SERVICE_DB)
						watchdog_fatal(notify_msg)
						service_manager.call_service(event, request.event_data)
	return result

def send_message_to_redis(event, event_data):
	try:
		redis_cli.set(event, event_data)
	except:
		redis_cli.set(event, event_data)
