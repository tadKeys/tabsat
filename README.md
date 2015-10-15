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

## Example usage
```sh
${TABSAT} -l NONDIR -q 20 -m 10 -p 0.8 -r 0 -t target.csv -a tmap -o output_dir input.fastq
```
**-t** Targetlist in CSV format [TODO example] [mandatory]<br />
**-l** Library mode of bisulfite experiment<br />
**-a** *[optional]* Specify the aligner that should be used<br />
**-m** *[optional]* This parameter is used for filtering reads that are shorter than the given threshold.<br />
**-q** *[optional]* Bases that are below the given threshold are removed from the 3’ end of the reads (read trimming)<br />
**-p** *[optional]* Percent of target covered by a read for pattern creation. This value specifies the percent of the target that needs to be covered by a read to include it for pattern analysis.<br />
**-r**: *[optional]* Minimum number of mapped reads that need to be present at each CpG site.	<br />
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
* Download the reference genome 
 * [Broad](ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/2.8/hg19/ucsc.hg19.fasta.gz)
 * [ENSEMBL](ftp://ftp.ensembl.org/pub/release-75/fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa.gz)
 * [NCBI] (ftp://ftp.ncbi.nlm.nih.gov/genbank/genomes/Eukaryotes/vertebrates_mammals/Homo_sapiens/GRCh37.p13/seqs_for_alignment_pipelines/GCA_000001405.14_GRCh37.p13_no_alt_analysis_set.fna.gz)
* Prepare the reference genome
```sh
$ tabsat/reference/prepareReference.sh
```
* Prepare the CpG file
```sh
apt-get install p7zip-full
```


