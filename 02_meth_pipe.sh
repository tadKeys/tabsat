#!/bin/bash

BASE_DIR="/home/app/tabsat"
TOOLS="${BASE_DIR}/tools"

PRINSEQLITE="${TOOLS}/prinseq-lite-0.20.4/prinseq-lite.pl"
PRINSEQGRAPHS="${TOOLS}/prinseq-lite-0.20.4/prinseq-graphs-noPCA.pl"

SCRIPT_BOWTIE2="${TOOLS}/bismark_original/bismark" #only for bowtie2
SCRIPT_TMAP="${TOOLS}/bismark_tmap/bismark"
#SCRIPT_TMAP="${TOOLS}/bismark_tmap/bismark_indel" #when using GATK
REFPATH_TMAP="${BASE_DIR}/reference/human/hg19/bismark_tmap"
REFPATH_BOWTIE2="${BASE_DIR}/reference/human/hg19/bismark_bowtie2"

SCRIPT_METH_BOWTIE2="${TOOLS}/bismark_original/bismark_methylation_extractor" #only for bowtie2
SCRIPT_METH_TMAP="${TOOLS}/bismark_tmap/bismark_methylation_extractor"

QC_MODULE="${BASE_DIR}/01_qc.sh"
FINAL_TABLE="${TOOLS}/ait/create_final_table.py"

export PATH="${TOOLS}/iontorrent/:$PATH"
export PATH="${TOOLS}/bowtie2/bowtie2-2.2.4/:$PATH"

if [ -n "$1" ];
then
file=${1}
else
echo "-- Please specify a file"
exit
fi


if [ -n "$2" ];
then
outputfolder=${2}
else
echo "-- Please specify an output folder"
exit
fi


if [ -n "$3" ];
then
target_list=${3}
else
echo "-- Please specify an list of targets in tab separated format."
exit
fi


if [[ $4 ]];
then
seq_library=${4}
echo "$seq_library"
else
echo "-- Please specify the sequence library: NONDIR or DIR/ $seq_library"
exit
fi


if [[ $5 ]];                                                                                                                                            
then                                                                                                              
aligner=${5}                                                                                                                                        
echo "$aligner"                                                                                                                                     
else                                                                                                                                                    
echo "-- Please specify the aligner: bowtie2 or tmap"                                                                              
exit                                                                                                                                                    
fi 


if [ $seq_library == "NONDIR" ]
then
seq_lib="--non_directional"
echo "$seq_library"
else 
seq_lib=""
fi

if [ $aligner == "bowtie2" ]                                                                                                                         
then                                                                                                                                                    
aligner="--bowtie2"
REFPATH=${REFPATH_BOWTIE2}
SCRIPT=${SCRIPT_BOWTIE2}
SCRIPT_METH_EXT=${SCRIPT_METH_BOWTIE2}                                                                                                           
else
aligner="--tmap -E 1 -g 3"
REFPATH=${REFPATH_TMAP}
SCRIPT=${SCRIPT_TMAP}
SCRIPT_METH_EXT=${SCRIPT_METH_TMAP}                                                                                                                                       
fi 

#rm /home/app/bismark_karina/zz_test/PGM_METH/*

##
## Create output folder
##
mkdir -p $outputfolder


##
## Prinseq filtering and trimming
##

echo "-- Performing Fastq filtering/trimming (filter min-length: 8bp, trim 3' end quality <20)"

FILENAME=`basename ${file} .fastq`
perl ${PRINSEQLITE} -fastq ${file} -out_good "${outputfolder}/${FILENAME}_trimmed" -min_len 8 -trim_qual_right 20 -trim_qual_rule lt -out_bad "${outputfolder}/${FILENAME}_bad" &> ${outputfolder}/prinseq_trimming.log

echo "-- ... done performing filtering/trimming"


##
## Call QC module again
##

${QC_MODULE} ${outputfolder}/${FILENAME}_trimmed.fastq ${outputfolder}


##
## Bismark mapping
##

SAM_FILE="${outputfolder}/${FILENAME}_trimmed.fastq_bismark_tmap.sam"

echo "-- Bismark $aligner for ${file} ..."

if [[ ! -f ${SAM_FILE} ]]
then
  #echo "enable here"
  ${SCRIPT} ${aligner} ${seq_lib} -o ${outputfolder} ${REFPATH} ${outputfolder}/${FILENAME}_trimmed.fastq &> "${outputfolder}/bismark.log" #deleted tmap-options: -E 1 -g 3
  #${SCRIPT_TMAP} --tmap -g 3 -E 1 -B test01 -o ${outputfolder} ${REFPATH_TMAP} ${outputfolder}/${FILENAME}_trimmed.fastq &> "${outputfolder}/bismark.log"
else
  echo "-- SAM file exists"
fi

echo "-- ... done with bismark."


SAM_FILE="${outputfolder}/${FILENAME}*.sam"

##
## Methyl extraction
##
echo "-- Performing methyl extraction.."
${SCRIPT_METH_EXT} -s --bedGraph ${SAM_FILE} -o ${outputfolder} &> "${outputfolder}/extracter.log"
echo "-- ... done with methyl extraction."


##
## Create final table
##
#echo "-- Creating final table.."

#python ${FINAL_TABLE} ${target_list} ${outputfolder}

#echo "-- .. done with table creation."



















