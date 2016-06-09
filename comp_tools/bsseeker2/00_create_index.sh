#!/bin/bash

REFPATH="/home/app/tabsat/reference/human/hg19/bsseeker2_bowtie2/hg19.fasta"
DBPATH="/home/app/tabsat/reference/human/hg19/bsseeker2_bowtie2/Bisulfite_Genome"

SCRIPT="/home/app/tabsat/tools/bsSeeker2/BSseeker2/bs_seeker2-build.py"

## Put bowtie2 into PATH
PATH="/home/app/tabsat/tools/bowtie2/bowtie2-2.2.4:$PATH"

${SCRIPT} -f ${REFPATH} --aligner=bowtie2 -d ${DBPATH}

