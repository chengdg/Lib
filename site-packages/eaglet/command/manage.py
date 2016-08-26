# -*- coding: utf-8 -*-


import os
import sys

def load_eaglet_command(command):
    module_name = 'eaglet.command.%s' % command
    try:
        print 'load eaglet command: ', module_name
        module = __import__(module_name, {}, {}, ['*',])
        return module
    except Exception:
        return None

def load_local_command(command):
    module_name = 'commands.%s' % command
    try:
        print 'load local command: ', module_name
        module = __import__(module_name, {}, {}, ['*',])
        return module
    except Exception:
        return None

def run_command(command):
    command_module = load_eaglet_command(command)
    if not command_module:
        command_module = load_local_command(command)

    if not command_module:
        print 'no command named: ', command
    else:
        instance = getattr(command_module, 'Command')()
        try:
            instance.handle(*sys.argv[2:])
        except TypeError, e:
            print '[ERROR]: wrong command arguments, usages:'
            print instance.help

# if __name__ == "__main__":
#     command = sys.argv[1]
#     target_py = '%s.py' % command
#     commands_dir = './commands'
#     found_command = False
#     import os
#     for f in os.listdir(commands_dir):
#         if os.path.isfile(os.path.join(commands_dir, f)):
#             if f == target_py:
#                 found_command = True
#                 module_name = 'commands.%s' % command
#                 module = __import__(module_name, {}, {}, ['*',])
#                 instance = getattr(module, 'Command')()
#                 try:
#                     instance.handle(*sys.argv[2:])
#                 except TypeError, e:
#                     print '[ERROR]: wrong command arguments, usages:'
#                     print instance.help

#     if not found_command:
#         print 'no command named: ', command
