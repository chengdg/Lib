#coding: utf8

import eaglet.peewee as peewee
# from playhouse.db_url import connect
from eaglet.core.hack_peewee import connect
import settings
import datetime

DB = settings.DATABASES['default']
db = None

if DB['NAME']:
	DB_URL = '%s://%s:%s@%s/%s' % (DB['ENGINE'], DB['USER'], DB['PASSWORD'], \
		"%s:%s" % (DB['HOST'], DB['PORT']) if len(DB['PORT'])>0 else DB['HOST'], DB['NAME'])
	db = connect(DB_URL)
	db.connect()

#print(peewee.__version__)

class Model(peewee.Model):
	class Meta:
		database = db

	@classmethod
	def from_dict(cls, dict):
		if dict == None:
			return None
		#obj = cls.__new__(cls)
		obj = cls()
		for key, value in dict.items():
			try:
				setattr(obj, key, value)
			except AttributeError:
				pass
		return obj

	@classmethod
	def from_list(cls, list):
		objs = []
		for dict in list:
			#obj = cls.__new__(cls)
			obj = cls()
			for key, value in dict.items():
				setattr(obj, key, value)
			objs.append(obj)
		return objs

	def to_dict(self, *attrs):
		#columns = [field.get_attname() for field in self._meta.fields]
		result = {}
		for field in self._meta.get_fields():
			if isinstance(field, ForeignKey):
				result[field.name+'_id'] = self._data.get(field.name)
			else:
				result[field.name] = self._data.get(field.name)
		for attr in attrs:
			result[attr] = getattr(self, attr, None)
		return result


class IntegerField(peewee.IntegerField):

	def __init__(self, blank=False, db_index=False, **kwargs):
		kwargs['null'] = blank
		if db_index:
			kwargs['index'] = db_index
		super(IntegerField, self).__init__(**kwargs)


class CharField(peewee.CharField):

	def __init__(self, blank=False, db_index=False, **kwargs):
		kwargs['null'] = blank
		if db_index:
			kwargs['index'] = db_index
		super(CharField, self).__init__(**kwargs)


class TextField(peewee.TextField):
	pass

class BareField(peewee.BareField):
	pass

class BigIntegerField(peewee.BigIntegerField):
	pass

class PrimaryKeyField(peewee.PrimaryKeyField):
	pass

class FloatField(peewee.FloatField):
	pass

class DoubleField(peewee.DoubleField):
	pass

class DecimalField(peewee.DecimalField):
	pass

class DateField(peewee.DateField):

	def __init__(self, auto_now_add=False, auto_now=False, blank=False, **kwargs):
		if auto_now or auto_now_add:
			kwargs['default'] = datetime.datetime.now
		kwargs['null'] = blank
		super(DateField, self).__init__(**kwargs)


class DateTimeField(peewee.DateTimeField):

	def __init__(self, auto_now_add=False, auto_now=False, blank=False, **kwargs):
		if auto_now or auto_now_add:
			kwargs['default'] = datetime.datetime.now
		kwargs['null'] = blank
		super(DateTimeField, self).__init__(**kwargs)

class ForeignKey(peewee.ForeignKeyField):
	pass

class EmailField(CharField):
	pass

class BooleanField(peewee.BooleanField):
	pass

if __name__=="__main__":
	pass
