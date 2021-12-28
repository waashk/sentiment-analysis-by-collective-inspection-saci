#!/usr/bin/perl -w
use warnings;
use strict;

my ($arquivo,$pos) = @ARGV;
my $reader;
my @linha;
my $totalA = 0;
my $totalR = 0;

open(FIN,"<",$arquivo);
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	@linha = split(/ /,$reader);
	if ($linha[1] eq "a"){
		$totalA++;
	}elsif ($linha[1] eq "r"){
		$totalR++;
	}
}
close(FIN);

my %hashA;
my %hashR;
my $i = 0;
open(FIN,"<",$pos);
while($i<$totalA){
	$reader = <FIN>;
	chomp($reader);
	if (!exists $hashA{$reader}){
		$hashA{$reader} = 1;
	}else{
		$hashA{$reader}++;
	}
	$i++;
}
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	if (!exists $hashR{$reader}){
		$hashR{$reader} = 1;
	}else{
		$hashR{$reader}++;
	}
}
close(FIN);

my $k;

print "Estatísticas Amplificadores: \n";
foreach $k(keys %hashA){
	print "$k: ".(($hashA{$k}/$totalA)*100)."\n";
}
print "\n";

print "Estatísticas Redutores: \n";
foreach $k(keys %hashR){
	print "$k: ".(($hashR{$k}/$totalR)*100)."\n";
}
print "\n";

print "Estatísticas Gerais: \n";
if (length(%hashR)>length(%hashA)){
	foreach $k(keys %hashR){
		if (exists $hashA{$k}){
			print "$k: ".((($hashR{$k}+$hashA{$k})/($totalA+$totalR))*100)."\n";
		}else{
			print "$k: ".((($hashR{$k})/($totalA+$totalR))*100)."\n";
		}
	}
}else{
	foreach $k(keys %hashA){
		if (exists $hashR{$k}){
			print "$k: ".((($hashR{$k}+$hashA{$k})/($totalA+$totalR))*100)."\n";
		}else{
			print "$k: ".((($hashA{$k})/($totalA+$totalR))*100)."\n";
		}
	}
}
