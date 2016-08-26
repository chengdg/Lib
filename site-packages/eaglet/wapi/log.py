#coding:utf8
from __future__ import absolute_import

import settings
#from core.exceptionutil import full_stack

from eaglet.core.service.celery import task
import json
#from eaglet.wapi.logger.mongo_logger import MongoAPILogger
import logging
from eaglet.core.exceptionutil import full_stack


_wapi_logger = None

def morph_params(param):
	"""
	将`webapp_user`和`webapp_owner`变成`wid`和`woid`

	@todo to be optimized
	"""
	new_param = {}
	for key, value in param.items():
		if key == 'webapp_user':
			new_param['wid'] = param['webapp_user'].id
		elif key == 'webapp_owner':
			new_param['woid'] = param['webapp_owner'].id
		elif key == 'zipkin_client':
			pass
		else:
			new_param[key] = value

	return new_param


def param_to_text(param):
	"""
	将param转成JSON text，用于调试
	"""
	return json.dumps(morph_params(param))


@task(bind=True, max_retries=3)
def wapi_log(self, app, resource, method, params, time_in_s, status=0):
	"""
	记录WAPI信息，保存到mongo中
	"""
	try:
		if settings.WAPI_LOGGER_ENABLED:
			#update by bert delete MongAPILogger
			#global _wapi_logger
			# if _wapi_logger is None:
			# 	_wapi_logger = MongoAPILogger()
			# if settings.MODE == 'develop' or settings.MODE == 'test':
			logging.info("called WAPI (in {} s): {} {}/{}, param: {}".format(time_in_s, method, app, resource, param_to_text(params)))
			#return _wapi_logger.log(app, resource, method, morph_params(params), time_in_s, status)
		else:
			logging.info("called WAPI (in {} s): {} {}/{}, param: {}".format(time_in_s, method, app, resource, param_to_text(params)))
		return 'OK'
	except:
		logging.error("Failed to send wapi log, retrying.:Cause:\n{}".format(full_stack()))
		raise self.retry()
	return 'OK'
