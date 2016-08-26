#!/usr/bin/python
import csv
import glob
import re
import shutil
import numpy
import os
import os.path
import sys
import datetime
import time
import subprocess
from subprocess import CalledProcessError
from collections import defaultdict


## Default cutoffs
def get_default_cutoffs():
    ## how many reads are needed to pass hard cutoff
    cov_sum_cutoff = 4
    cov_pos_cutoff = 2

    ## set how many reads are needed at each position to trust methylation call
    read_cutoff = 0

    return cov_sum_cutoff, cov_pos_cutoff, read_cutoff






#
# Gets all results (.cov) files from Bismark
# 
#
#
def prepareInitalList(file_initial_list, cov_dir, all_cpg_file_path, read_cutoff):

    strand_information_buffer = dict()

    # Write results into MethyList
    with open(cov_dir + "/MethylList.csv", "w") as w:
        writer = csv.writer(w)
        with open(file_initial_list) as csvfile:

            header_printed = False
            first_pass_of_prefill = True

            for m_line in csv.reader(csvfile, delimiter='\t'):
                if not header_printed:
                    m_line.append("pos")
                    writer.writerow(m_line)
                    header_printed = True
                    continue

                pos_list = list()       # store positions to avoid duplicates
                m_chr = m_line[1]       # chromosome of target region
                m_start = m_line[2]     # start      of target region
                m_end = m_line[3]       # end        of target region
                m_strand = m_line[4]    # strand     of target region (+, -, +/-)

                # print "m: %s, %s, %s " % (m_chr, m_start, m_end)
                for cov_file in getInputCovFiles(cov_dir):      # get all Bismark result files

                    #print "\nReading in file: " + str(cov_file)

                    ## Prefill the buffer to increase speed
                    if first_pass_of_prefill:
                        strand_information_buffer = prefill_strand_information_buffer(strand_information_buffer, cov_file, all_cpg_file_path, read_cutoff)


                    with open(cov_file) as f:

                        for f_line in f.readlines():  # Go over each line in result file
                            f_line_split = f_line.strip().split()
                            f_chr = f_line_split[0]
                            f_pos = f_line_split[1]

                            # print "f_pos: " + str(f_pos)
                            # print "pos_list: " + str(pos_list)

                            if f_pos not in pos_list:

                                if f_chr == m_chr and f_pos >= m_start and f_pos <= m_end:

                                    ## Get strand information to current position
                                    cur_key = str(f_chr) + "-" + str(f_pos)
                                    if cur_key in strand_information_buffer:
                                        ## DEBUG
                                        #print "cur_key in dict: " + str(cur_key)
                                        f_strand = strand_information_buffer[cur_key]
                                    else:
                                        f_strand = get_strand_of_position(cur_key, all_cpg_file_path)
                                        strand_information_buffer[cur_key] = f_strand

                                    ## Check if this position is on the correct strand
                                    if is_correct_strand(m_strand, f_strand):
                                        pos_list.append(f_pos)

                                    ## DEBUG
                                    #else:
                                    #    print "Filtered position as it is not on the correct strand - " + \
                                    #    "target: " + str(m_strand) + " / " + \
                                    #    "ref: " + str(f_strand) + " .... " + \
                                    #    str(f_chr) + ":" + str(f_pos)



                for pos in pos_list:
                    m_line_cp = list(m_line)
                    m_line_cp.append(pos)
                    writer.writerow(m_line_cp)


                first_pass_of_prefill = False


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def prefill_strand_information_buffer(strand_information_buffer, cov_file, all_cpg_file_path, read_cutoff):

    ## Build list of keys
    key_list = list()
    with open(cov_file) as f:

        for line in f.readlines():  # Go over each line in result file
            line_split = line.strip().split()
            chr = line_split[0]
            pos = line_split[1]

            meth = line_split[4]
            un_meth = line_split[5]

            ## Check if min cutoff is fulfilled
            if int(meth) + int(un_meth) < read_cutoff:
                continue

            new_key = chr + "-" + pos

            ## Only add keys were no information is present
            if new_key not in strand_information_buffer:
                key_list.append(chr + "-" + pos)


    print "Prefilling strand information buffer with " + str(len(key_list)) + " items"


    ## Run grep on the CpG file - split into chunks

    awk_result = ""
    for key_list_chunk in chunks(key_list, 1000):

        ## Using AWK instead of grep

        cmd = ["awk"]
        cmd += ["'/" + "\s|".join(key_list_chunk) + "/'"]
        cmd += [all_cpg_file_path]

        ## DEBUG
        #print ""
        #print " ".join(cmd)
        #print ""
        
        
        ## Test with gnu parallel -> not faster
        
        #cmd1 = ["cat"]
        #cmd1 += [all_cpg_file_path]
        #cmd1 += ["|"]
        #cmd1 += ["/home/app/tabsat/tools/gnu_parallel/parallel-20160722/src/parallel"]
        #cmd1 += ["--pipe"]
        #cmd1 += ["awk"]
        #cmd1 += ["\\'\/" + "\\\s\|".join(key_list_chunk) + "\/\\'"]
        
        #print " ".join(cmd1)
        
        
        #gnu_parallel_cmd = "/home/stephan/bin/gnu_parallel/parallel-20160222/src/parallel"
        #ps = subprocess.Popen(["echo", "-e", "\n".join(key_list)], stdout=subprocess.PIPE)
        #grep_result = subprocess.check_output([gnu_parallel_cmd, "--pipe", "-L1000", "--round-robin",
        #                                       "grep", "-F", "-f", "-", all_cpg_file_path], stdin=ps.stdout)
        #ps.wait()
        
        

        tmp_awk_result = subprocess.check_output(" ".join(cmd), shell=True)

        ## DEBUG
        #print tmp_awk_result

        if tmp_awk_result:
            awk_result += tmp_awk_result
        else:
            print "awk result is empty"






    #print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    #print "second"
    #print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    #gnu_parallel_cmd = "/home/stephan/bin/gnu_parallel/parallel-20160222/src/parallel"
    #ps = subprocess.Popen(["echo", "-e", "\n".join(key_list)], stdout=subprocess.PIPE)
    #grep_result = subprocess.check_output([gnu_parallel_cmd, "--pipe", "-L1000", "--round-robin",
    #                                       "grep", "-F", "-f", "-", all_cpg_file_path], stdin=ps.stdout)
    #ps.wait()
    #print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))


    ## DEBUG
    #print key_list
    #print len(key_list)
    #print grep_result

    awk_result_list = awk_result.strip().split("\n")

    ## DEBUG
    #print "awk_result_list: " + str(awk_result_list)

    if not awk_result_list or len(awk_result_list) == 0 or (len(awk_result_list) == 1 and awk_result_list[0] == ""):
        print "awk_result_list is empty"
    else:
        for result in awk_result_list:
            s_result = result.split("\t")

            if s_result[0] not in strand_information_buffer:
                strand_information_buffer[s_result[0]] = s_result[1]


    ## DEBUG
    #print "strand_information_buffer" + str(strand_information_buffer)

    return strand_information_buffer



