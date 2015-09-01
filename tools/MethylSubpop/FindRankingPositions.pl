#!/usr/bin/perl

#start with ./FindRankingPositions.pl <positions of first and last x/X of all samples -> "ValidPositions.txt"> 

use strict;
use warnings;
use List::Util 'max','min';

my $eachline;

#read in regions of interest & return max(First) & min(Last)
open (my $regions, "<", $ARGV[0]) or die ("no such file!");
while(defined($eachline=<$regions>))
	{
		my (@start,@end);		
		chomp $eachline;
		while ($eachline =~ m/FIRST=([0-9]*)/g)
		{
			push @start, $1;
		}	
		while ($eachline =~ m/LAST=([0-9]*)/g)
		{
			push @end, $1;
		}
		if ($eachline =~ /^\s*$/)
		{
			print "FIRST=0 LAST=0\n";
			next;
		}
		print "FIRST=", max( @start ),"\tLAST=", min( @end ), "\n";
	}
close($regions);


