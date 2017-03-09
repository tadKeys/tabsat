#!/usr/bin/env python2

import os
import glob
import csv
import sys
from collections import defaultdict


def combine_stats(idx_dir, output_file):
    idx_files = glob.glob(os.path.join(idx_dir, "*.idxstats"))

    chr_dict = defaultdict(list)


    ## Read in the idx files
    for idx_file in idx_files:
        with open(idx_file) as idx_fh:
            chr_dict["header"].append(os.path.basename(idx_file))

            for row in csv.reader(idx_fh, delimiter="\t"):
                chr = row[0]
                coverage = row[2]


                chr_dict[chr].append(coverage)


    ## Output the combined idx files
    with open(output_file, "w") as of:
        csv_writer = csv.writer(of, delimiter="\t")

        ## Build list of chromosomes to output
        chr_1_22 = list()
        for i in range(1, 23):
            chr_1_22.append("chr" + str(i))
        chr_1_22.extend(["chrM", "chrX", "chrY"])


        ## Write the header row
        header_row = ["Chrom"]
        header_row.extend(chr_dict["header"])
        csv_writer.writerow(header_row)


        ## Write coverage of files
        for chr in chr_1_22:
            row = [chr]

            for cov in chr_dict[chr]:
                row.append(cov)

            csv_writer.writerow(row)




def main():
    if len(sys.argv) < 3:
        print "Not enough arguments - run: python combine_idx_stats.py <idx_dir> <output_file>"
        sys.exit()

    idx_dir = sys.argv[1]
    output_file = sys.argv[2]

    combine_stats(idx_dir, output_file)

if __name__ == "__main__":
    main()


## Testing
#combine_stats("/home/stephan/work/bisulfiteseq_2016_01_17/run1/idxstats", "/home/stephan/work/bisulfiteseq_2016_01_17/run1/idxstats/coverage_summary.csv")