def perform_grep_with_cur_key(cur_key, all_cpg_file_path):
    
    print "Perform grep with cur key"
    print " ".join(["grep", cur_key, all_cpg_file_path])
    
    return subprocess.check_output(["grep", cur_key, all_cpg_file_path])



def get_strand_of_position(cur_key, all_cpg_file_path):

    ## DEBUG
    #print "get strand of position"
    #print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    #print "\ncur_key: " + str(cur_key)

    #cur_key = "chr10-6221208"
    #cur_key = "chr5-50683248"


    try:
        grep_result = perform_grep_with_cur_key(cur_key, all_cpg_file_path)

        ## DEBUG
        #print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

        ## Split in case multiple elements are found
        grep_result_list = grep_result.strip().split("\n")

        if len(grep_result_list) > 1:
            print "Found multiple elements"
            for ind_grep_result in grep_result_list:
                if ind_grep_result.split("\t")[0] == cur_key:
                    return ind_grep_result.split("\t")[1]

            print "Nothing found in the list: " + str(grep_result_list) + " item: " + str(cur_key)
            return "+/-"

        else:
            return grep_result.strip().split("\t")[1]


    except CalledProcessError as e:
        ## DEBUG
        #print e

        return "+/-"






def is_correct_strand(m_strand, f_strand):
    if m_strand == "+/-" or f_strand == "+/-":
        return True
    else:
        return m_strand == f_strand



##
## Open a bismark coverage file
## Search for entry at specific chromosome (m_chr) and position (m_pos)
## Returns %methylated, reads methylated, reads unmethylated
##
def processLine(m_chr, m_pos, cov_file):
    with open(cov_file) as f:
        for f_line in f.readlines():
            f_line_split = f_line.strip().split()
            f_chr = f_line_split[0]
            f_pos = f_line_split[1]
            f_percent = f_line_split[3]
            f_count_meth = f_line_split[4]
            f_count_not_meth = f_line_split[5]
            if (f_chr == m_chr and f_pos == m_pos):
                # print "found: " + str(f_percent) + " --- " + str(f_count_meth)
                return str(round(float(f_percent), 2)), f_count_meth, f_count_not_meth
    return "-", "-", "-"



