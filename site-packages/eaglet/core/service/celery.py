# -*- coding: utf-8 -*-
#coding:utf8
from __future__ import absolute_import

import os
import sys
import logging

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_DIR)
from celery import Celery
from celery.utils.log import get_logger
import settings

logging.info("init celery")
app = Celery('apiserver')
logging.info("loaded `celeryconfig`")
app.config_from_object('eaglet.core.service.celeryconfig')
app.autodiscover_tasks(lambda: settings.INSTALLED_TASKS)
celery_app  = app
task = celery_task = app.task


WEAPP_TASKS_PREFIX_LEN = len(os.path.realpath( os.path.join(settings.PROJECT_HOME,'..'))) + 1
celery_app  = app
task = celery_task = app.task
def celery_logger(name = None):
    if name:
        return get_logger(name)
    
    f = None
    if hasattr(sys, '_getframe'): 
        f = sys._getframe(1)
    else:
        try:
            raise Exception
        except:
            f = sys.exc_info()[2].tb_frame.f_back
    task = 'celery'
    if hasattr(f, "f_code"):
        co = f.f_code
        task = co.co_filename
        task = task[WEAPP_TASKS_PREFIX_LEN:task.rfind('.')].replace(os.sep,'.')
        task = '%s.%s' % (task, co.co_name)
    return get_logger(task)