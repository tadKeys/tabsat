#!/bin/bash

echo -e  "\n*****************************"
echo "* Comparing mapping results *"
echo -e "*****************************\n\n"


echo "**** Bismark ****"
grep "Mapping efficiency" bismark/bismark.log
echo ""

echo "**** BSMap ****"
grep "aligned reads" bsmap/run.log | cut -f 1 -d "," | sed 's/\t//g'
echo ""


echo "**** BsSeeker2 ****"
grep "Mappability" bsseeker2/run.log | cut -f 2 -d "]" | sed 's/ //g'
echo ""


