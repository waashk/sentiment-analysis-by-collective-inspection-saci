#!/usr/bin/perl -w
use warnings;
use strict;

my ($arquivo,$saidaA, $saidaR) = @ARGV;
my $reader;
my @linha;
my $word;
my $classe;

open(FIN,"<","$arquivo");
open(FSAIDAA,">",$saidaA);
open(FSAIDAR,">",$saidaR);
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	@linha = split(" ",$reader);
	chop($linha[0]);
	if ($linha[1] eq "a" || $linha[1] eq "r"){
		$word = $linha[0];
		$classe = $linha[1];
		open(FOUT,">","entrada.txt");
		print FOUT $word;
		close(FOUT);

		system("./stanford-postagger.sh models/english-left3words-distsim.tagger entrada.txt > saida.txt");
		open(FENTRADA,"<","saida.txt");
		$reader = <FENTRADA>;
		chomp($reader);
		@linha = split("_",$reader);
		close(FENTRADA);

		if ($classe eq "a"){
			print FSAIDAA "$linha[1]\n";
		}
		if ($classe eq "r"){
			print FSAIDAR "$linha[1]\n";
		}

	}
}
close(FIN);
close(FSAIDAA);
close(FSAIDAR);

my %hashA;
my $k;
my $totalA = 0;
open(FIN,"<",$saidaA);
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	if (!exists $hashA{$reader}){
		$hashA{$reader} = 1;
	}else{
		$hashA{$reader}++;
	}
	$totalA++;
}
close(FIN);

print "Estatísticas Amplificadores: \n";
foreach $k(keys %hashA){
	print "$k: ".(($hashA{$k}/$totalA)*100)."\n";
}
print "\n";

my %hashR;
my $totalR = 0;
open(FIN,"<",$saidaR);
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	if (!exists $hashR{$reader}){
		$hashR{$reader} = 1;
	}else{
		$hashR{$reader}++;
	}
	$totalR++;
}
close(FIN);

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
