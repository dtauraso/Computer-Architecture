#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
if len(sys.argv) <= 1:
    print('no filename was provied')
else:

    cpu.load(sys.argv[1])
    cpu.run()