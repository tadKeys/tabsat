#!/usr/bin/python

import csv
import sys

if not len(sys.argv) > 1:
    print "Please pass the 'final table' and the output 'final bed' to the script"
    sys.exit()

final_table = sys.argv[1]
final_bed = sys.argv[2]

print "Converting table: " + str(final_table)

with open(final_table) as ft, open(final_bed, "w") as fb:

    header_processed = False
    sample_pos_dict = dict()

    for row in csv.reader(ft, delimiter=","):
	
	if not header_processed:
	    ## Store sample information in dict
	    count = 0
	    for column in row:
		if count > 5 and (count + 1) % 3 == 0:
		    sample_pos_dict[count] = column.split()[2]
		count += 1

	    header_processed = True
	    continue


	output_row = []
	output_row.append(row[1])
	output_row.append(str(int(row[5])-1))
	output_row.append(str(int(row[5])))

	## Get all samples with a valid % methylation for that position
	samples_with_value_at_pos = list()
	for index in sample_pos_dict:
	    if row[index] and row[index] != "-" and row[index] != "":
		samples_with_value_at_pos.append(sample_pos_dict[index])

	output_row.append(",".join(samples_with_value_at_pos))

	    
	fb.write("\t".join(output_row) + "\n")
