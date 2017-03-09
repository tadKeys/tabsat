#!/usr/bin/env python2

import sys

## Check that Python version is 2.7
if sys.version_info < (2,7) or sys.version_info >= (3,0):
    print "Please run TABSAT with version 2.7; Currently: " + str(sys.version_info)
    sys.exit(1)