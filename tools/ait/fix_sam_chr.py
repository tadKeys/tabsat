import sys
import shutil

## Input parameters
my_sam_file=sys.argv[1]
my_sam_file_fixed=sys.argv[2]

## Check if something needs to be done
needs_to_be_fixed = False
with open(my_sam_file) as msf:
    for line in msf:
	line = line.strip()
	if line.startswith("@"):
	    continue
	else:
	    ## Check 3 column
	    sline = line.split("\t")
	    if "chr" not in sline[2]:
		needs_to_be_fixed = True
		break

if not needs_to_be_fixed:
    print("No Fix needed -> copying")
    shutil.copy(my_sam_file, my_sam_file_fixed)
    sys.exit()

print("Fix needed")

all_chrs = map(str, range(1,23))
all_chrs.extend(["MT", "X", "Y", "m"])
#print(all_chrs)

with open(my_sam_file) as msf, open(my_sam_file_fixed, "w") as msf_fixed:
    for line in msf:
	#print(line)
	line = line.strip()
	if line.startswith("@SQ"):
	    sline = line.split("\t")
	    for cur_chr in all_chrs:
		if sline[1] == "SN:"+cur_chr:
		    sline[1] = "SN:chr"+cur_chr
		    break
	    msf_fixed.write("\t".join(sline)+"\n")
	elif not line.startswith("@"):
	    sline = line.split("\t")
	    sline[2] = "chr" + sline[2] 
	    msf_fixed.write("\t".join(sline)+"\n")
	else:
	    msf_fixed.write(line)


print("Done fixing the SAM file")