##
## Reads the Result file that has been created so far (has been copied in previous step)
## Appends new results from cov_file to each row
##
def createEntriesForSample(cov_dir, cov_file, read_cutoff, mapper):
    count = 0
    with open(cov_dir + "/ResultMethylList.csv", "w") as w:
        writer = csv.writer(w)
        with open(cov_dir + "/MethylList.csv") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header_printed = 0
            for m_line in csvreader:
                if (not header_printed):
                    sampleName = getNameFromCovFile(cov_file, mapper)
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
                    m_strand = m_line[4]
                    m_pos = m_line[5]
                    r_percent, r_count_meth, r_count_not_meth = processLine(m_chr, m_pos, cov_file)
                    # print r_percent
                    # print r_count_meth
                    # print r_count_not_meth
                    # print ""
                    # check if cutoff is met
                    sumReads = 0
                    if r_count_meth != "-":
                        sumReads = sumReads + int(r_count_meth)
                    if r_count_not_meth != "-":
                        sumReads = sumReads + int(r_count_not_meth)
                    if (sumReads >= read_cutoff):
                        m_line.append(r_count_meth)
                        m_line.append(r_count_not_meth)
                        m_line.append(r_percent)
                    else:
                        # print "Position did not meet cutoff --- pos: " + m_pos + ", #methyl: " + r_count_meth + ", #not_methyl: " + r_count_not_meth + ", percent: " + r_percent
                        m_line.append("-")
                        m_line.append("-")
                        m_line.append("-")
                    writer.writerow(m_line)


# if (count < 1):
#			count = count + 1
#		    else:
#		        break


def removeLineWithoutReport(output_file, input_file):
    with open(output_file, 'w') as w:
        writer = csv.writer(w)
        with open(input_file) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for m_line in csvreader:
                all_missing = 1
                for field in m_line[6:]:
                    if field != "-":
                        all_missing = 0
                        # print str(m_line) + ": " + str(all_missing)
                if (not all_missing):
                    writer.writerow(m_line)


##
## Creates entries for all cov files (adds them as columns)
##
def createEntriesForAllCovFiles(cov_dir, read_cutoff, mapper):
    all_cov_files = getInputCovFiles(cov_dir)
    for cov_file in all_cov_files:
        createEntriesForSample(cov_dir, cov_file, read_cutoff, mapper)
        shutil.copyfile(cov_dir + "/ResultMethylList.csv",
                        cov_dir + "/MethylList.csv")  # copy result file - to be new input file


def getInputCovFiles(cov_dir):
    return sorted(glob.glob(cov_dir + "/*.cov"))


def getNameFromCovFile(cov_file, mapper):
    cur_cov_file_basename = os.path.basename(cov_file)
    print "cur_cov_file_basename: " + str(cur_cov_file_basename)

    if mapper == "tmap":
        m = re.search("\w+_\d+._IonXpress_(\d+)_1(_trimmed)+.fastq_bismark_\w+.bismark.cov", cur_cov_file_basename)
        cov_file_name = m.group(1)
    else:
        cov_file_name = cur_cov_file_basename.split("_trimmed")[0]

    print "cov_file name: " + str(cov_file_name)
    return cov_file_name




# PGM_316D_IonXpress_032_1_trimmed_trimmed.fastq_bismark_tmap.bismark.cov


