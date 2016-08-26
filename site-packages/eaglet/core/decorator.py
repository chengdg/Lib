# -*- coding: utf-8 -*-
import warnings

class cached_property(object):
	"""
	Decorator that converts a method with a single self argument into a
	property cached on the instance.
	"""
	def __init__(self, func):
		self.func = func

	def __get__(self, instance, type=None):
		if instance is None:
			return self
		res = instance.__dict__[self.func.__name__] = self.func(instance)
		return res


def deprecated(func):
	"""This is a decorator which can be used to mark functions
	as deprecated. It will result in a warning being emmitted
	when the function is used."""
	def newFunc(*args, **kwargs):
		warnings.warn("Call to deprecated function %s." % func.__name__,
					  category=DeprecationWarning)
		return func(*args, **kwargs)
	newFunc.__name__ = func.__name__
	newFunc.__doc__ = func.__doc__
	newFunc.__dict__.update(func.__dict__)
	return newFunc
