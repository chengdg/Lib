# -*- coding: utf-8 -*-
import json
__author__ = 'bert'

class ObjectAttrWrapedInDict(dict):
	def __init__(self, src_dict):
		if src_dict:
			for key, value in src_dict.items():
				setattr(self, key, value)

	def __getattribute__(self, key):
		if not hasattr(self, key):
			return None

		return dict.__getattribute__(self, key)
