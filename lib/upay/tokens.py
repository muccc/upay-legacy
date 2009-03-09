#!/usr/bin/python

# $Id: tokens.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

import sqlite3
import hashlib
import sys

from upay.logger import flogger, getLogger

class Token:
    log = getLogger('Token')

    def __init__(self):
        self.tokencount = 0
        self.cost = 0
        self.tokenreset = False
        self.db = sqlite3.connect('token.db')
        self.db_cur = self.db.cursor()
        self.tokenlist = []

    def bootstrap(self):
        pass

    def add(self, token):
        return True 
    
    @flogger(log)
    def hash(self, token):
        self.log.info('token=%s' % token)
        self.hashlib = hashlib.sha512()
        self.hashlib.update(token)
        self.log.info('return=%s' % self.hashlib.hexdigest())
        return self.hashlib.hexdigest()

    @flogger(log)
    def check(self, token):
        if self.tokenreset:
            self.log.info('Resetting in-memory token data')
            self.tokenreset = False
            self.tokencount = 0
            self.tokenlist = []
        
        if token in self.tokenlist:
            self.log.warning('token already in tokenlist')
            self.log.info('aborting')
            return False

        hashtoken = self.hash(token)

        self.db_cur.execute('SELECT hash FROM tokens WHERE used=0 AND hash=? LIMIT 1', (hashtoken,))
        ret = self.db_cur.fetchone()
        self.log.debug('fetch returned %s' % str(ret))
        if ret:
            self.log.info('%s is unused' % token)
            # print "FOUND UNUSED TOKEN: %s" % token
            self.tokencount = self.tokencount+1
            self.tokenlist.append(token)
            return True
        else:
            self.log.info('%s is used' % token)
            return False

    @flogger(log)
    def eot(self):
        self.log.info('Number of valid tokens: %s' % self.tokencount)
        return self.tokencount
    
    @flogger(log)
    def assets(self, priceline):
        self.db_cur.execute('SELECT price FROM pricelines WHERE priceline=?', (priceline,))
        price = self.db_cur.fetchone()
        self.log.debug('price=%s' % price)
        self.cost = int(price[0])
        self.log.info('cost=%s' % self.cost)
        
        if self.tokencount >= self.cost:
            self.log.info('Liquidity is given')
            return True
        else:
            self.log.info('Liquidity is not given')
            return False

    @flogger(log)
    def finish(self, priceline):
        rejected = 0
        if self.cost != 2342:
            for token in self.tokenlist:
                if rejected < self.cost:
                    self.log.info('Rejecting %s' % token)
                    hashtoken = self.hash(token)
                    self.db.execute('UPDATE tokens SET used=1 WHERE hash=?', (hashtoken,))
                    rejected = rejected+1 
        self.db.commit()
        self.tokenreset = True
        return True

if __name__ == '__main__':
    token = Token()
    token.hash("ppsqmxjdgu")
    token.hash("ppsqmxjdgu")
    token.hash("ppsqmxjdgu")
    token.hash("ppsqmxjdgu")
    sys.exit(0)
    token.check("frnzjbcns")
    crd = token.eot()
    ret = token.assets('1')
    token.finish(1)

