#!/usr/bin/perl -w
use warnings;
use strict;

#Declarações
my ($baseFile, $dicionarioFile, $saidaA, $saidaR) = @ARGV;
my $reader;
my @linha;

#Buscando o dicionario e colocando na hash
my %dicionario;
open(FIN,"<",$dicionarioFile);
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	@linha = split(/ /,$reader);
	chop($linha[0]);
	$dicionario{$linha[0]} = $linha[1];
}
close(FIN);

#Lendo a base já limpa!!!
my @tweets;
my $cont = 0;
open(FIN,"<",$baseFile);
while(!eof(FIN)){
	$reader = <FIN>;
	chomp($reader);
	@linha = split(/ /,$reader);
	foreach my $l(@linha){
		if (exists $dicionario{$l}){
			if (($dicionario{$l} eq "a")||($dicionario{$l} eq "r")){
				push(@tweets,[@linha]);
				$cont++;
				last;
			}
		}

	}
}
close(FIN);


my %hashA;
my %hashR;
my $totalA = 0;
my $totalR = 0;
my $k;
my @termos;
foreach my $t(@tweets){

	my @vetor = @{$t};
	my $string = "";
	for (my $i=1;$i<@vetor;$i++){
		$string .= $vetor[$i]." ";
	}

	open(FENTRADA,">","entrada.txt");
	print FENTRADA $string;
	close(FENTRADA);

	system("./stanford-postagger.sh models/english-left3words-distsim.tagger entrada.txt > saida.txt");

	open(FSAIDA,"<","saida.txt");
	$reader = <FSAIDA>;
	chomp($reader);
	@linha = split(/ /,$reader);
	foreach my $l(@linha){
		@termos = split(/_/,$l);
		if ((exists $dicionario{$termos[0]})&&($dicionario{$termos[0]} eq "a")){
			if (!(exists $hashA{$termos[1]})){
				$hashA{$termos[1]} = 1;
			}else{
				$hashA{$termos[1]}++;
			}
			$totalA++;
		}
		if ((exists $dicionario{$termos[0]})&&($dicionario{$termos[0]} eq "r")){
			if (!(exists $hashR{$termos[1]})){
				$hashR{$termos[1]} = 1;
			}else{
				$hashR{$termos[1]}++;
			}
			$totalR++;
		}
	}
	close(FSAIDA);
}
print "$cont palavras tem termos amplificadores ou redutores\n";

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
