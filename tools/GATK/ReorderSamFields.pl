#!/usr/bin/perl

use strict;
use warnings;

my $eachline;
my ($RG,$PG,$MD,$NM,$AS,$XM,$XA,$XS,$XT,$XF,$XE)="";

open (my $input, "<", $ARGV[0]) or die ("no such file!");
while(defined($eachline=<$input>))
	{
		if($eachline=~/^@/) 
			{
				print $eachline;			
			}
		elsif($eachline=~/\t[A|C|G|T]*\t/) 
			{
				chomp $eachline;				
				my ($RG,$PG,$MD,$NM,$AS,$XM,$XA,$XS,$XT,$XF,$XE)="";				
				my @fields = split (/\t/,$eachline);
				#print @fields;
				foreach (@fields){
					 $RG=$_ if ($_ =~ /^RG/); 
					 $PG=$_ if ($_ =~ /^PG/);  
					 $MD=$_ if ($_ =~ /^MD/); 
					 $NM=$_ if ($_ =~ /^NM/); 
					 $AS=$_ if ($_ =~ /^AS/); 
					 $XM=$_ if ($_ =~ /^XM/); 
					 $XA=$_ if ($_ =~ /^XA/); 
					 $XS=$_ if ($_ =~ /^XS/); 
					 $XT=$_ if ($_ =~ /^XT/); 
					 $XF=$_ if ($_ =~ /^XF/); 
					 $XE=$_ if ($_ =~ /^XE/);
					 }
				foreach (0 .. 10)
					{print "$fields[$_]\t";}
				if ($XT && $XF && $XE)
				{print "$RG\t$PG\t$MD\t$NM\t$AS\t$XM\t$XA\t$XS\t$XT\t$XF\t$XE\n";}
				elsif ($XT)
				{print "$RG\t$PG\t$MD\t$NM\t$AS\t$XM\t$XA\t$XS\t$XT\n";}
				elsif ($XS)
				{print "$RG\t$PG\t$MD\t$NM\t$AS\t$XM\t$XA\t$XS\n";}
				else
				{print "$RG\t$PG\n";}
			}		
	}
close($input);


