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
**-t** Targetlist in CSV format [TODO example] [mandatory]</br>
**-l** Library mode of bisulfite experiment</br>
**-d** List of inputfiles; if not specified, the input files are added at the end [optional]</br>
**-a** Specify the aligner that should be used</br>
**-o** Output directory</br>

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


