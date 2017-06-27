#/bin/bash

TMP_CUR_DIR=`dirname $0`
TMP_TABSAT_SCRIPT="$TMP_CUR_DIR/../tabsat"
TMP_ABS_TABSAT_SCRIPT=`readlink -f $TMP_TABSAT_SCRIPT`
BASE_DIR=`dirname $TMP_ABS_TABSAT_SCRIPT`

TOOLS="${BASE_DIR}/tools"

SCRIPT="${TOOLS}/bismark_tmap/bismark_genome_preparation"
TMAP="${TOOLS}/iontorrent"
BOWTIE="${TOOLS}/bowtie2/bowtie2-2.2.4"

REFPATH_HUMAN_TMAP="${BASE_DIR}/reference/human/hg19/bismark_tmap"
REFPATH_HUMAN_BOWTIE="${BASE_DIR}/reference/human/hg19/bismark_bowtie2"

REFPATH_MOUSE_TMAP="${BASE_DIR}/reference/mouse/mm10/bismark_tmap"
REFPATH_MOUSE_BOWTIE="${BASE_DIR}/reference/mouse/mm10/bismark_bowtie2"



#####
##### HUMAN
#####

## TMAP
## Create dirs
mkdir -p ${REFPATH_HUMAN_TMAP}
mkdir -p ${REFPATH_HUMAN_TMAP}/Bisulfite_Genome

## Check if all files are present
tmap_human_ct="${REFPATH_HUMAN_TMAP}/Bisulfite_Genome/CT_conversion/genome_mfa.CT_conversion.fa"
tmap_human_ga="${REFPATH_HUMAN_TMAP}/Bisulfite_Genome/GA_conversion/genome_mfa.GA_conversion.fa"

if [ ! -e "${tmap_human_ct}" ] || [ ! -e "${tmap_human_ga}" ]
then
    echo "Human TMAP index files need to be created"

    ## Symlink the reference
    ln -s ${REFPATH_HUMAN_TMAP}/../hg19.fasta ${REFPATH_HUMAN_TMAP}/hg19.fasta

    ${SCRIPT} --path_to_program ${TMAP} --tmap ${REFPATH_HUMAN_TMAP}
else
    echo -e "\nHuman TMAP index files already exist"
fi




## Bowtie 2
## Create dirs
mkdir -p ${REFPATH_HUMAN_BOWTIE}
mkdir -p ${REFPATH_HUMAN_BOWTIE}/Bisulfite_Genome

## Check if all files are present
bowtie_human_ct="${REFPATH_HUMAN_BOWTIE}/Bisulfite_Genome/CT_conversion/genome_mfa.CT_conversion.fa"
bowtie_human_ga="${REFPATH_HUMAN_BOWTIE}/Bisulfite_Genome/GA_conversion/genome_mfa.GA_conversion.fa"

if [ ! -e "${bowtie_human_ct}" ] || [ ! -e "${bowtie_human_ga}" ]
then
    echo "Human Bowtie2 index files need to be created"

    ## Symlink the reference
    ln -s ${REFPATH_HUMAN_BOWTIE}/../hg19.fasta ${REFPATH_HUMAN_BOWTIE}/hg19.fasta

    ${SCRIPT} --path_to_program ${BOWTIE} --bowtie2 ${REFPATH_HUMAN_BOWTIE}
else
    echo "Human Bowtie2 index files already exist"
fi









#####
##### MOUSE
#####

## TMAP
## Create dirs
mkdir -p ${REFPATH_MOUSE_TMAP}
mkdir -p ${REFPATH_MOUSE_TMAP}/Bisulfite_Genome

## Check if all files are present
tmap_mouse_ct="${REFPATH_MOUSE_TMAP}/Bisulfite_Genome/CT_conversion/genome_mfa.CT_conversion.fa"
tmap_mouse_ga="${REFPATH_MOUSE_TMAP}/Bisulfite_Genome/GA_conversion/genome_mfa.GA_conversion.fa"


if [ ! -e "${tmap_mouse_ct}" ] || [ ! -e "${tmap_mouse_ga}" ]
then
    echo "Mouse TMAP index files need to be created"

    ## Symlink the reference
    ln -s ${REFPATH_MOUSE_TMAP}/../mm10.fasta ${REFPATH_MOUSE_TMAP}/mm10.fasta

    ${SCRIPT} --path_to_program ${TMAP} --tmap ${REFPATH_MOUSE_TMAP}
else
    echo "Mouse TMAP index files already exist"
fi





## Bowtie 2
## Create dirs
mkdir -p ${REFPATH_MOUSE_BOWTIE}
mkdir -p ${REFPATH_MOUSE_BOWTIE}/Bisulfite_Genome

## Check if all files are present
bowtie_mouse_ct="${REFPATH_MOUSE_BOWTIE}/Bisulfite_Genome/CT_conversion/genome_mfa.CT_conversion.fa"
bowtie_mouse_ga="${REFPATH_MOUSE_BOWTIE}/Bisulfite_Genome/GA_conversion/genome_mfa.GA_conversion.fa"

if [ ! -e "${bowtie_mouse_ct}" ] || [ ! -e "${bowtie_mouse_ga}" ]
then
    echo "Mouse Bowtie2 index files need to be created"

    ## Symlink the reference
    ln -s ${REFPATH_MOUSE_BOWTIE}/../mm10.fasta ${REFPATH_MOUSE_BOWTIE}/mm10.fasta

    ${SCRIPT} --path_to_program ${BOWTIE} --bowtie2 ${REFPATH_MOUSE_BOWTIE}
else
    echo "Mouse Bowtie2 index files already exist"
fi







