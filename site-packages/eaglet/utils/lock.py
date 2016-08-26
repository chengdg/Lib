# -*- coding: utf-8 -*-
"""
使用redis构建的锁

"""
import functools
import math
import time
import uuid
import logging
import redis

from eaglet.core.cache.utils import r
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog

DEFAULT_CONN = r    # 默认连接
DEFAULT_ACQUIRE_DELAY = 0.001   # 默认申请锁尝试时间时的延迟，单位秒
DEFAULT_TIMEOUT = 30  # 默认锁超时时间，单位秒
DEFAULT_ACQUIRE_TIME = 0    # 默认申请锁尝试时间，单位秒

try:
	from settings import REGISTERED_LOCK_NAMES
except ImportError as e:
	logging.info('RedisLock Warning: No REGISTERED_LOCK_NAMES in settings')


# Todo EVALSHA命令节省带宽
UNLOCK_SCRIPT = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end"""


def get_wapi_lock(lockname, lock_timeout=1):
	try:
		conn = DEFAULT_CONN
		identifier = '1'
		lockname = 'lk:' + lockname
		lock_timeout = int(math.ceil(lock_timeout))
		if conn.set(name=lockname, value=identifier, nx=True, ex=lock_timeout):
			return identifier
		else:
			return False
	except:
		watchdog.alert(unicode_full_stack())
		return True


class RedisLock(object):
	"""
	redis锁
	Examples:
		redis_lock = RedisLock()
		redis_lock.lock({'name': REGISTERED_LOCK_NAMES['coupon_lock'], 'resource': str(purchase_info.coupon_id)})
		redis.unlock()
	"""

	def __init__(self):
		self.__conn = DEFAULT_CONN
		self.__identifier = None
		self.__redis_error = False
		self._redis_lock_key = None
		self.acquired_lock = False

	def lock(self, lock_name_and_resource, lock_timeout=DEFAULT_TIMEOUT, acquire_time=DEFAULT_ACQUIRE_TIME):
		try:
			registerer_lock_names = REGISTERED_LOCK_NAMES.values()
			__prefix = REGISTERED_LOCK_NAMES['__prefix']

			conn = self.__conn
			lock_name = lock_name_and_resource['name']
			assert lock_name in registerer_lock_names, '{} is not in REGISTERED_LOCK_NAME'.format(lock_name)
			self._redis_lock_key = __prefix + lock_name + lock_name_and_resource['resource']
			self.__identifier = str(uuid.uuid4())

			if acquire_time > 0:
				end = time.time() + acquire_time
				while time.time() < end:
					if conn.set(name=self._redis_lock_key, value=self.__identifier, nx=True, ex=lock_timeout):
						return True
					time.sleep(DEFAULT_ACQUIRE_DELAY)
			else:
				return conn.set(name=self._redis_lock_key, value=self.__identifier, nx=True, ex=lock_timeout)
		except BaseException as e:
			self.__log_exception(e)
			self.__redis_error = True
			return True

	def unlock(self):
		conn = self.__conn
		try:
			conn.eval(UNLOCK_SCRIPT, 1, self._redis_lock_key, self.__identifier)
			return True
		except BaseException as e:
			self.__log_exception(e)
			return False

	def __log_exception(self, e=BaseException):
		if isinstance(e, redis.exceptions.RedisError):
			exception_type = 'redis_error'
		else:
			exception_type = 'other'
		watchdog.alert(
			'redis_lock_error:type:{}.\nunicode_full_stack:{}'.format(exception_type, unicode_full_stack()))
		self.__redis_error = True
		return True


def wapi_lock():
	"""
	wapi接口锁装饰器，锁定一个用户同时只能访问一个接口一次
	Examples:
		class AOrder(api_resource.ApiResource):
			app = 'mall'
			resource = 'order'

			@param_required(['ship_name', 'ship_address', 'ship_tel', 'order_type', 'xa-choseInterfaces'])
			@wapi_lock()
			def put(args):
				...
	"""
	def decorator_func(func):
		redis_lock = RedisLock()

		def wrapper_func(*args, **kwargs):
			# 申请锁
			if not redis_lock.lock({
				'name': REGISTERED_LOCK_NAMES['wapi_lock'],
				'resource': args[0]['wapi_id'] + str(args[0]['webapp_user'].id)
			}, lock_timeout=3):
				reason_dict = {
					"is_success": False,
					"msg": u'请勿连续点击',
					"type": "coupon"  # 兼容性type
				}
				return 500, {'detail': [reason_dict]}

			retval = func(*args, **kwargs)
			# 释放锁
			redis_lock.unlock()

			return retval

		return wrapper_func

	return decorator_func


class MRedisLock(object):
	"""
	@warning 别用
	一次建立多个锁并解多个锁
	Examples:
	def __acquire_create_order_lock_by_purchase_info(self, purchase_info):
		locked_resource = []
		webapp_user_id = self.context['webapp_user'].id
		redis_lock = RedisLock()
		if purchase_info.coupon_id:
			# 优惠券锁
			locked_resource.append({'name': REGISTERED_LOCK_NAMES['coupon_lock'], 'resource': purchase_info.coupon_id})
		if purchase_info.order_integral_info or purchase_info.group2integralinfo:
			locked_resource.append({'name': REGISTERED_LOCK_NAMES['integral_lock'], 'resource': webapp_user_id})
		if purchase_info.wzcard_info:
			for wzcard in purchase_info.wzcard_info:
				locked_resource.append({'name': REGISTERED_LOCK_NAMES['wz_card_lock'], 'resource': wzcard['card_name']})

		return redis_lock.mlock(locked_resource), redis_lock


	def __release_create_order_lock(self):
		self.context['create_order_lock'].munlock()
	"""

	def __init__(self):
		self.__conn = DEFAULT_CONN
		self.__redis_error = False
		self.__redis_locks = {}
		self.redis_lock_names = []
		self.acquired_lock = False

	def mlock(self, lock_names_and_resources, timeout=None):
		try:
			registerer_lock_names = REGISTERED_LOCK_NAMES.values()
			__prefix = REGISTERED_LOCK_NAMES['__prefix']
			timeout = DEFAULT_TIMEOUT if not timeout else timeout
			conn = self.__conn
			for name_and_resource in lock_names_and_resources:
				lock_name = name_and_resource['name']
				assert lock_name in registerer_lock_names, '{} is not in REGISTERED_LOCK_NAME'.format(lock_name)
				redis_lock_name = __prefix + lock_name + name_and_resource['resource']
				self.__redis_locks[redis_lock_name] = str(uuid.uuid4())

			is_get_locks = conn.msetnx(self.__redis_locks)

			if is_get_locks:
				pipe = conn.pipeline(transaction=False)
				for redis_lock_name in self.redis_lock_names:
					pipe.expire(redis_lock_name, timeout)
				self.acquired_lock = True
				return True
			else:
				return False
		except BaseException as e:
			self.__log_exception(e)
			self.__redis_error = True
			return True

	def munlock(self):
		try:
			if not self.acquired_lock:
				return

			conn = self.__conn
			pipe = conn.pipeline(transaction=False)
			for key, value in self.__redis_locks.items():
				pipe.eval(UNLOCK_SCRIPT, 1, key, value)

			result = pipe.execute()

		except BaseException as e:
			self.__log_exception(e)
			self.__redis_error = True
			return True

	def __log_exception(self, e=BaseException):
		if isinstance(e, redis.exceptions.RedisError):
			exception_type = 'redis_error'
		else:
			exception_type = 'other'
		watchdog.alert(
			'redis_lock_error:type:{}.\nunicode_full_stack:{}'.format(exception_type, unicode_full_stack()))
		self.__redis_error = True
		return True

		# def lock(self, acquire_time=0, lock_timeout=5):
		# 	"""
		# 	申请锁
		# 	@param acquire_time: 请求建锁的最长时间
		# 	@param lock_timeout:
		# 	@return:
		# 	"""
		# 	try:
		# 		identifier = str(uuid.uuid4())
		# 		lock_timeout = int(math.ceil(lock_timeout))
		# 		conn = self.__conn
		# 		end = time.time() + acquire_time
		# 		while time.time() < end:
		# 			if conn.set(name=self.__lock_key, value=identifier, nx=True, ex=lock_timeout):
		# 				return identifier
		# 			elif not conn.ttl(self.__lock_key, lock_timeout):
		# 				conn.expire(self.__lock_key, lock_timeout)
		# 			time.sleep(DEFAULT_ACQUIRE_DELAY)
		# 		return False
		# 	except BaseException as e:
		# 		if isinstance(e, redis.exceptions.RedisError):
		# 			exception_type = 'redis_error'
		# 		else:
		# 			exception_type = 'other'
		# 		watchdog.alert(
		# 			'redis_lock_error:type:{}.\nunicode_full_stack:'.format(exception_type, unicode_full_stack()))
		# 		self.__redis_error = True
		# 		return True

		# def release(self):
		# 	"""
		# 	释放锁。基本语句：pipe.delete(self.__lock_name)
		# 	使用事务的情景示例:创建锁k,但是pipe.get()到delete之间恰巧key过期，设置了新的锁，事务保证了不会误删新的锁。
		# 	@return:
		# 	"""
		# 	try:
		# 		if self.__redis_error:
		# 			return True
		# 		else:
		# 			conn = self.__conn
		# 			pipe = conn.pipeline(transaction=True)
		#
		# 			while True:
		# 				try:
		# 					pipe.watch(self.__lock_key)
		# 					if pipe.get(self.__lock_key) == self.identifier:
		# 						pipe.multi()
		# 						pipe.delete(self.__lock_key)
		# 						pipe.execute()
		# 						return True
		# 					pipe.unwatch()
		# 					break
		# 				except redis.exceptions.WatchError:
		# 					pass
		# 			return False
		# 	except BaseException as e:
		# 		if isinstance(e, redis.exceptions.RedisError):
		# 			exception_type = 'redis_error'
		# 		else:
		# 			exception_type = 'other'
		# 		watchdog.alert(
		# 			'redis_lock_error:type:{}.\n unicode_full_stack:'.format(exception_type, unicode_full_stack()))
		# 		self.__redis_error = True
		# 		return True
		# def lock2(self):
		# 	"""
		# 	申请锁，lua脚本版
		# 	"""
		# 	pass
		#
		#
		# def release2(self):
		# 	"""
		# 	释放锁，lua脚本版
		# 	@return:
		# 	"""
		# 	conn = self.__conn
		# 	try:
		# 		conn.eval(RELEASE_SCRIPT, 1, self.__lock_key, self.identifier)
		# 		return True
		# 	except:
		# 		return False
		#
		#
		# def __unlock(self, key):
		# 	"""
		# 	释放锁，lua脚本版
		# 	@return:
		# 	"""
		# 	conn = self.__conn
		# 	try:
		# 		conn.eval(RELEASE_SCRIPT, 1, self.__lock_key, self.identifier)
		# 		return True
		# 	except:
		# 		return False
		#
		#
		# @property
		# def real_lock_name(self):
		# 	return self.__lock_key

		# def wapi_lock4(function_to_decorate):
		# 	def wrapper(*args, **kw):
		# 		# Calling your function
		# 		output = function_to_decorate(*args, **kw)
		# 		# Below this line you can do post processing
		# 		print "In Post Processing...."
		#
		# 	return wrapper
		#
		#
		# def wapi_lock2(args):
		# 	def decorator(func):
		# 		@functools.wraps(func)
		# 		def wrapper(*args,**kw):
		# 			print('------in decorator',args,kw)
		# 			return func(*args,**kw)
		# 		return wrapper
		# 	return decorator()
		#
		#
		# def wapi_lock1(func):
		# 	# @functools.wraps(func)
		# 	def wrapper(*args, **kw):
		# 		print('call %s():', func.__name__)
		# 		print('------in decorator', args, kw)
		# 		return func(*args, **kw)
		# 	print('111122222222222222222')
		# 	return wrapper
