import pybedtools
import sys
import glob
import subprocess
import os


## 

def create_section(section_start, prev_end, interval, cur_sum):

    if cur_sum == 0:
        print section_start
        print interval
        cur_sum = 1

    #print cur_sum
    #print (int(interval.start) - int(section_start))

    return str(interval.chrom) + "\t" + str(section_start) + "\t" + str(prev_end) + str("\t") + str( float(cur_sum) / (float(prev_end) - float(section_start)) )  ## don't us end as we are already in the next section


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

	

        if int(interval.count) < 25:

            ## Check if in the middle of a section
            if cur_sum > 0:
                #print "printint first"
                off_target_sections.append(create_section(section_start, prev_end, interval, cur_sum))
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
                off_target_sections.append(create_section(section_start, prev_end, interval, cur_sum))

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
    tmap_off_targets = list()
    for f in tmap_sam_files:
        tmap_off_targets.append(get_stats_for_file(target_file, f))

    tmap_total_ot = 0
    for t in tmap_off_targets:
	tmap_total_ot += len(t)

    print "Total: " + str(tmap_total_ot)



    print "\nBOWTIE\n"

    bowtie_off_targets = list()
    for f in bowtie_sam_files:
        bowtie_off_targets.append(get_stats_for_file(target_file, f))

    bowtie_total_ot = 0
    for t in bowtie_off_targets:
	bowtie_total_ot += len(t)

    print "Total: " + str(bowtie_total_ot)








if __name__ == '__main__':
    main()
