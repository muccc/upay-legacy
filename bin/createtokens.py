#!/usr/bin/python

import sys
from upay.tokens import Token

n = int(sys.argv[1])
tokens = Token().generate(n)
print '\n'.join(tokens)

