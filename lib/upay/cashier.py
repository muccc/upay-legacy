#!/usr/bin/python

# $Id: cashier.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

import socket
from upay.logger import flogger, getLogger

class Cashier:
    log = getLogger('Cashier')

    @flogger(log)
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(('127.0.0.1', 4444))
        self.socket.settimeout(1)
        
    @flogger(log)
    def send(self, msg):
        sent = self.socket.send(msg)
        if sent != 0:
            self.log.debug('"%s": Send OK' % msg)
            return True
        else:
            self.log.debug('"%s": Send failed' % msg)
            return False
    
    @flogger(log)
    def recv(self, expect):
        try:
            data = self.socket.recv(64)
        except:
            return False
        
        data = data.strip()
        if data == expect:
            self.log.debug('"%s": Receive OK' % expect)
            return True
        else:
            self.log.debug('"%s": Receive failed' % expect)
            return False

    @flogger(log)
    def isReady(self):
        sent = self.send("Rd")
        if sent:
            rcvd = self.recv("READY")
        else:
            return False
                        
        if rcvd:
            return True
        else:
            return False

    @flogger(log)
    def reportBadPurse(self):
        sent = self.send("Bp")

    @flogger(log)
    def abort(self):
        sent = self.send("Ab")
        if sent: rcvd = self.recv("OK")
        else: return False
                        
        if rcvd: return True
        else: return False

    @flogger(log)
    def checkToken(self, token):
        sent = self.send("Tc%s" % token)

        if sent:
            rcvd = self.recv("OK")
        else:
            return False
        
        if rcvd:
            self.log.debug('"%s": True' % token)
            return True
        else:
            self.log.debug('"%s": False' % token)
            return False

    @flogger(log)
    def checkCredit(self):
        sent = self.send("Td")


if __name__ == '__main__':
    cashier = Cashier()
    ret = cashier.checkToken("12345678")
    ret = cashier.checkToken("12345678")
    ret = cashier.checkToken("12345678")
    ret = cashier.checkToken("12345678")
    ret = cashier.checkCredit()

