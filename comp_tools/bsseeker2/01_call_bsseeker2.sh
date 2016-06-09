#!/bin/bash

REFPATH="/home/app/tabsat/reference/human/hg19/bsseeker2_bowtie2/hg19.fasta"
DBPATH="/home/app/tabsat/reference/human/hg19/bsseeker2_bowtie2/Bisulfite_Genome"

SCRIPT="/home/app/tabsat/tools/bsSeeker2/BSseeker2/bs_seeker2-align.py"
FILE="/home/app/tabsat/tools/zz_test/PGM_316D_IonXpress_028_1.fastq"


## Put bowtie2 into PATH
PATH="/home/app/tabsat/tools/bowtie2/bowtie2-2.2.4:$PATH"


SCRIPT="${SCRIPT} -g ${REFPATH}"
SCRIPT="${SCRIPT} -d ${DBPATH}"
SCRIPT="${SCRIPT} -i ${FILE}"
SCRIPT="${SCRIPT} --aligner=bowtie2"
SCRIPT="${SCRIPT} --bt-p 30" # 30threads per run
SCRIPT="${SCRIPT} -o PGM_316D_IonXpress_028_1.sam"
SCRIPT="${SCRIPT} -f sam"


${SCRIPT}

