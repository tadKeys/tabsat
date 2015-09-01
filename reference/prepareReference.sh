#/bin/bash

BASE="/home/xworx/bismark_karina/"
TOOLS="${BASE}/tools"

SCRIPT="${TOOLS}/bismark_tmap/bismark_genome_preparation"
REFPATH="${BASE}/reference/human/hg19/bismark_tmap"
TMAP="${TOOLS}/iontorrent"

mkdir -p ${REFPATH}

${SCRIPT} --path_to_program ${TMAP} --tmap ${REFPATH}