##
## Removes calls with a low coverage
## Uses given threshold for "hard" clipping
## Calculates average per gene/sample -> clips everything below (mean - stddev)
##
def filterLowCovCalls(result_file, filtered_file, cov_sum_cutoff, cov_pos_cutoff):
    sample_cov = defaultdict(list)
    oligo_pos = dict()  # number of positions per oligo

    index_to_start = 6

    with open(result_file, 'r') as r:
        csvreader = csv.reader(r, delimiter=",")

        header_printed = 0
        for m_line in csvreader:
            # Skip header line
            if not header_printed:
                header_printed = 1
                continue

            ## DEBUG
            #print m_line

            sample_index = 0

            oligo = m_line[0]
            if (oligo in oligo_pos):
                oligo_pos[oligo] += 1
            else:
                oligo_pos[oligo] = 1

            ## Index where to start
            i = index_to_start
            while (i < len(m_line)):
                
                ## DEBUG
                #print i
                
                ## Methylated reads
                me_r = m_line[i]

                ## Unmethylated reads
                i += 1
                um_r = m_line[i]

                ## Skip percentage
                i += 1

                ## Build key
                key = oligo + "_" + str(sample_index)

                ## Build average
                if me_r != "-" and um_r != "-":
                    sum_cov = float(me_r) + float(um_r)
                    # print int(me_r)
                    # print int(um_r)
                    avg_at_pos = float(sum_cov) / 2
                    # print avg_at_pos

                    ## Don't add if sum_cov is < cov_sum_cutoff (default 4)
                    ## Don't trust calls where max cov_pos_cutoff (default 2) reads where used

                    # print "me_r " + str(me_r)
                    # print "um_r " + str(um_r)

                    if sum_cov > cov_sum_cutoff or (int(me_r) > cov_pos_cutoff and int(um_r) > cov_pos_cutoff):
                        sample_cov[key].append(avg_at_pos)

                    # print i
                    # print me_r
                    # print um_r

                i += 1
                sample_index += 1


    ## Apply average filter
    with open(result_file, 'r') as r, open(filtered_file, 'w') as w:
        csvreader = csv.reader(r, delimiter=",")
        writer = csv.writer(w)

        header_printed = 0

        for m_line in csvreader:
            if not header_printed:
                header_printed = 1
                writer.writerow(m_line)
                continue

            oligo = m_line[0]
            sample_index = 0

            ## Index where to start
            i = index_to_start
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

                ## Don't trust calls where 'cutoff value' reads where used
                if sum_cov <= cov_sum_cutoff and (int(me_r) <= cov_pos_cutoff or int(um_r) <= cov_pos_cutoff):

                    print "Sample " + key + " does not have enough coverage for hard cutoff or me/um cutoff:"
                    print "sum_cov: " + str(sum_cov) + "/" + str(cov_sum_cutoff)
                    print "ME: " + str(int(me_r)) + "/" + str(cov_pos_cutoff)
                    print "UM: " + str(int(um_r)) + "/" + str(cov_pos_cutoff)

                    m_line[me_index] = "-"
                    m_line[um_index] = "-"
                    m_line[perc_index] = "-"
                    i += 1
                    sample_index += 1
                    continue




                ## DEBUG
                #print "key: " + str(key)
                #print "sample_cov[key]: " + str(sample_cov[key])
                # print "mean: " + str(numpy.mean(sample_cov[key]))		# calculate the average only from values that are there (don't use "-")
                # print "median: " + str(numpy.median(sample_cov[key]))
                # print "std: " + str(numpy.std(sample_cov[key]))
                # print "perc: " + str(numpy.percentile(sample_cov[key], 20))
                # print numpy.percentile(sample_cov[key], 10)


                ## Calculate the cutoff value
                cutoff_cov = 0
                if sample_cov[key]:  # Check if values are present
                    # cutoff_cov = numpy.percentile(sample_cov[key], 20)				# Percentile cutoff
                    cutoff_cov = numpy.mean(sample_cov[key]) - numpy.std(sample_cov[key])  # Mean-std cutoff



                #print "cutoff_cov: " + str(cutoff_cov)
                #print "sum_cov: " + str(sum_cov)

                ## Filter low cov positions
                if sum_cov < cutoff_cov:

                    print "\nRemoving sample because of cutoff cov"
                    print "key: " + str(key)
                    print "sample_index: " + str(sample_index)
                    print "i: " + str(i)
                    print "sample_cov[key]: " + str(sample_cov[key])
                    print "cutoff_cov: " + str(cutoff_cov)
                    print "sum_cov: " + str(sum_cov)

                    m_line[me_index] = "-"
                    m_line[um_index] = "-"
                    m_line[perc_index] = "-"

                i += 1
                sample_index += 1

            writer.writerow(m_line)


def filterNotReferenceCpGs(result_file, filtered_file, all_cpg_file_path):

    with open(result_file, "r") as r, open(filtered_file, 'w') as w:
        csvreader = csv.reader(r, delimiter=",")

        writer = csv.writer(w)

        header_printed = 0
        for m_line in csvreader:

            if not header_printed:
                header_printed = 1
                writer.writerow(m_line)
                continue

            chr = m_line[1].strip()
            pos = m_line[5].strip()

            cur_key = chr + "-" + pos

            try:
                perform_grep_with_cur_key(cur_key, all_cpg_file_path)
                ## No error -> position is in file
                writer.writerow(m_line)

            except CalledProcessError as e:
                print "Removing key: " + str(cur_key)






