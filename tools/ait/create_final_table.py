#!/usr/bin/python
import csv
import glob
import re
import shutil
import numpy
import os
import os.path
import sys


## set how many reads are needed at each position to trust methylation call
read_cutoff=0

## how many reads are needed to pass hard cutoff
cov_sum_cutoff=4
cov_pos_cutoff=2

## file containing all cpgs
file_all_cgps = os.environ['HOME'] + "/tabsat/tools/ait/all_cpgs_only_pos.txt"


#
# gets all results (.cov) files from Bismark
# 
#
#
def prepareInitalList(file_initial_list, dir_cov_file):
    # write results into MethyList
    with open(dir_cov_file + "/MethylList.csv", "w") as w:
	writer = csv.writer(w)
        with open (file_initial_list) as csvfile:
	    header_printed = 0
	    csvreader = csv.reader(csvfile, delimiter='\t')
	    for m_line in csvreader:
		if (not header_printed):
		    m_line.append("Pos")
		    writer.writerow(m_line)
		    header_printed = 1
		else:
	    	    pos_list = list()     # store positions to avoid duplicates
		    m_chr = m_line[1]     # chromosome of target region
		    m_start = m_line[2]   # start      of target region
		    m_end = m_line[3]     # end        of target region
		    #print "m: %s, %s, %s " % (m_chr, m_start, m_end)
		    all_cov_files = getInputCovFiles(dir_cov_file)  # get all bismark result files
		    for cov_file in all_cov_files:
			with open (cov_file) as f:
			    for f_line in f.readlines(): # go over each line in result file
				f_line_split = f_line.strip().split()
				f_chr = f_line_split[0]
				f_pos = f_line_split[1]
				#print "f_pos: " + str(f_pos)
				#print "pos_list: " + str(pos_list)
				if (f_pos not in pos_list):
				    if (f_chr == m_chr):
					if (f_pos >= m_start and f_pos <= m_end):
					    pos_list.append(f_pos)

		    #print lines with positions
		    #print "pos_list: " + str(pos_list)
		    for pos in pos_list:
		        m_line_cp = list(m_line)
		        m_line_cp.append(pos)
		        writer.writerow(m_line_cp)





##
## Open a bismark coverage file
## Search for entry at specific chromosome (m_chr) and position (m_pos)
## Returns %methylated, reads methylated, reads unmethylated
##
def processLine(m_chr, m_pos, cov_file):
    with open (cov_file) as f:
	for f_line in f.readlines():
	    f_line_split = f_line.strip().split()
	    f_chr = f_line_split[0]
	    f_pos = f_line_split[1]
	    f_percent = f_line_split[3]
	    f_count_meth = f_line_split[4]
	    f_count_not_meth = f_line_split[5]
	    if (f_chr == m_chr and f_pos == m_pos):
		#print "found: " + str(f_percent) + " --- " + str(f_count_meth)
		return str(round(float(f_percent),2)), f_count_meth, f_count_not_meth
    return "-", "-", "-"



##
## Reads the Result file that has been created so far (has been copied in previous step)
## Appends new results from cov_file to each row
##
def createEntriesForSample(dir_cov_file, cov_file):
    count = 0
    with open(dir_cov_file + "/ResultMethylList.csv", "w") as w:
	writer = csv.writer(w)
	with open (dir_cov_file + "/MethylList.csv") as csvfile:
    	    csvreader = csv.reader(csvfile, delimiter=',')
	    header_printed = 0
	    for m_line in csvreader:
		if (not header_printed):
		    sampleName = getNameFromCovFile(cov_file)
		    m_line.append("Reads ME_" + sampleName)
		    m_line.append("Reads UM_" + sampleName)
		    m_line.append("Reads % ME_" + sampleName)
		    writer.writerow(m_line)
		    header_printed = 1
		else:
		    #print m_line
		    m_chr = m_line[1]
		    m_start = m_line[2]
		    m_end = m_line[3]
		    m_pos = m_line[4]
		    r_percent, r_count_meth, r_count_not_meth = processLine(m_chr, m_pos, cov_file)
		    #print r_percent
		    #print r_count_meth
		    #print r_count_not_meth
		    #print ""
		    #check if cutoff is met
		    sumReads = 0
		    if (r_count_meth != "-"):
			sumReads = sumReads + int(r_count_meth)
		    if (r_count_not_meth != "-"):
			sumReads = sumReads + int(r_count_not_meth)
		    if (sumReads >= read_cutoff):
			m_line.append(r_count_meth)
			m_line.append(r_count_not_meth)
			m_line.append(r_percent)
		    else:
			#print "Position did not meet cutoff --- pos: " + m_pos + ", #methyl: " + r_count_meth + ", #not_methyl: " + r_count_not_meth + ", percent: " + r_percent
			m_line.append("-")
			m_line.append("-")
			m_line.append("-")
		    writer.writerow(m_line)
