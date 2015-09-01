#!/bin/bash

BASE_DIR="/home/app/tabsat"
PRINSEQLITE="${BASE_DIR}/tools/prinseq-lite-0.20.4/prinseq-lite.pl"
PRINSEQGRAPHS="${BASE_DIR}/tools/prinseq-lite-0.20.4/prinseq-graphs-noPCA.pl"


echo "-- Performing QC"

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


FILENAME=`basename ${file}`

#echo $FILENAME
#echo $outputfolder


##
## Create output folder
##
mkdir -p $outputfolder



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


