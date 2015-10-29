#/usr/bin/python

import csv
import json
import sys
import glob
import os
import base64
from zipfile import ZipFile
from collections import defaultdict


class TabsatOutput:

    def _get_subpop_to_name(self, subpopulation_directory, sample_name):
        subpop_files = glob.glob(os.path.join(subpopulation_directory, "*" + sample_name + "*FinalSubpop.txt"))

        if subpop_files:
            return insert_spacer_file_path(subpop_files[0], "subpopulations")

    def _get_qc_to_name(self, qc_directory, sample_name):
        qc_files = glob.glob(os.path.join(qc_directory, "*" + sample_name + "*.html"))

        if qc_files and len(qc_files) > 1:
            qc_files_sorted = sorted(qc_files)
            return (insert_spacer_file_path(qc_files_sorted[0], "qc"),insert_spacer_file_path(qc_files_sorted[1], "qc"))

    def _get_idxstats_to_name(self, idx_directory, sample_name):
        idx_files = glob.glob(os.path.join(idx_directory, "*" + sample_name + "*.idxstats"))

        if idx_files:
            return insert_spacer_file_path(idx_files[0], "idxstats")

    def _add_to_sample_dict(self, row, field, the_field_name, subpopulation_directory, qc_directory, idx_directory):
        if field.startswith(the_field_name):
            sample = field.strip(the_field_name)
            self.sample_dict[sample][the_field_name] = row[field]

            ## Also add subpopulation plot if not already present for this sample
            if "subpopulations_path" not in self.sample_dict[sample]:
                self.sample_dict[sample]["subpopulations_path"] = self._get_subpop_to_name(subpopulation_directory, sample)

            if "qc_before_path" not in self.sample_dict[sample]:
                self.sample_dict[sample]["qc_before_path"] = self._get_qc_to_name(qc_directory, sample)[0]
            if "qc_after_path" not in self.sample_dict[sample]:
                self.sample_dict[sample]["qc_after_path"] = self._get_qc_to_name(qc_directory, sample)[1]

            if "idxstats_path" not in self.sample_dict[sample]:
                self.sample_dict[sample]["idxstats_path"] = self._get_idxstats_to_name(idx_directory, sample)


    def __init__(self, row, plot_directory, subpopulation_directory, qc_directory, idx_directory, zip_file_path):
        self.name = row["Name"]
        self.chr = row["chr"]
        self.start = row["start"]
        self.end = row["end"]
        self.pos = row["Pos"]
        self.zip_file = insert_spacer_file_path(zip_file_path, None)

        ## To each sample properties are stored
        self.sample_dict = defaultdict(dict)

        for field in row:
            self._add_to_sample_dict(row, field, "Reads % ME_", subpopulation_directory, qc_directory, idx_directory)
            self._add_to_sample_dict(row, field, "Reads UM_", subpopulation_directory, qc_directory, idx_directory)
            self._add_to_sample_dict(row, field, "Reads ME_", subpopulation_directory, qc_directory, idx_directory)


        ## Append the plot information
        file_prop, file_adapt = get_plots_to_name(plot_directory, row["Name"])

        self.file_prop = insert_spacer_file_path(file_prop, "plots")
        self.file_adapt = insert_spacer_file_path(file_adapt, "plots")




    def get_json_dump(self):
        json_dict = dict()
        json_dict["Name"] = self.name
        json_dict["Chr"] = self.chr
        json_dict["Start"] = self.start
        json_dict["End"] = self.end
        json_dict["Pos"] = self.pos
        json_dict["Zip"] = self.zip_file

        ## Create list of samples
        sample_list = list()
        for sample_name in sorted(self.sample_dict):
            sample_dict = self.sample_dict[sample_name]
            sample_dict["Name"] = sample_name

            sample_list.append(sample_dict)

        json_dict["Samples"] = sample_list

        json_dict["pdf_proportional_path"] = self.file_prop
        json_dict["pdf_adapted_path"] = self.file_adapt

        #json_dict["pdf_proportional"] = encode_pdf_base64(self.file_prop)
        #json_dict["pdf_adapted"] = encode_pdf_base64(self.file_adapt)

        return json_dict




def insert_spacer_file_path(the_file, the_folder):
    if not the_file:
        return the_file

    basename = os.path.basename(the_file)

    if the_folder:
        return os.path.join("$$$_SPACER_$$$", the_folder, basename)
    else:
        return os.path.join("$$$_SPACER_$$$", basename)



