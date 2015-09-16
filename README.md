# TABSAT

TABSAT - Targeted Amplicon Bisulfite Sequencing Analysis Tool - is a tool for analyzing targeted bisulfite sequencing data generated on an Ion Torrent PGM / Illumina MiSeq. 
It performs
* QA
* Alignment using [Bismark][http://www.bioinformatics.babraham.ac.uk/projects/bismark/]
* Result aggregation into a table
* Visualization as lollipop plots

Available as
* Fully configured Virtual Machine [TODO]
* [Platomics](www.platomics.com) app [TODO]
* Source code

Please check out the Sourceforge page: http://sourceforge.net/projects/tabsat/

## Use
```sh
./tabsat -t targetlist -l <DIR|NONDIR> -d inputdirectory [with list of files] -a aligner <bowtie2|tmap> -o outputdirectory [files]
```
**-t** Targetlist in CSV format [TODO example] [mandatory]<br />
**-l** Library mode of bisulfite experiment<br />
**-a** Specify the aligner that should be used<br />
**-m** This parameter is used for filtering reads that are shorter than the given threshold.<br />
**-q** Bases that are below the given threshold are removed from the 3’ end of the reads (read trimming)<br />
**-p** Percent of target covered by a read for pattern creation. This value specifies the percent of the target that needs to be covered by a read to include it for pattern analysis.<br />
**-r**: Minimum number of reads that need to be present at each CpG site.	<br />
**-o** Output directory<br />
**-d** List of inputfiles; if not specified, the input files are added at the end [optional]<br />

#### Examples
Test with input file directory
```sh
tabsat -l NONDIR -t target.csv -d test_input_dir -a tmap -o test_output_dir
```
Test with separate input files
```sh
tabsat -l NONDIR -t target.csv -o test_output_files xy.fastq abs.fastq
```


## Installation
* Check out the project (git clone)
* Download the reference genome - [Example dowload](ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/hg19/ucsc.hg19.fasta.gz)
* Prepare the reference genome
```sh
$ tabsat/reference/prepareReference.sh
```
* Prepare the CpG file
```sh
apt-get install p7zip-full
```


