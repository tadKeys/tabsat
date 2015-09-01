#!/usr/bin/perl

#start with ./MethylPatter.pl <wholetargetlist> <sam file>
#returns the different methylation patterns of the whole targets

use strict;
use warnings;
use List::MoreUtils qw(uniq);
use Switch; # sudo apt-get install libswitch-perl or cpan; install Switch

my $eachline;
my @samfields;
my @targets;
my $modified;

#read in regions of interest
open (my $regions, "<", $ARGV[0]) or die ("no such file!");
while(defined($eachline=<$regions>))
	{
		chomp $eachline;	
		push @targets, { split /[\s+=]/, $eachline };
	}
close($regions);

my @targetarray= ();
foreach my $i ( 0 .. scalar @targets-1 ) {
	my $j = $i+1;
	push @{ $targetarray[$i] }, ("Target $j; $targets[$j-1]{CHR}; $targets[$j-1]{START}-$targets[$j-1]{END}");	
}

#read in samfile
open(my $samfile, "<", $ARGV[1]) or die "cannot open < $ARGV[1]: $!";
while(defined($eachline=<$samfile>))
	{
		unless ($eachline=~/^@.*/)
			{
				@samfields = split("\t", $eachline);
				chomp($samfields[0]);  # remove whitespaces
				next if ($samfields[1] == 16);
				my $entry = {chro => $samfields[2], start => $samfields[3], leng => length($samfields[9])};
				  foreach my $elem(@targets){
				    if(testMatch($entry, $elem)){
					my $adap1 =""; #filling gaps of read in the if it is shorter than the whole read
					$adap1 = "*"x ($samfields[3] - $elem->{START}) if ($samfields[3] > $elem->{START});
					$modified = cigar($samfields[5],$samfields[13]);
					push @{$targetarray[($elem->{TNR})-1]}, ($adap1 . $modified);
				    }
  }
			}
	}
close($samfile);

foreach my $row (@targetarray) {
    foreach my $element (uniq @$row) {	
	
        print $element, "\n";
    }
   print "\n";  
}

#check whether read match with target and cover at least 80% of the target
sub testMatch
{
  my $elem  = shift;
  my $range = shift;

  return    $elem->{chro}   eq $range->{CHR}
         && $elem->{start} >= $range->{START} 
         && $elem->{start} <= $range->{START}+(($range->{END})-($range->{START})+1)*0.2
         && $elem->{leng}   >= (($range->{END})-($range->{START})+1)*0.8 
  ;
}

#considering indels
sub cigar
{
	my $command = shift;
	my $input   = shift;
	my $output = "";

	$input =~ s/XM:Z://; #remove bismark syntax
	$input =~ s/[hHxXuU]/./g; #we are only interested in methylation positions;

	while ($command =~ m/(\d+)([MID])/g) {
	    my $value = $1;
	    my $code  = $2;

	    switch($code) {
		case ('D') {
		    $output .= '.' x $value;
		}
		case ('I') {
		    $input = substr($input, $value);
		}
		case ('M') {
		    $output .= substr($input, 0, $value);
		    $input = substr($input, $value);
		}
	    }
	}
	return $output;
}


