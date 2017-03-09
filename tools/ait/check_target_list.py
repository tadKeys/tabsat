#!/usr/bin/env python2
import sys

import create_final_table 

##
## Checks the target list
##

if __name__ == '__main__':

    ## Reading inputs
    target_list = sys.argv[1]

    ## Check the table
    create_final_table.check_target_list(target_list)