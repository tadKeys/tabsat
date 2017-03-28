#!/bin/bash

echo -e "\nRunning Tabsat test \n"

TMP_CUR_DIR=`dirname $0`
TMP_TABSAT_SCRIPT="$TMP_CUR_DIR/../../tabsat"
TMP_ABS_TABSAT_SCRIPT=`readlink -f $TMP_TABSAT_SCRIPT`
BASE_DIR=`dirname $TMP_ABS_TABSAT_SCRIPT`

TABSAT="${BASE_DIR}/tabsat"
TEST_DIR="${BASE_DIR}/tools/zz_test"
TARGET_FILE="${TEST_DIR}/target_list_tmap.csv"
TEST_OUTPUT="${BASE_DIR}/tabsat_test_output_tmap"

## Create directory
mkdir -p ${TEST_OUTPUT}

## Test with file list
FILE1="${TEST_DIR}/PGM_316D_IonXpress_028_1.fastq"

${TABSAT} -l NONDIR -e SE -g hg19 -q 21 -m 9 -p 0.7 -r 4 -t "${TARGET_FILE}" -a tmap -o ${TEST_OUTPUT} ${FILE1}


