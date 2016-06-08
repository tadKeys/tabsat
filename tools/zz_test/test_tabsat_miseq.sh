#!/bin/bash

echo -e "\nRunning Tabsat test \n"

USER_HOME=$HOME
BASE_DIR="${USER_HOME}/tabsat"
TABSAT="${BASE_DIR}/tabsat"

TEST_DIR="${BASE_DIR}/tools/zz_test"
TARGET_FILE="${TEST_DIR}/target_list_miseq.csv"
TEST_OUTPUT="${BASE_DIR}/tabsat_test_output_miseq"

## Create directory
mkdir -p ${TEST_OUTPUT}

## Test with file list
FILE1="${TEST_DIR}/SRR3296596_1.fastq"
FILE2="${TEST_DIR}/SRR3296596_2.fastq"

${TABSAT} -e PE -g hg19 -l NONDIR -q 21 -m 9 -p 0.7 -r 4 -t "${TARGET_FILE}" -a bowtie2 -o ${TEST_OUTPUT} ${FILE1} ${FILE2}


