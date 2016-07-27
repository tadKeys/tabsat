#!/bin/bash

USER_HOME=$HOME
BASE_DIR="${USER_HOME}/tabsat"
TOOLS="${BASE_DIR}/tools"

PRINSEQLITE="${TOOLS}/prinseq-lite-0.20.4/prinseq-lite.pl"
PRINSEQGRAPHS="${TOOLS}/prinseq-lite-0.20.4/prinseq-graphs-noPCA.pl"

SCRIPT_BOWTIE2="${TOOLS}/bismark_original/bismark" #only for bowtie2
SCRIPT_TMAP="${TOOLS}/bismark_tmap/bismark"
#SCRIPT_TMAP="${TOOLS}/bismark_tmap/bismark_indel" #when using GATK

SCRIPT_METH_BOWTIE2="${TOOLS}/bismark_original/bismark_methylation_extractor" #only for bowtie2
SCRIPT_METH_TMAP="${TOOLS}/bismark_tmap/bismark_methylation_extractor"

QC_MODULE="${BASE_DIR}/01_qc.sh"
FINAL_TABLE="${TOOLS}/ait/create_final_table.py"

export PATH="${TOOLS}/iontorrent/:$PATH"
export PATH="${TOOLS}/bowtie2/bowtie2-2.2.4/:$PATH"


echo -e "\n- Starting 02_meth_pipe.sh\n"

echo $@

if [ -n "$1" ];
then
    file=${1}
else
    echo "-- Please specify a file"
    exit 1
exit
fi


if [ -n "$2" ];
then
    outputfolder=${2}
else
    echo "-- Please specify an output folder"
    exit 1
exit
fi


if [ -n "$3" ];
then
    target_list=${3}
else
    echo "-- Please specify an list of targets in tab separated format."
    exit 1
exit
fi


if [[ $4 ]];
then
    seq_library=${4}
    echo "- SeqLibrary: $seq_library"
else
    echo "-- Please specify the sequence library: NONDIR or DIR/ $seq_library"
    exit 1
exit
fi


if [[ $5 ]];
then
    aligner=${5}
    echo "- Aligner: $aligner"
else
    echo "-- Please specify the aligner: bowtie2 or tmap"
    exit 1
exit
fi 


if [[ $6 ]];
then
    param_min_length=${6}
else
    param_min_length="8"
fi
echo "- param_min_length: ${param_min_length}"


if [[ $7 ]];
then
    param_max_length=${7}
else
    param_max_length="100000"
fi
echo "- param_max_length: ${param_max_length}"



if [[ $8 ]];
then
    param_min_qual=${8}
else
    param_min_qual="20"
fi
echo "- param_min_qual: ${param_min_qual}"


if [[ $9 ]];
then
    param_ref_genome=${9}
else
    echo "- Assuming human reference is needed"
    param_ref_genome="hg19"
fi
echo "- param_ref_genome: ${param_ref_genome}"


if [[ ${10} ]];
then
    if [ ${10} == "SE" ] || [ ${10} == "PE" ]
    then
        param_seq_library=${10}
    else
	echo "- Please specify a correct sequencing library (SE,PE)"
	exit 1
    fi
else
    echo "- Please specify a sequencing library (SE,PE)"
    exit 1
fi
echo "- param_seq_library: ${param_seq_library}"



## If libary is PE than a second file needs to be provided
if [ $param_seq_library == "PE" ]
then
    echo "- PE library - looking for second file"
    if [[ ${11} ]];
    then
	file_pe=${11}
	echo "- Found 2nd PE file: ${file_pe}"
    else
	echo "- No second file for PE specified"
	exit 1
    fi
fi



## Create paths for reference genome
if [ $param_ref_genome == "hg19" ]
then
    REFPATH_TMAP="${BASE_DIR}/reference/human/hg19/bismark_tmap"
    REFPATH_BOWTIE2="${BASE_DIR}/reference/human/hg19/bismark_bowtie2"
elif [ $param_ref_genome == "mm10" ]
then
    REFPATH_TMAP="${BASE_DIR}/reference/mouse/mm10/bismark_tmap"
    REFPATH_BOWTIE2="${BASE_DIR}/reference/mouse/mm10/bismark_bowtie2"
else
    echo "-- Please specify a valid reference genome (hg19, mm10)."
    exit 1
fi



if [ $seq_library == "NONDIR" ]
then
    seq_lib="--non_directional"
