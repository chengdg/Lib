# # -*- coding: utf-8 -*-
# """
# 需要 pymongo 2.5
# ```
# pip install "pymongo==2.5"
# ```

# """

# from datetime import datetime
# import json

# import settings

# from pymongo import Connection

# """
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weapp.settings")
# """

# class MongoAPILogger(object):
# 	"""
# 	搜集WAPI信息的logger
# 	"""

# 	def __init__(self):
# 		self.connection = None
# 		self.db = None
# 		self.connect(settings.WAPI_LOGGER_SERVER_HOST, settings.WAPI_LOGGER_SERVER_PORT, settings.WAPI_LOGGER_DB)

# 	def connect(self, host, port, db):
# 		self.connection = Connection(host, port)
# 		self.db = self.connection[db]

# 	def get_now(self):
# 		return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 	def params_to_str(self, params):
# 		"""
# 		将params转成字符串
# 		"""
# 		try:
# 			str = json.dumps(params)
# 		except:
# 			# params有时是QueryDict对象
# 			str = '{}'.format(params)
# 		return str

# 	def log(self, app, resource, method, params, time_in_s, status=0):
# 		"""
# 		记录WAPI的信息
# 		"""
# 		now = self.get_now()
# 		record = {
# 			'api': '%s/%s' % (app, resource),
# 			'method': method,
# 			#'params': '{}'.format(params),
# 			'params': self.params_to_str(params),
# 			'at': now,
# 			'time_s': time_in_s,
# 			'status': status
# 		}
# 		self.db.log.insert(record)
# 		return now


# if __name__=="__main__":
# 	log = MongoAPILogger()
# 	log.log("dev", "test", {"param1":"hello", "param2":"world"}, 1)
