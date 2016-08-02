__author__ = 'Stephan'

import glob
import sys
import os
import csv
import numpy


class Region:
    def __init__(self, region_chr, region_start, region_end):
        self.region_chr = region_chr
        self.region_start = region_start
        self.region_end = region_end
                
        if not "random" in region_chr and region_chr != "chrX" and region_chr != "chrY":
            self.region_chr_int = int(region_chr.lstrip("chr"))
        elif region_chr == "chrX":
            self.region_chr_int = 23
        elif region_chr == "chrX":
            self.region_chr_int = 24
        else:
            self.region_chr_int = 25
        
        
    def check_overlap_and_extend(self, rtc):        ## rtc == region_to_check
        if self.region_chr == rtc.region_chr:
            
            ## Check if it is outside
            if self.region_start > rtc.region_end or self.region_end < rtc.region_start:
                ## outside -> not found
                #print "not found"
                return False
            else:
                #print "found"
                ## inside
                ## set new boundaries                
                if self.region_start > rtc.region_start:
                    self.region_start = rtc.region_start
                if self.region_end < rtc.region_end:
                    self.region_end = rtc.region_end
                    
                ## Inside -> found
                return True
       
       
    def overlaps(self, rtc):
        if self.region_chr == rtc.region_chr:
            
            ## Check if it is outside
            if self.region_start > rtc.region_end or self.region_end < rtc.region_start:
                ## outside -> not found
                #print "not found"
                return False
            else:
                return True
            
            
        return False
        
        
    def to_str(self):
        return str(self.region_chr) + ":" + str(self.region_start) + "-" + str(self.region_end)
                    
    def __str__(self):
        return str(self.region_chr) + "(" + str(self.region_chr_int) + ")" + ":" + str(self.region_start) + "-" + str(self.region_end)
        
    def __repr__(self):
        return self.__str__()



def build_region_list(region_list, r):
    
    #print "\n" + str(region_list)
    
    ## Check if anything is in the region list
    if len(region_list) == 0:
        region_list.append(r)
        return 
    
    ## Go over existing entries
    found_region = False
    for reg in region_list:
        #print "reg: " + str(reg)
        #print "r: "+ str(r)
        found_region = reg.check_overlap_and_extend(r)
        if found_region:
            return

    if not found_region:
        region_list.append(r)


def print_rows(rows, output_file):
    
    with open(output_file, "w") as of:
        for row in rows:
            of.write(";".join(row) + "\n")


def summarize(quality_dir, output_file):
    bed_files = glob.glob(os.path.join(quality_dir, "*non_intersect_cov_merged.bed"))
    
    bed_files = sorted(bed_files)
    
    #print bed_files
    
    region_list = list()
    
    ## Build regions
    for bed_file in bed_files:
        with open(bed_file) as bf:
            for row in csv.reader(bf, delimiter="\t"):
                #print row
                
                ## Extend start and end by 5 bps
                region_chr = row[0]
                region_start = int(row[1]) - 5
                region_end = int(row[2]) + 5
                
                ## Check if it overlaps -> if so extend region
                r = Region(region_chr, region_start, region_end)
                
                build_region_list(region_list, r)
                
                
        #break
        
    
    ## Sort region list    
    region_list_sorted = sorted(region_list, key = lambda x: (x.region_chr_int, x.region_start, x.region_end))
    
    
    ## Go over all bed files and build table    
    
    ## Build bed file names
    bed_files_names = [os.path.basename(bf).rstrip(".bam.sorted.non_intersect_cov_merged.bed") for bf in bed_files]
    
    ## Header    
    header = ["Region"]
    header.extend(bed_files_names)
    
    
    rows = [header]
    for r in region_list_sorted:
        output_row = [r.to_str()]
        
        #print "to_str: " + r.to_str()
        #print output_row
        
        #print r
        for bed_file in bed_files:
            
            with open(bed_file) as bf:
                
                found_covs = list()
                
                for row in csv.reader(bf, delimiter="\t"):
                    bf_chr = row[0]
                    bf_start = int(row[1])
                    bf_end = int(row[2])
                    bf_cov = float(row[3])
                    
                    bf_region = Region(bf_chr, bf_start, bf_end)
                    
                    #print "r: " + str(r)
                    #print "bf_region: " + str(bf_region)
                    
                    if r.overlaps(bf_region):                        
                        found_covs.append(bf_cov)
                        
                if len(found_covs) == 0:
                    output_row.append("-")
                else:
                    output_row.append("{:.2f}".format(numpy.mean(found_covs)))
                    
       
        rows.append(output_row)
        
        #break
        
        
    print_rows(rows, output_file)
    
    
    
if __name__ == '__main__':
    
    quality_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    print "Start summarizing off-targets ..."
    
    ## TESTING
    #quality_dir = "/home/stephan/PycharmProjects/TABSAT/quality"
    #output_file = "/home/stephan/PycharmProjects/TABSAT/quality/01_targets_combined.csv"
    
    if not os.path.exists(quality_dir):
        print "Directory does not exist: " + str(quality_dir)
        sys.exit(1)
    
    summarize(quality_dir, output_file)
    
    
    print "Finished summarizing off-targets."




