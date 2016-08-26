# -*- coding: utf-8 -*-

APPRESOURCE2CLASS = dict()


class ResourceBase(type):
	def __new__(cls, name, bases, attrs):
		return super(ResourceBase, cls).__new__(cls, name, bases, attrs)

	def __init__(self, name, bases, attrs):
		if name == 'Resource':
			pass
		else:
			app_resource = '%s-%s' % (self.app, self.resource)
			print 'register inner resource: %s' % app_resource

			for key, value in self.__dict__.items():
				if hasattr(value, '__call__'):
					static_method = staticmethod(value)
					setattr(self, key, static_method)

			APPRESOURCE2CLASS[app_resource] = {
				'cls': self,
				'instance': None
			}

		super(ResourceBase, self).__init__(name, bases, attrs)


class Resource(object):
	__metaclass__ = ResourceBase
