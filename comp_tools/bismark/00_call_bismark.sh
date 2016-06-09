#!/bin/bash


SCRIPT="/home/app/tabsat/tools/bismark_original/bismark"
REFPATH="/home/app/tabsat/reference/human/hg19/bismark_bowtie2"
FILE="/home/app/tabsat/tools/zz_test/PGM_316D_IonXpress_028_1.fastq"


## Put bowtie2 into PATH
PATH="/home/app/tabsat/tools/bowtie2/bowtie2-2.2.4:$PATH"


${SCRIPT} --bowtie2 --non_directional -o . ${REFPATH} ${FILE}  &> bismark1.log