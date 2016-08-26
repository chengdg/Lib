#
#
#

# -*- coding: utf-8 -*-

class BaseCommand(object):
    def handle(self):
        raise RuntimeError('you muse extend BaseCommand and overwrite handle method')