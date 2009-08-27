#!/usr/bin/python

# $Id: tokens.py 84 2009-02-26 23:08:06Z fpletz $
# ----------------------------------------------------------------------------
# "THE MATE-WARE LICENSE"
# codec <codec@muc.ccc.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a mate in return.
# ----------------------------------------------------------------------------

import psycopg2
import hashlib
import sys

from upay.config import config
from upay.logger import flogger, getLogger

class Token:
    log = getLogger('Token')

    def __init__(self):
        self.tokencount = 0
        self.cost = 0
        self.db = psycopg2.connect(
                database=config.get('database', 'db'),
                host=config.get('database', 'host'),
                port=config.getint('database', 'port'),
                user=config.get('database', 'user'),
                password=config.get('database', 'password'))
        self.db_cur = self.db.cursor()
        self.tokenlist = []

    @flogger(log)
    def clear():
        self.tokenlist = []
        self.tokencount = 0

    @flogger(log)
    def bootstrap(self):
        self.db_cur.execute('''
            DROP TABLE IF EXISTS pricelines;
            CREATE TABLE pricelines (
                priceline INT PRIMARY KEY,
                price INT
            )
        ''')
        self.db_cur.execute('''
            DROP TABLE IF EXISTS tokens;
            CREATE TABLE tokens (
                hash VARCHAR PRIMARY KEY,
                used DATE NULL,
                created DATE
            )
        ''')
        self.db_cur.execute('''
            DROP TABLE IF EXISTS history;
            CREATE TABLE history (
                priceline INT,
                date DATE,
                UNIQUE (priceline, date)
            )
        ''')
        self.db.commit()

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
    def check(self, token, reset=False):
        if token in self.tokenlist:
            self.log.warning('token already in tokenlist')
            self.log.info('aborting')
            return False

        hashtoken = self.hash(token)

        self.db_cur.execute('SELECT hash FROM tokens WHERE used IS NULL AND hash=%s', (hashtoken,))
        ret = self.db_cur.fetchone()
        self.log.debug('fetch returned %s' % str(ret))
        if ret:
            self.log.info('%s is unused' % token)
            # print "FOUND UNUSED TOKEN: %s" % token
            self.tokencount += 1
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
        self.db_cur.execute('SELECT price FROM pricelines WHERE priceline=%s', (priceline,))
        price = self.db_cur.fetchone()
        self.log.debug('price=%s' % price)
        
        if price is None:
            self.log.error('Priceline %s not found! o.O' % priceline)
            return False

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
                    self.log.info('Marking %s used' % token)
                    hashtoken = self.hash(token)
                    self.db_cur.execute('UPDATE tokens SET used=NOW() WHERE hash=%s', (hashtoken,))
                    rejected = rejected+1
        self.db_cur.execute('INSERT INTO history VALUES(%s, NOW())',
                (priceline,))
        self.db.commit()
        return True

if __name__ == '__main__':
    token = Token()
    token.bootstrap()
    #token.hash("ppsqmxjdgu")
    token.check("frnzjbcns")
    crd = token.eot()
    ret = token.assets('1')
    token.finish(1)

