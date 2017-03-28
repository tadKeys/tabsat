#!/bin/bash

TMP_CUR_DIR=`dirname $0`
TMP_TABSAT_SCRIPT="$TMP_CUR_DIR/tabsat"
TMP_ABS_TABSAT_SCRIPT=`readlink -f $TMP_TABSAT_SCRIPT`
BASE_DIR=`dirname $TMP_ABS_TABSAT_SCRIPT`

PRINSEQLITE="${BASE_DIR}/tools/prinseq-lite-0.20.4/prinseq-lite.pl"
PRINSEQGRAPHS="${BASE_DIR}/tools/prinseq-lite-0.20.4/prinseq-graphs-noPCA.pl"


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


## Get the filename
FILENAME=`basename ${file}`


##
## Create output folder
##
mkdir -p $outputfolder



echo "-- Performing QC with ${file} - folder: ${outputfolder} - filename: ${FILENAME}"

##
## Run PrinSeq
##
FILENAME=`basename ${file}`
perl ${PRINSEQLITE} -fastq ${file} -graph_data ${outputfolder}/${FILENAME}.graph -out_good null -out_bad null &> ${outputfolder}/${FILENAME}.log



##
## Create PrinSeq graph
##
FILENAME=`basename ${file}`
perl ${PRINSEQGRAPHS} -i ${outputfolder}/${FILENAME}.graph -html_all


echo "-- ... done performing QC"