#		    if (count < 1):
#			count = count + 1
#		    else:
#		        break


def removeLineWithoutReport(output_file, input_file):
    with open(output_file, 'w') as w:
	writer = csv.writer(w)
	with open (input_file) as csvfile:
	    csvreader = csv.reader(csvfile, delimiter=',')
	    for m_line in csvreader:
		all_missing = 1
		for field in m_line[6:]:
		    if field != "-":
			all_missing = 0
		#print str(m_line) + ": " + str(all_missing)
		if (not all_missing):
		    writer.writerow(m_line)


##
## Creates entries for all cov files (adds them as columns)
##
def createEntriesForAllCovFiles(dir_cov_file):
    all_cov_files = getInputCovFiles(dir_cov_file)
    for cov_file in all_cov_files:
        createEntriesForSample(dir_cov_file, cov_file)	
	shutil.copyfile(dir_cov_file + "/ResultMethylList.csv", dir_cov_file + "/MethylList.csv")  #copy result file - to be new input file



def getInputCovFiles(dir_cov_file):
    return sorted(glob.glob(dir_cov_file + "/*.cov"))

def getNameFromCovFile(cov_file):
    cov_file_base = os.path.basename(cov_file)
    print "cov_file_base: " + str(cov_file_base)
    m = re.search("PGM_\d+._IonXpress_(\d+)_1(_trimmed)+.fastq_bismark_\w+.bismark.cov", cov_file_base)

    return m.group(1)
    #PGM_316D_IonXpress_032_1_trimmed_trimmed.fastq_bismark_tmap.bismark.cov


##
## Removes calls with a low coverage
## Uses given threshold for "hard" clipping
## Calculates average per gene/sample -> clips everything below (mean - stddev)
##
def filterLowCovCalls(result_file, filtered_file):
    
    sample_cov = dict()
    oligo_pos = dict()		# number of positions per oligo

    with open(result_file, 'r') as r:
	csvreader = csv.reader(r, delimiter=",")
	
	header_printed = 0
	for m_line in csvreader:
	    # Skip header line
	    if (not header_printed):
		header_printed = 1
		continue

	    #print m_line

	    sample_index = 0

	    oligo = m_line[0]
	    if (oligo in oligo_pos):
		oligo_pos[oligo] += 1
	    else:
		oligo_pos[oligo] = 1

	    ## Index where to start
	    i = 5
	    while (i < len(m_line)):
		## Methylated reads
		me_r = m_line[i]
		
		## Unmethylated reads
		i += 1
		um_r = m_line[i]

		## Skip percentage
		i += 1

		## Add to array
		key = oligo + "_" + str(sample_index)
		if (not key in sample_cov):
		    sample_cov[key] = list()
		
		## Build average
		if me_r != "-" and um_r != "-":
		    sum_cov = float(me_r) + float(um_r)
		    #print int(me_r)
		    #print int(um_r)
		    avg_at_pos = float(sum_cov) / 2
		    #print avg_at_pos

		    ## Don't add if sum_cov is < cov_sum_cutoff (default 4)
		    ## Don't trust calls where max cov_pos_cutoff (default 2) reads where used

		    #print "me_r " + str(me_r)
		    #print "um_r " + str(um_r)

		    if (sum_cov > cov_sum_cutoff or (int(me_r) > cov_pos_cutoff and int(um_r) > cov_pos_cutoff)):
			sample_cov[key].append(avg_at_pos)

		#if me_r != "-":
		#    sample_cov[key].append(int(me_r))
		#if um_r != "-":
		#    sample_cov[key].append(int(um_r))


		#print i
		#print me_r
		#print um_r

		i += 1
		sample_index += 1




    with open(result_file, 'r') as r:
	csvreader = csv.reader(r, delimiter=",")
	with open(filtered_file, 'w') as w:
	    writer = csv.writer(w)

	    header_printed = 0

	    for m_line in csvreader:
		if (not header_printed):
		    header_printed = 1
		    writer.writerow(m_line)
		    continue


		oligo = m_line[0]
		sample_index = 0

		## Index where to start
		i = 5
		me_index = 0
		um_index = 0
		perc_index = 0
		while (i < len(m_line)):
		    ## Methylated reads
		    me_index = i
		    me_r = m_line[i] if m_line[i] != "-" else 0

		    ## Unmethylated reads
		    i += 1
		    um_index = i
		    um_r = m_line[i] if m_line[i] != "-" else 0
		
		    ## Skip percentage
		    i += 1
		    perc_index = i

		    ##
		    ## Check if reads have sufficient coverage
		    ##
		    sum_cov = float(me_r) + float(um_r)
		    key = oligo + "_" + str(sample_index)

		    ## Don't trust calls where max 2 reads where used
		    if (sum_cov <= cov_sum_cutoff and (int(me_r) <= cov_pos_cutoff or int(um_r) <= cov_pos_cutoff)):
			m_line[me_index] = "-"
			m_line[um_index] = "-"
			m_line[perc_index] = "-"
			i += 1
			sample_index += 1
			continue

		    
		    #print "\nNew position"
		    ## Average cov for sample at oligo
		    sum_up_cov = 0
		    for val in sample_cov[key]: 