def get_plots_to_name(plot_directory, name):

    files = glob.glob(os.path.join(plot_directory, "*" + name + ".pdf.png"))

    ## DEBUG
    #print "Getting plots to name"
    #print "plot_directory: " + str(plot_directory)
    #print "name: " + str(name)
    #print "files: " + str(files)

    file_prop = None
    file_adapt = None

    for the_file in files:
        if "proportional" in the_file:
            file_prop = the_file
        if "adapted" in the_file:
            file_adapt = the_file

    return file_prop, file_adapt





def encode_pdf_base64(file_path):

    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            return base64.b64encode(fh.read()).decode('ascii')

    return None


def create_zip_of_output(plot_directory, subpopulation_directory, qc_directory, final_table, final_bed):

    ## All plots
    plots = glob.glob(os.path.join(plot_directory, "*.pdf"))
    ## Final subpop file
    final_subpops = glob.glob(os.path.join(subpopulation_directory, "*FinalSubpop.txt"))
    ## Final sample comparison
    sample_comp_subpops = glob.glob(os.path.join(subpopulation_directory, "*SampleComparision*"))
    ## QC files
    qc_files = glob.glob(os.path.join(qc_directory, "*html"))

    zip_file_path = "final.zip"

    with ZipFile(zip_file_path, "w") as my_zip:
        for plot in plots:
            my_zip.write(plot)

        for final_subpop in final_subpops:
            my_zip.write(final_subpop)

        for sample_comp_subpop in sample_comp_subpops:
            my_zip.write(sample_comp_subpop)

        for qc_file in qc_files:
            my_zip.write(qc_file)

        my_zip.write(final_table)
        my_zip.write(final_bed)


    return zip_file_path





def do(final_table, plot_directory, subpopulation_directory, qc_directory, idx_directory, zip_file_path):

    print "Creating final JSON file from " + str(final_table) + " using plot directory: '" + \
          str(plot_directory + "' and subpop dir: '" + str(subpopulation_directory)) + "'"

    header_line = []

    ## First get fieldnames == header of row
    with open (final_table, "r") as csv_file:
        header_line = csv.reader(csv_file).next()


    with open("final_output.json", "w") as json_file, open(final_table, "r") as csv_file:

        ## Count the number of lines
        count_reader = csv.DictReader(csv_file)

        ## Skip the heade
        count_reader.next()

        total_rows = 0
        for row in count_reader:
          total_rows += 1

        ## Reset the file
        csv_file.seek(0)  # You may not have to do this, I didn't check to see if DictReader did


        ## Actual reader
        reader = csv.DictReader(csv_file, header_line)

        ## Skip header
        reader.next()

        ## Begin the list
        json_file.write("[")

        ## Dump the file
        count = 0
        for row in reader:

            ## Build the Tabsat Output
            tso = TabsatOutput(row, plot_directory, subpopulation_directory, qc_directory, idx_directory, zip_file_path)

            ## Dump it into the JSON file
            json.dump(tso.get_json_dump(), json_file)

            ## Write the JSON file - split by ","
            if count < total_rows:
                json_file.write(",\n")
            else:
                json_file.write("\n")

            count += 1


        ## End the list
        json_file.write("]")


    print "Done creating final_output.json file ."


def create_report_config_json():
    ## Create the "report_config.json" -> which references the final output json file
    with open("report_config.json", "w") as rcj:
        rcj.write("{\"files\": [\"final_output.json\"]}\n")

    print "Done creating report_config.json ."


def main():

    if len(sys.argv) < 6:
        print "Not enough argument provided. Required: <final_table> <plots dir> <subpop dir>"
        sys.exit()

    final_table = sys.argv[1]

    if not os.path.exists(final_table):
        print "Final table does not exist: " + str(final_table)
        sys.exit()

    plot_directory = sys.argv[2]

    if not os.path.exists(plot_directory):
        print "Plot directory does not exist: " + str(final_table)
        sys.exit()

    subpopulation_directory = sys.argv[3]

    if not os.path.exists(subpopulation_directory):
        print "Subpopulation directory does not exist: " + str(final_table)
        sys.exit()

    qc_directory = sys.argv[4]
    if not os.path.exists(qc_directory):
        print "QC directory does not exist: " + str(final_table)
        sys.exit()


    idx_directory = sys.argv[5]
    if not os.path.exists(idx_directory):
        print "Idxstats directory does not exist: " + str(final_table)
        sys.exit()

    final_bed = sys.argv[6]

    ## Create the ZIP file
    zip_file_path = create_zip_of_output(plot_directory, subpopulation_directory, qc_directory, final_table, final_bed)

    ## Call the script
    do(final_table, plot_directory, subpopulation_directory, qc_directory, idx_directory, zip_file_path)

    ## Create the report config json -> needed for the report
    create_report_config_json()




if __name__ == "__main__":
    main()

    ## TESTING
    #do("ResultMethylListOnlyReferenceCpGs.csv", ".", "subpop")