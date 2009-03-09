#!/usr/bin/python

import time

import upay.serialinterface
from upay.logger import getLogger, flogger

class Matemat:
    log = getLogger('Matemat')

    def __init__(self):
        self.interface = serialinterface.SerialInterface("/dev/ttyS0",115200,5)
        pass

    @flogger(log)
    def _waitForReply(self,reply):
        self.log.debug('reply=%s' % reply)
        while True:
            msg = self.interface.readMessage()
            if msg == False:
                return False
            if msg in reply:
                self.log.debug('msg=%s' % msg)
                return msg

    @flogger(log)
    def writeLCD(self, msg):
        self.log.info('writeLCD(): msg=%s' % msg)
        msg = "d"+msg
        self.interface.writeMessage(msg);
        return self._waitForReply(["dD"])
    
    @flogger(log)
    def getPriceline(self):
        self.interface.writeMessage("p")
        while True:
            msg = self.interface.readMessage()
            if msg == False:
                return -1
            if msg[0] == 'p':
                self.log.debug('priceline=%s' % msg[2])
                return int(msg[2])

    @flogger(log)
    def serve(self,priceline):
        self.log.info('priceline=%s' % priceline)
        self.interface.writeMessage("s"+str(priceline))
        ret = self._waitForReply(["sO","sN"])
        if ret == False:
            return False
        if ret == "sN":
            return False
        return True

    @flogger(log)
    def completeserve(self):
        return self._waitForReply(["sD"])

# "Testing"
if __name__ == '__main__':
    m = Matemat()
    m.writeLCD("luvv")
    while m.getPriceline() != 3:
        time.sleep(0.2)
    m.serve(3)
    m.completeserve()