#			print val
			sum_up_cov += int(val)

		    ## Sum of meth & unmeth calls for position
		    sam_oligo_avg_cov = float(float(sum_up_cov) / float(oligo_pos[oligo]))
		    
		    #print "key: " + str(key)
		    #print "sample_cov[key]: " + str(sample_cov[key])
		    #print "sam_oligo_avg_cov: " + str(sam_oligo_avg_cov)
		    #print "mean: " + str(numpy.mean(sample_cov[key]))		# calculate the average only from values that are there (don't use "-")
		    #print "median: " + str(numpy.median(sample_cov[key]))
		    #print "std: " + str(numpy.std(sample_cov[key]))
		    #print "perc: " + str(numpy.percentile(sample_cov[key], 20))
		    
		    
		    #print numpy.percentile(sample_cov[key], 10)
		
		    cutoff_cov = 0
		    if sample_cov[key]:		#Check if values are present
			#cutoff_cov = numpy.percentile(sample_cov[key], 20)				# Percentile cutoff
			cutoff_cov = numpy.mean(sample_cov[key]) - numpy.std(sample_cov[key])		# Mean-std cutoff


		    #print "cutoff_cov: " + str(cutoff_cov)

		    ## Filter low cov positions
		    if (sum_cov < cutoff_cov):
			m_line[me_index] = "-"
			m_line[um_index] = "-"
			m_line[perc_index] = "-"
		    

		    i += 1
		    sample_index += 1


		writer.writerow(m_line)






def filterNotReferenceCpGs(result_file, filtered_file):


    with open(file_all_cgps, "r") as fac:

        all_cpgs_set = set(fac.read().splitlines())


        with open(result_file, "r") as r:
    	    csvreader = csv.reader(r, delimiter=",")
	    with open(filtered_file, 'w') as w:
		writer = csv.writer(w)

		header_printed = 0

		for m_line in csvreader:

		    if (not header_printed):
			header_printed = 1
			writer.writerow(m_line)
			continue

		    
		    chr = m_line[1].strip()
		    pos = m_line[4].strip()
		    
		    search_str = chr + "-" + pos

		    #print search_str

		    ## Only print the line if it's a true cpg
		    if search_str in all_cpgs_set:
			writer.writerow(m_line)

#			print "found"
#		    else:
#			print "NOT found"




##
## MAIN MAIN MAIN
##





print "Generating final output table"

print "- reading cutoff config"

if os.path.isfile("cutoff.cfg"):
    with open ("cutoff.cfg", "r") as r:
	line = r.readline()
	if (line):
	    cov_sum_cutoff = int(line.strip().split("=")[1])
	line = r.readline()
	if (line):
	    cov_pos_cutoff = int(line.strip().split("=")[1])


print "-- cov_sum_cutoff: " + str(cov_sum_cutoff)
print "-- cov_pos_cutoff: " + str(cov_pos_cutoff)



print "- preparing list"

initial_list_file = sys.argv[1]
dir_cov_file = sys.argv[2]

print "- initial_list_file: " + str(initial_list_file)
print "- dir_cov_file: " + str(dir_cov_file)


## Reading hard cutoff value
if len(sys.argv) > 3:
    print "- using the read cutoff specified by the user"
    read_cutoff = int(sys.argv[3])

print "- read_cutoff: " + str(read_cutoff)



prepareInitalList(initial_list_file, dir_cov_file)



print "- creating entries"
createEntriesForAllCovFiles(dir_cov_file)


#now remove entries where nothing has been reported (line consists only of "-")
print "- cleaning result file"
removeLineWithoutReport(dir_cov_file + "/ResultMethylList.csv", dir_cov_file + "/MethylList.csv")


print "- filtering low cov calls"
filterLowCovCalls(dir_cov_file + "/ResultMethylList.csv", dir_cov_file + "/ResultMethylListFiltered.csv")


print "- cleaning filtered result file"
removeLineWithoutReport(dir_cov_file + "/ResultMethylListCleaned.csv", dir_cov_file + "/ResultMethylListFiltered.csv")


print "- keeping only CpGs from reference"
filterNotReferenceCpGs(dir_cov_file + "/ResultMethylListCleaned.csv", dir_cov_file + "/ResultMethylListOnlyReferenceCpGs.csv")


print "- Remove temp files"
os.remove(dir_cov_file + "/ResultMethylListFiltered.csv")


print "Done."

