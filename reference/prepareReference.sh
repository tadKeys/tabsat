#/bin/bash

USER_HOME=$HOME
BASE_DIR="${USER_HOME}/tabsat"
TOOLS="${BASE_DIR}/tools"

SCRIPT="${TOOLS}/bismark_tmap/bismark_genome_preparation"
REFPATH="${BASE_DIR}/reference/human/hg19/bismark_tmap"
TMAP="${TOOLS}/iontorrent"

mkdir -p ${REFPATH}

${SCRIPT} --path_to_program ${TMAP} --tmap ${REFPATH}
