#!/bin/bash

USER_HOME=$HOME
BASE_DIR="${USER_HOME}/tabsat"
BEDTOOLS_BASE="${BASE_DIR}/tools/bedtools/bedtools2/bin"

BAMTOBED="${BEDTOOLS_BASE}/bamToBed"
SORTBED="${BEDTOOLS_BASE}/sortBed"
INTERSECTBED="${BEDTOOLS_BASE}/intersectBed"
COVERAGEBED="${BEDTOOLS_BASE}/coverageBed"
GENOMECOVERAGE="${BEDTOOLS_BASE}/genomeCoverageBed"
MERGEBED="${BEDTOOLS_BASE}/mergeBed"

## INPUTS
QUALITY_DIR=$1
TARGET_LIST=$2
BAM_FILE=$3

if [ ! -n "$1" ];
then
    echo "-- Please specify a quality directory"
    exit 1
exit
fi


if [ ! -n "$2" ];
then
    echo "-- Please specify a target_list file"
    exit 1
exit
fi


if [ ! -n "$3" ];
then
    echo "-- Please specify a BAM file"
    exit 1
exit
fi





## Basename of BAM file
BAM_FILE_BASENAME=`basename ${BAM_FILE}`
BAM_FILE_BASENAME_WO_SUFFIX=`basename ${BAM_FILE} .bam`

## Convert the target list to BED
sed "s/$/\t-$f/" ${TARGET_LIST} | awk '{ print $2"\t"$3"\t"$4"\t"$1"\t"$6"\t"$5}' - | tail -n +2 | ${SORTBED} -i - > ${QUALITY_DIR}/target_list.bed


## Set output file names
NON_INTERSECT_BAM="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.non_intersect.bam"
INTERSECT_BAM="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.intersect.bam"
NON_INTERSECT_COV_BED="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.non_intersect_cov.bed"
INTERSECT_COV_BED="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.intersect_cov.bed"
NON_INTERSECT_COV_MERGED_BED="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.non_intersect_cov_merged.bed"
INTERSECT_COV_MERGED_BED="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.intersect_cov_merged.bed"

## Create an off-target BAM file
#samtools sort -o ${BAM_FILE} aa | ${INTERSECTBED} -v -a - -b ${QUALITY_DIR}/target_list.bed > ${NON_INTERSECT_BAM}

## Create an on-target BAM file
#samtools sort -o ${BAM_FILE} aa | ${INTERSECTBED} -a - -b ${QUALITY_DIR}/target_list.bed > ${INTERSECT_BAM}



## Calculate coverage of off-target sites
#${GENOMECOVERAGE} -ibam ${NON_INTERSECT_BAM} -bg > ${NON_INTERSECT_COV_BED}

## Calculate coverage of on-target sites
#${GENOMECOVERAGE} -ibam ${INTERSECT_BAM} -bg > ${INTERSECT_COV_BED}



## Merge off-target coverage file and limit to regions with coverage greater than 0
#cat ${NON_INTERSECT_COV_BED} | awk '$4 > 100' | ${MERGEBED} -i - -c 4 -o mean > ${NON_INTERSECT_COV_MERGED_BED}

## Merge on-target coverage file and limit to regions with coverage greater than 0
#cat ${INTERSECT_COV_BED} | awk '$4 > 100' | ${MERGEBED} -i - -c 4 -o mean > ${INTERSECT_COV_MERGED_BED}


## Create a summary
SUMMARY_FILE="${QUALITY_DIR}/${BAM_FILE_BASENAME_WO_SUFFIX}.summary.txt"
rm -f ${SUMMARY_FILE}

summary_num_reads_target=`samtools view ${INTERSECT_BAM} | wc -l`
echo "Number of reads on target: ${summary_num_reads_target}" >> ${SUMMARY_FILE}

summary_num_reads_off_target=`samtools view ${NON_INTERSECT_BAM} | wc -l`
echo "Number of reads off target: ${summary_num_reads_off_target}" >> ${SUMMARY_FILE}


summary_num_off_target=`cat ${NON_INTERSECT_COV_MERGED_BED} | wc -l`
echo "Number of targets: ${summary_num_off_target}" >> ${SUMMARY_FILE}








