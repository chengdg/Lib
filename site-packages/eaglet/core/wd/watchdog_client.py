# -*- coding: utf-8 -*-

import uuid
import json
import logging
from eaglet.core.exceptionutil import unicode_full_stack


class WatchdogClient(object):
    """docstring for WatchdogClient"""
    def __init__(self, service_name):
        super(WatchdogClient, self).__init__()
        self.index = 0
        self.msg = '[watchdog:python]'
        self.service_name = service_name
        self.type = "api"
        self.id = str(uuid.uuid1())

    def getMessge(self, message, user_id, type=None):
        self.index += 1
        if type:
            self.type =  type
        
        try:
            err_msg = ''
            json.dumps(message)
        except:
            message = str(message)
            err_msg = unicode_full_stack()

        message = {
            "msg": self.msg,
            "service_name": self.service_name,
            "type": self.type,
            "uuid": self.id,
            "index":  self.index,
            "message": message,
            "user_id": user_id,
            "json_error": err_msg
        }
        return json.dumps(message)