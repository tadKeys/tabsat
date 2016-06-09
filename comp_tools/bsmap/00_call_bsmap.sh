#!/bin/bash

SCRIPT="/home/app/tabsat/tools/bsmap/bsmap-2.90/bsmap"
REFPATH="/home/app/tabsat/reference/human/hg19/bsmap/hg19.fasta"

FILE="/home/app/tabsat/tools/zz_test/PGM_316D_IonXpress_028_1.fastq"

#
# maybe consider -g parameter
#
${SCRIPT} -a ${FILE} -d ${REFPATH} -o PGM_316D_IonXpress_028_1.sam &> run.log