else
    seq_lib=""
fi

echo "-- seq_library: $seq_library"

if [ $aligner == "bowtie2" ]
then
    aligner="--bowtie2"
    REFPATH=${REFPATH_BOWTIE2}
    SCRIPT=${SCRIPT_BOWTIE2}
    SCRIPT_METH_EXT=${SCRIPT_METH_BOWTIE2}
else
    aligner="--tmap -E 1 -g 3"
    #aligner="--tmap"
    REFPATH=${REFPATH_TMAP}
    SCRIPT=${SCRIPT_TMAP}
    SCRIPT_METH_EXT=${SCRIPT_METH_TMAP}
fi


##
## Start with the work
##





##
## Create output folder
##
mkdir -p $outputfolder


##
## Call QC module for the first time
##
${QC_MODULE} ${file} ${outputfolder}

## Call for pair
if [ $param_seq_library == "PE" ]
then
    ${QC_MODULE} ${file_pe} ${outputfolder}
fi




##
## Prinseq filtering and trimming
##

echo "-- Performing Fastq filtering/trimming (filter min-length: ${param_min_length}bp, trim 3' end quality <${param_min_qual})"


if [ $param_seq_library == "SE" ]
then
    echo "-- Filter for SE"
    FILENAME=`basename ${file} .fastq`
    perl ${PRINSEQLITE} -fastq ${file} -out_good "${outputfolder}/${FILENAME}_trimmed" -min_len ${param_min_length} -max_len ${param_max_length} -trim_qual_right ${param_min_qual} -trim_qual_rule lt -out_bad "${outputfolder}/${FILENAME}_bad" &> ${outputfolder}/prinseq_trimming.log
else
    echo "-- Filter for PE"
    FILENAME=`basename ${file} _1.fastq`
    echo "- FILENAME in PE setting: ${FILENAME}"
    perl ${PRINSEQLITE} -fastq ${file} -fastq2 ${file_pe} -out_good "${outputfolder}/${FILENAME}_trimmed" -min_len ${param_min_length} -max_len ${param_max_length} -trim_qual_right ${param_min_qual} -trim_qual_rule lt -out_bad "${outputfolder}/${FILENAME}_bad" &> ${outputfolder}/prinseq_trimming_pe.log
fi

echo "-- ... done performing filtering/trimming"



##
## Call QC module again
##

if [ $param_seq_library == "SE" ]
then
    ${QC_MODULE} ${outputfolder}/${FILENAME}_trimmed.fastq ${outputfolder}
else
    ## Call for paired-end
    ${QC_MODULE} ${outputfolder}/${FILENAME}_trimmed_1.fastq ${outputfolder} &
    ${QC_MODULE} ${outputfolder}/${FILENAME}_trimmed_2.fastq ${outputfolder} &
    wait
fi


##
## Bismark mapping
##

SAM_FILE="${outputfolder}/${FILENAME}_trimmed.fastq_bismark.sam"

if [[ ! -f ${SAM_FILE} ]]
then
    if [ $param_seq_library == "PE" ]
    then
	echo "-- Calling Bismark PE: ${outputfolder}/${FILENAME}_trimmed_1.fastq and ${outputfolder}/${FILENAME}_trimmed_2.fastq"
	${SCRIPT} ${aligner} ${seq_lib} -o ${outputfolder} ${REFPATH} -1 ${outputfolder}/${FILENAME}_trimmed_1.fastq -2 ${outputfolder}/${FILENAME}_trimmed_2.fastq &> "${outputfolder}/bismark.log"
    else
	echo "-- Calling Bismark SE ${outputfolder}/${FILENAME}_trimmed.fastq"
	${SCRIPT} ${aligner} ${seq_lib} -o ${outputfolder} ${REFPATH} ${outputfolder}/${FILENAME}_trimmed.fastq &> "${outputfolder}/bismark.log"
    fi
else
    echo "-- SAM file exists"
fi

echo "-- ... done with bismark."


SAM_FILE="${outputfolder}/${FILENAME}*.sam"

##
## Methyl extraction
##
echo "-- Performing methyl extraction on SAM_FILE: ${SAM_FILE} ..."
${SCRIPT_METH_EXT} -s --bedGraph ${SAM_FILE} -o ${outputfolder} &> "${outputfolder}/extracter.log"
echo "-- ... done with methyl extraction."





















