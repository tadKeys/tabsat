#!/bin/bash

echo -e "\nRunning Tabsat test \n"

USER_HOME=$HOME
BASE_DIR="${USER_HOME}/tabsat"
TABSAT="${BASE_DIR}/tabsat"
TARGET_FILE="${BASE_DIR}/zz_test/target_list.csv"

TEST_OUTPUT="${BASE_DIR}/tabsat_test_output"

## Create directory
mkdir -p ${TEST_OUTPUT}

## Test with file list
FILE1="${BASE_DIR}/zz_test/PGM_316D_IonXpress_032_1.fastq"

${TABSAT} -l NONDIR -q 21 -m 9 -p 0.7 -r 4 -t "${TARGET_FILE}" -a tmap -o ${TEST_OUTPUT} ${FILE1}


