#coding: utf8
"""@package weapp.webapp.handlers.test
event_handler_util的测试脚本

"""
from __future__ import absolute_import

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from db.account.models import User, UserProfile
from db.member.models import Member, SocialAccount, MemberHasSocialAccount, WebAppUser
from core.watchdog.utils import *
user = User.get(username='jobs')
user_id = user.id
user_profile = UserProfile.get(user=user)
user_profile_id = user_profile.id
social_account = SocialAccount.get(webapp_id=user_profile.webapp_id, openid='bill_jobs')
member = MemberHasSocialAccount.get(account=social_account).member
webapp_user = WebAppUser.get(webapp_id=user_profile.webapp_id, member_id=member.id)

def test_local_handle():
	# 测试本地情况的handle
	from core.handlers.event_handler_util import handle
	args = {
		'GET': {'get1':'value1', 'get2':'value2'},
		'COOKIES': '<cookie>',
		'method': 'GET',
		'POST': {'post1': 'value1', 'post2': 'value2'},
		'data': {
			'app_id': '123',
			'user_id': user_id,
			'webppuser_id': webapp_user.id,
			'user_profile_id': user_profile_id,
			'social_account_id': social_account.id,
			'member_id': member.id,
			'is_user_from_mobile_phone': False,
			'is_user_from_weixin': False,
			},
		'visit_data': '<visit_data>'
	}
	result = handle(args, 'example')
	
	watchdog_alert('result: {}'.format(result))
	watchdog_error('result: {}'.format(result))
	watchdog_info('result: {}'.format(result))
	print('result: {}'.format(result))

if __name__=="__main__":
	test_local_handle()

