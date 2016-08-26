# -*- coding: utf-8 -*-

from optparse import make_option
from datetime import datetime
import errno
import os
import re
import sys
import socket

import six
import settings
#from django.core.management.base import BaseCommand, CommandError
#from django.core.servers.basehttp import run, get_internal_wsgi_application
from eaglet.utils import autoreload
from eaglet.utils.command import BaseCommand
#from django.utils import six

naiveip_re = re.compile(r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""", re.X)
DEFAULT_PORT = "8000"


class Command(BaseCommand):
    args = '[optional port number, or ipaddr:port]'

    def get_handler(self, *args, **options):
        """
        Returns the default WSGI handler for the runner.
        """
        return get_internal_wsgi_application()

    def handle(self, *args, **options):
        if not args:
            raise RuntimeError('Usage is runserver %s' % self.args)

        self.addr = args[0]
        if len(args) > 1:
            self.port = args[1]
        else:
            self.port = DEFAULT_PORT
        self.stdout = sys.stdout
        self.run(*args, **options)

    def run(self, *args, **options):
        """
        Runs the server, using the autoreloader if needed
        """
        autoreload.main(self.inner_run, args, options)

    def inner_run(self, *args, **options):
        import falcon
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'

        now = datetime.now().strftime('%B %d, %Y - %X')
        if six.PY2:
            now = now.decode('utf-8')

        self.stdout.write((
            "\n\n*************************************************************\n"
            "          Falcon API Server version %(version)s\n\n"
            " %(started_at)s\n"
            " Starting development server at http://%(addr)s:%(port)s/\n"
            " Quit the server with %(quit_command)s.\n"
            "*************************************************************\n"
        ) % {
            "started_at": now,
            "version": falcon.version.__version__,
            "addr": '%s' % self.addr,
            "port": self.port,
            "quit_command": quit_command,
        })

        try:
            from wsgiref import simple_server
            from .. import apps
            wsgi_application = apps.create_app()

            if settings.DEV_SERVER_MULTITHREADING:
                from SocketServer import ThreadingMixIn
                class ThreadingWSGIServer(ThreadingMixIn, simple_server.WSGIServer):
                    pass

                httpd = simple_server.make_server(self.addr, int(self.port), wsgi_application, ThreadingWSGIServer)
            else:
                httpd = simple_server.make_server(self.addr, int(self.port), wsgi_application)
            httpd.serve_forever()
        except socket.error as e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned-to.",
            }
            try:
                error_text = ERRORS[e.errno]
            except KeyError:
                error_text = str(e)
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)