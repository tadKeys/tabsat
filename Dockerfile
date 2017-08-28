FROM ubuntu:14.04
MAINTAINER Stephan Pabinger <stephan.pabinger@ait.ac.at>

ENV DEBIAN_FRONTEND noninteractive

## Update the system
##
RUN apt-get update


## Setup a base system 
##
RUN apt-get update && apt-get install -y \
build-essential \
libjson-perl \
p7zip-full \
curl \
git \
supervisor \
libcairo-perl \
samtools \
python-numpy \
r-base \
r-cran-ggplot2 \
r-cran-plyr \
liblist-moreutils-perl \
libswitch-perl \
imagemagick \
gawk \
nano \
mc 


##
## Change to /root directory
WORKDIR "/root"

##
## Install pybedtools
##
RUN pip install --upgrade pip
RUN pip install cython
RUN pip install pybedtools
RUN pip install pandas


## Clone the repository
##
RUN git clone https://github.com/tadKeys/tabsat.git


## Create reference directory
##
RUN mkdir -p tabsat/reference/human/hg19/bismark_tmap/Bisulfite_Genome


## Download the reference file
RUN curl -SL ftp://ftp.ncbi.nlm.nih.gov/genbank/genomes/Eukaryotes/vertebrates_mammals/Homo_sapiens/GRCh37.p13/seqs_for_alignment_pipelines/GCA_000001405.14_GRCh37.p13_no_alt_analysis_set.fna.gz | gunzip - > tabsat/reference/human/hg19/hg19.fasta 


## Prepare the reference
##
RUN ln -s tabsat/reference/human/hg19/ucsc.hg19.fasta tabsat/reference/human/hg19/bismark_tmap/hg19.fasta
RUN sh ./tabsat/reference/prepareReference.sh


## Prepare the CpG file
## 
RUN 7z e -o tabsat/tools/ait/ tabsat/tools/ait/all_cpgs_only_pos_hg19.7z
RUN 7z e -o tabsat/tools/ait/ tabsat/tools/ait/all_cpgs_only_pos_mm10.7z


## Configure the supervisor
#
COPY files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY files/start.sh /root/start.sh
RUN chmod +x /root/start.sh
ENTRYPOINT ["/root/start.sh"]

