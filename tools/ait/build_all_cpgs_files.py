#!/usr/bin/python

import csv
import os
import subprocess
import sys


def create_directory(dir_name):
    try:
	os.makedirs(dir_name)
    except OSError:
	print("Output directory already exists: " + dir_name)
	pass



## Call bismark
def call_bismark(reference_folder, reference):
    print "Call bismark"

    output_dir = "/tmp/all_cpgs_" + str(reference) + "/"

    ## Create directory in /tmp
    create_directory(output_dir)

    ## Check if tmp file exists
    tmp_bed_graph = os.path.join(output_dir, "PGM_316D_IonXpress_028_1_trimmed.fastq_bismark_tmap.CpG_report.txt")
    if os.path.exists(tmp_bed_graph):
	print "Bed Graph for " + str(reference) + " exists"
	return tmp_bed_graph


    sam_file = "/home/app/tabsat/tabsat_test_output/PGM_316D_IonXpress_028_1_NONDIR_tmap/PGM_316D_IonXpress_028_1_trimmed.fastq_bismark_tmap.sam"


    ## Build the call
    bs_call = []
    bs_call.append("/home/app/tabsat/tools/bismark_original/bismark_methylation_extractor")
    bs_call.append("-s")
    bs_call.append("--bedGraph")
    bs_call.append("--counts")
    bs_call.append("--buffer_size")
    bs_call.append("10G")
#     bs_call.append("--CX_context")
    bs_call.append("--cytosine_report")
    bs_call.append("--genome_folder")
    bs_call.append(reference_folder)
    bs_call.append(sam_file)

    print " ".join(bs_call)

    sp = subprocess.Popen(bs_call, cwd=output_dir)
    sp.wait()

    print "Finished running Bismark"

    return tmp_bed_graph






## Extract positions
def extract_positions(tmp_bed_graph, all_cpgs):
    print "Extract positions from: " + str(tmp_bed_graph)

    with open(tmp_bed_graph) as org_cpg, open(all_cpgs, "w") as new_cpg:
	csv_new = csv.writer(new_cpg, delimiter = "\t")
	for row in csv.reader(org_cpg, delimiter = "\t"):
	    csv_new.writerow([row[0] + "-" + row[1], row[2]])



def file_exists(file_path):
    print "Check if final file exists: '" + str(file_path) + "'"
    return os.path.exists(file_path)


def sort_file(file_path):
    print "Sorting all_cpgs file: " + str(file_path)

    sorted_file_path = file_path[:-4] + "_sorted.txt"

    cmd = ["sort", "-k", "1", file_path, ">", sorted_file_path]

    print "cmd: " + " ".join(cmd)

    s = subprocess.Popen(cmd, shell=True)
    s.communicate()

    subprocess.check_call(["dos2unix", sorted_file_path])



def main():
    ## Human
    print "HUMAN"
    all_cpgs_human = "all_cpgs_only_pos_hg19a.txt"
    if not file_exists(all_cpgs_human):
	print "Final file exists: " + str(all_cpgs_human)
    else:
	print "Start generating file"
        #tmp_bed_graph = call_bismark("/home/app/tabsat/reference/human/hg19", "hg19")
	#extract_positions(tmp_bed_graph, all_cpgs_human)
	sort_file(all_cpgs_human)
	print "Done with hg19"

    print "\n"

    sys.exit()

    print "MOUSE"

    ## Mouse
    all_cpgs_mouse = "all_cpgs_only_pos_mm10.txt"
    if file_exists(all_cpgs_mouse):
	print "Final file exists: " + str(all_cpgs_mouse)
    else:
	print "Start generating file"
	tmp_bed_graph = call_bismark("/home/app/tabsat/reference/mouse/mm10", "mm10")
	extract_positions(tmp_bed_graph, all_cpgs_mouse)
	sort_file(all_cpgs_mouse)
	print "Done with mm10"




if __name__ == '__main__':
    main()

