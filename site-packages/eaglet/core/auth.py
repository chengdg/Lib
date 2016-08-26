# -*- coding: utf-8 -*-

class UserProfile(object):
	"""
	模拟webapp_owner_user_profile，用于cache调用
	"""
	def __init__(self, webapp_id=0, user_id=0):
		self.webapp_id = webapp_id
		self.user_id = user_id


class WebAppUser(object):
	def __init__(self, id):
		self.id = id
		self.integral_info = {
			'count': 0,
			'usable_integral_percentage_in_order': 1,
			'count_per_yuan': 1,
			'usable_integral_or_conpon': 0
		}
		self.coupons = []
		self.ship_info = None


class WebAppOwnerInfo(object):
	def __init__(self, id):
		self.member_grades = []


class DummyRequest(object):
	"""
	模拟Django Request
	"""
	def __init__(self):
		pass

class DummyModel(object):
	"""
	模拟数据库Model
	"""

	def __init__(self):
		pass