##
## MAIN MAIN MAIN
##
def main_method(target_list, cov_dir, usr_read_cutoff, all_cpg_file_path, mapper):
    print "\n***** Generating final output table (Python) *****"

    ## Default cutoffs
    cov_sum_cutoff, cov_pos_cutoff, read_cutoff = get_default_cutoffs()

    if usr_read_cutoff:
        read_cutoff = usr_read_cutoff

    ## Read cutoff config
    print "- reading cutoff config"
    if os.path.isfile("cutoff.cfg"):
        with open("cutoff.cfg", "r") as r:
            line = r.readline()
            if line:
                cov_sum_cutoff = int(line.strip().split("=")[1])
            line = r.readline()
            if line:
                cov_pos_cutoff = int(line.strip().split("=")[1])

    print "-- cov_sum_cutoff: " + str(cov_sum_cutoff)
    print "-- cov_pos_cutoff: " + str(cov_pos_cutoff)
    print "-- read_cutoff: " + str(read_cutoff)



    print "- preparing list"
    print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    prepareInitalList(target_list, cov_dir, all_cpg_file_path, read_cutoff)
    print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    print "- creating entries"
    createEntriesForAllCovFiles(cov_dir, read_cutoff, mapper)

    # Now remove entries where nothing has been reported (line consists only of "-")
    print "- cleaning result file"
    removeLineWithoutReport(cov_dir + "/ResultMethylList.csv", cov_dir + "/MethylList.csv")

    print "- filtering low cov calls"
    filterLowCovCalls(cov_dir + "/ResultMethylList.csv", cov_dir + "/ResultMethylListFiltered.csv", cov_sum_cutoff, cov_pos_cutoff)

    print "- cleaning filtered result file"
    removeLineWithoutReport(os.path.join(cov_dir, "ResultMethylListCleaned.csv"),
                            os.path.join(cov_dir, "ResultMethylListFiltered.csv"))

    print "- keeping only CpGs from reference"

    filterNotReferenceCpGs(os.path.join(cov_dir, "ResultMethylListCleaned.csv"),
                           os.path.join(cov_dir, "ResultMethylListOnlyReferenceCpGs.csv"),
                           all_cpg_file_path)

    print "- Remove temp files"
    os.remove(cov_dir + "/ResultMethylListFiltered.csv")

    print "- Final output file: " + str(os.path.join(cov_dir, "ResultMethylListOnlyReferenceCpGs.csv"))

    print "Done."




def check_target_list(target_list):
    
    print "- checking the target list"
    
    if not os.path.exists(target_list):
        print "- target_list not present: " + str(target_list)
        sys.exit(1)
        
    with open(target_list) as tl:
        header = ["Name", "chr", "start", "end", "strand"]
        
        checked_header = False
        for line in tl:
            s_line = line.split("\t")
            
            line = line.strip()
            
            ## Check line length
            if len(s_line) != 5:
                print "- wrong number of columns in target file line: " + str(s_line)
                sys.exit(1)
            
            
            ## Split again with strip
            s_line = line.strip().split("\t")
            
            if not checked_header:
                if s_line != header:
                    print "- header is not ok for target file: " + str(s_line) + " - should be: " + "\t".join(header)                    
                    sys.exit(1)
                    
                checked_header = True
                

    print "- target list is ok"

    return "ok"




if __name__ == '__main__':

    ## Reading inputs
    target_list = sys.argv[1]
    cov_dir = sys.argv[2]
    mapper = sys.argv[3]
    cpg_file_path = sys.argv[4]

    print "- target_list: " + str(target_list)
    print "- cov_dir: " + str(cov_dir)
    print "- mapper: " + str(mapper)
    print "- cpg_file_path: " + str(cpg_file_path)


    ## Check the target list    
    check_target_list(target_list)


    usr_read_cutoff = None
    ## Reading hard cutoff value
    if len(sys.argv) > 5:
        usr_read_cutoff = int(sys.argv[5])
        print "- using the read cutoff specified by the user: " + str(usr_read_cutoff)


    main_method(target_list, cov_dir, usr_read_cutoff, cpg_file_path, mapper)



## testing
#if __name__ == '__main__':
#    t_test_dir = os.path.join(os.path.dirname(__file__), "test_create_final_table")
#    t_target_list = os.path.join(t_test_dir, "target_list.csv")
#    t_cov_dir = os.path.join(t_test_dir, "COV_DIR")
#    t_all_cpg_dir = os.path.join(t_test_dir, "/home/stephan/PycharmProjects/TABSAT/test_create_final_table/all_cpgs_only_pos.txt")
#    main_method(t_target_list, t_cov_dir, None, t_all_cpg_dir)