#!/bin/bash

echo -e "\nRunning Tabsat test - mouse\n"

USER_HOME=$HOME
BASE_DIR="${USER_HOME}/tabsat"
TABSAT="${BASE_DIR}/tabsat"

TEST_DIR="${BASE_DIR}/tools/zz_test"
TARGET_FILE="${TEST_DIR}/target_list.csv"
TEST_OUTPUT="${BASE_DIR}/tabsat_test_output_mouse"

## Create directory
mkdir -p ${TEST_OUTPUT}

## Test with file list
FILE1="${TEST_DIR}/PGM_316D_IonXpress_028_1.fastq"

${TABSAT} -l NONDIR -q 21 -m 9 -p 0.7 -r 4 -t "${TARGET_FILE}" -a tmap -o ${TEST_OUTPUT} ${FILE1}


