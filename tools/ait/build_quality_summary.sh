#!/bin/bash

QUALITY_DIR=$1
SUMMARY_FILE="${QUALITY_DIR}/00_summary.txt"

## Remove the old summary file
rm -f ${SUMMARY_FILE}

## Concatenate all summaries into one file
for sum_file in `ls ${QUALITY_DIR}/*summary.txt`;
do
    sum_file_base=`basename ${sum_file} .summary.txt`
    echo ${sum_file_base} >> ${SUMMARY_FILE}
    cat ${sum_file} >> ${SUMMARY_FILE}
    echo "" >> ${SUMMARY_FILE}
done
