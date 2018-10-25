#!/bin/bash

usage () {
    echo "usage: $0 -i <path to SampleComparison.txt> -s <sample directory>"
}

echo -e "\nPreparing SampleComparison for Patternmap"

#Filerting of parameters
while getopts "hi:s:t:a:" option; do
    case "$option" in
	h) usage
	   exit 0 ;;
	i) INDIR=${OPTARG} ;;
	s) SAMPLEDIR=${OPTARG} ;;
	t) TARGET_LIST=${OPTARG} ;;
	a) ALIGNER=${OPTARG} ;;
	?) echo "Error: unknown option $OPTARG"
	   usage
	   exit 1;;
    esac
done

TMP_CUR_DIR=`dirname $0`
TMP_TABSAT_SCRIPT="$TMP_CUR_DIR/../../tabsat"
TMP_ABS_TABSAT_SCRIPT=`readlink -f $TMP_TABSAT_SCRIPT`
BASE_DIR=`dirname $TMP_ABS_TABSAT_SCRIPT`

HOMEDIR="${BASE_DIR}/tools/Patternmap"
OUTDIR="${INDIR}/Patternmap"
SAMPLE_C="${INDIR}/COVERAGE_NONDIR_${ALIGNER}/MethylSubpopulations/Output/SampleComparison.txt"

echo "INDIR: ${INDIR}"
echo "OUTDIR: ${OUTDIR}"

## Create output dir
mkdir -p $OUTDIR

## CD into output directory
cd $OUTDIR

## Copy the positions file
echo "cp $SAMPLE_C $OUTDIR/All_targets.txt"
cp $SAMPLE_C $OUTDIR/All_targets.txt

## Get the input files
ls ${SAMPLEDIR}/*fastq | awk -F/ '{print $NF}' > sample.list


sed -i ' s/Z/1/g; s/z/0/g ' All_targets.txt  #ALLE zZ werden geändert
sample_count=$(wc -l < sample.list)

## Create target lists
echo "---- Crete target lists in patternmap"
while read line; do
	if [[ $line == Target* ]]; then
		target=$(echo $line | cut -d ";" -f 1 | sed s/" "/"_"/g)
		echo $line > "$target".target
	else
		echo $line >> "$target".target
	fi
done < All_targets.txt

## Delete targets with no patterns and create sample specific target files
a=1
for i in *target; do
	a=$(($a+1))
	target_nm=$(cut -f 1 ${TARGET_LIST} | sed "$a q;d")
	TARGET_NAME=$(echo "$i" | cut -f 1 -d ".") 
	lines=$(wc -l $i | cut -d " " -f1)	
	if [[ $lines == 3 ]]; then
		rm $i
	else 
		awk -F '[;]' -v target=$target_nm '{if ($1 ~ /^Target/) print "\""target"\":{\"chrom\":\""$2"\",\"chrom_pos\":\""$3"\",\"samples\":["}' OFS='' $i > ${TARGET_NAME}.json

		START_POS=$(grep "^Target" $i | cut -f 4 -d ";" | cut -f 1 -d "-")
		END_POS=$(grep "^Target" $i | cut -f 4 -d ";" | cut -f 2 -d "-")
		for c in $(seq 1 $sample_count); do
			NAME=$(sed -n "$c"p sample.list | cut -f 1 -d ".")
			echo -e "Position" $(seq ${START_POS} ${END_POS}) | sed 's/ /\t/g' > ${NAME}.${TARGET_NAME}.target	
			more +3 $i | awk -v var=$c -F ' ' '{print $var, $NF} '| sed '/^0/d; s/\./ 2 /g'| tr -s ' ' | sort -r -t" " -nk1 >> ${NAME}.${TARGET_NAME}.target
			count=$(awk '{sum += $1} END {print sum}' ${NAME}.${TARGET_NAME}.target)
			if [[ $count == "0" ]]; then
				rm ${NAME}.${TARGET_NAME}.target
			fi
		done
	total_samples=$(ls | grep ".${TARGET_NAME}.target" | cut -f 1 -d "." | tr '\n' "," | sed s/.$// | sed s/,/\",\"/ )
	echo "\"$total_samples\"]" >> ${TARGET_NAME}.json
	fi	
done

rm Target*.target
rm sample.list
rm All_targets.txt

for file in *.target; do
############# Alle Positionen ohne Wert (unknown) werden entfernt ##################
	awk '
	{ 
		for (i=1; i<=NF; i++)  {
		    a[NR,i] = $i
		}
	}
	NF>p { p = NF }
	END {    
		for(j=1; j<=p; j++) {
		    str=a[1,j]
		    for(i=2; i<=NR; i++){
		        str=str" "a[i,j];
		    }
		    print str
		}
	}' $file > $file.transponse.target

#entfernt alle Positionen die keine C's beinhalten (codiert als 2)

	while read line; do
		count=$(echo $line | grep -o " 2" | wc -l)
		positions=$(echo $line | wc -w)
		position_count=$(( $positions - 1 ))
		if [ "$count" != "$position_count" ]; then
			echo $line >> $file.trshld.target
		fi 
	done < $file.transponse.target

	awk '
	{ 
		for (i=1; i<=NF; i++)  {
		    a[NR,i] = $i
		}
	}
	NF>p { p = NF }
	END {    
		for(j=1; j<=p; j++) {
		    str=a[1,j]
		    for(i=2; i<=NR; i++){
		        str=str" "a[i,j];
		    }
		    print str
		}
	}' $file.trshld.target > $file.transponse.target

############ Deleted positions #########################

	sed -i 's/ /,/g' $file.transponse.target
	i=1	
	while read line;do
			if [ $i == 1 ];then #erste Zeile enthält die Positionen
				echo $line"]}" | cut -f 2- -d "," > pos.log
				i+=1
			else #die nächsten Zeilen enthalten das Pattern
				echo "[$line]" >> $file.jsons
			fi
		done < $file.transponse.target

	more $file.jsons | tr "\n" "," > $file.json
	sed -i s/.$// $file.json
	echo "]" >> $file.json
	
	AKT_TRGT=$(echo "$file" | cut -f 2 -d ".")
	AKT_SAMPLE=$(echo "$file" | cut -f 1 -d ".")	
	
########## Whole JSON #############

	echo ", \"${AKT_SAMPLE}\":{\"pattern\":[" >> ${AKT_TRGT}.json
	more $file.json >> ${AKT_TRGT}.json
	echo ",\"realpos\":[" >> ${AKT_TRGT}.json
	more pos.log >> ${AKT_TRGT}.json
	rm $file.json
done

echo "- Patternmap: removing *.log, *.target, *.json"
pwd

rm *.log
rm *.target
rm *.json

for i in *.json
do
	echo "}," >> $i
	tr -d "\n" < $i >> targets.json
done 
sed -i s/.$// targets.json
echo "}" >> targets.json

rm -f Target*

cp ${HOMEDIR}/Patternmap.html ${OUTDIR}/Patternmap.html
sed -i -e "/var all =/r targets.json" ${OUTDIR}/Patternmap.html
cd ${BASE_DIR}
echo -e "\nDone with Patternmap\n"
