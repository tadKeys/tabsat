import pybedtools
import sys
import glob
import subprocess
import os
import numpy


## Based on the deep coverage of up to 3300 1-2% seems reasonable for the cutoff
min_read_depth = 45


def create_section(section_start, prev_end, section_chrom, cur_sum):

    if cur_sum == 0:
        print section_start
        print section_chrom
        cur_sum = 1

    #print cur_sum
    #print (int(interval.start) - int(section_start))

    return str(section_chrom) + "\t" + str(section_start) + "\t" + str(prev_end) + str("\t") + str( float(cur_sum) / (float(prev_end) - float(section_start)) )  ## don't us end as we are already in the next section


def print_off_targets(off_target_sections):

    print "Chr\tStart\tEnd\tAvgCov"
    for ots in off_target_sections:
        print ots




def summary_off_target_mapping(bed_file_path, sam_file_path):

    bed_file = pybedtools.example_bedtool(bed_file_path)
    sam_file = pybedtools.example_bedtool(sam_file_path)

    ## Build intersect (-v similar to grep)
    non_intersect_bam = sam_file.intersect(bed_file, v=True)

    ## Calculate coverage of off-sites
    non_intersect_coverage = non_intersect_bam.genome_coverage(bg=True)


    ## Filter all with cov < 11


    off_target_sections = list()
    
    section_start = 0
    section_chrom = None
    prev_end = 0
    cur_sum = 0

    count = 0
    for interval in non_intersect_coverage:
        #print interval

	

        if int(interval.count) <= min_read_depth:

            ## Check if in the middle of a section
            if cur_sum > 0:
                #print "printint first"
                off_target_sections.append(create_section(section_start, prev_end, section_chrom, cur_sum))
                section_start = 0
		section_chrom = None
                cur_sum = 0
            
	    continue


        ## Check if the interval continues
        if section_chrom and section_chrom == interval.chrom and int(prev_end) == int(interval.start):
            #print "adding: " + str(interval.count) + " to: " + str(cur_sum)
            cur_sum += int(interval.count) * int(interval.end - interval.start)
        else:
            ## Check if the section_start >0

            if section_start > 0:
                ## Print the interval
                #print "printing second"
                off_target_sections.append(create_section(section_start, prev_end, section_chrom, cur_sum))

            section_start = int(interval.start)
	    section_chrom = interval.chrom
            cur_sum = int(interval.count) * int(interval.end - interval.start)



        prev_end = int(interval.end)

#    	if count > 700:
#    	    break
#    
#    	count += 1


    print_off_targets(off_target_sections)
    print "Number off-targets: " + str(len(off_target_sections))

    return off_target_sections



def get_tmap_sam_files():
    return glob.glob(os.path.join(get_cwd(), "comparison/*NONDIR_tmap/*sam"))


def get_bowtie_sam_files():
    return glob.glob(os.path.join(get_cwd(), "comparison/*NONDIR_bowtie2/*sam"))

def get_cwd():
    return os.path.dirname(os.path.realpath(__file__))


def prepare_bam_file(sam_file):

    bam_name = os.path.join(get_cwd(), os.path.basename(sam_file)[:-4] + "_sorted")

    if os.path.exists(bam_name + ".bam"):
        return bam_name + ".bam"


    #print sam_file
    #print bam_name

    cmd = ["samtools"]
    cmd += ["view"]
    cmd += ["-S"]
    cmd += ["-b"]
    cmd += [sam_file]
    cmd += ["|"]
    cmd += ["samtools"]
    cmd += ["sort"]
    cmd += ["-"]
    cmd += [bam_name]


    #print " ".join(cmd)

    ps = subprocess.Popen(" ".join(cmd), shell=True)
    ps.wait()

    return bam_name + ".bam"





def get_stats_for_file(target_bed, sam_file):

    bam_file = prepare_bam_file(sam_file)

    print bam_file + ":"

    return summary_off_target_mapping(target_bed, bam_file)





def main():

    target_file = os.path.join(get_cwd(), "target.bed")

    tmap_sam_files = get_tmap_sam_files()
    bowtie_sam_files = get_bowtie_sam_files()

    #get_stats_for_file(target_file, tmap_sam_files[7])
    #get_stats_for_file(target_file, bowtie_sam_files[8])
    #sys.exit()


    print "TMAP\n"
    tmap_off_targets = dict()
    for f in tmap_sam_files:
	f_name = os.path.basename(f).split(".")[0]
        tmap_off_targets[f_name] = get_stats_for_file(target_file, f)
#	break

    tmap_total_ot = 0
    for t in tmap_off_targets:
	tmap_total_ot += len(t)

    print "Total: " + str(tmap_total_ot)



    print "\nBOWTIE\n"

    bowtie_off_targets = dict()
    for f in bowtie_sam_files:
	f_name = os.path.basename(f).split(".")[0]
        bowtie_off_targets[f_name] = get_stats_for_file(target_file, f)
#	break

    bowtie_total_ot = 0
    for t in bowtie_off_targets:
	bowtie_total_ot += len(t)

    print "Total: " + str(bowtie_total_ot)



    ## Intersect
    print "Intersect"

    #print tmap_off_targets
    #print bowtie_off_targets


    list_num_not_overlapping = list()

    for t_file in sorted(tmap_off_targets):

	t_t = tmap_off_targets[t_file]
	b_t = bowtie_off_targets[t_file]
#	b_t = bowtie_off_targets.values()[0]

	print "File: " + str(t_file)
	print "Number off-targets tmap: " + str(len(t_t))
	print "Number off-targets bowtie: " + str(len(b_t))

	## Create bed files
	t_bed = pybedtools.BedTool("\n".join(t_t), from_string=True)
	b_bed = pybedtools.BedTool("\n".join(b_t), from_string=True)
	#print "a: " + str(t_bed)
	#print "b: " + str(b_bed)


	#print "Closest: "
	closest = t_bed.closest(b_bed, d=True)
	#print closest
	#print len(closest)

	num_not_overlapping = 0

	for c in closest:
	    #print c
	    distance = c[8]
	    #print c[8]
	    if not int(distance) == 0:
		#print distance
		num_not_overlapping += 1

	print "# not overlapping: " + str(num_not_overlapping)

	list_num_not_overlapping.append(num_not_overlapping)

    print ""
    print "Median not overlapping: " + str(numpy.median(list_num_not_overlapping))
    print "Mean not overlapping: " + str(numpy.mean(list_num_not_overlapping))
    


	






if __name__ == '__main__':
    main()
