#!/usr/bin/env python
import os.path
import cherrypy

from upay.tokens import Token

class CheckToken:
    token = Token()

    @cherrypy.expose
    def check(self, token=''):
        return '\n'.join(map(lambda x: str(self.token.check(x, reset=True)),
            token.strip().split('\n')))

class UPay:
    @cherrypy.expose
    def index(self):
        return 'Hello World!'

upay = UPay()
upay.token = CheckToken()

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 4480,
                        'server.thread_pool': 2,
                        'log.screen': False,
                       })

cherrypy.quickstart(upay)

