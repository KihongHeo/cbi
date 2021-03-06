#!/usr/bin/perl -w

use strict;
use FindBin;

my $usage = "./genMscript.pl <datadir>";
my $datadir = shift;
die $usage if !defined $datadir;
my $matdir = "$datadir/mats";

`mkdir -p $matdir` if !-e $matdir;

open (my $fd, "> calculate.m") || die "Open: $!";
print $fd "%%%% This file is automatically generated by genMscript.pl\n%%%% Please do not modify.\n";
print $fd "%%%% input command: ./gencalcAdj.pl $datadir\n";
print $fd "\naddpath ('$FindBin::Bin');\n\n";

## M is the number of predicates, and N is the number of runs
&output_comments($fd);
&output_calcAdj($fd, $datadir, $matdir, "f");
&output_calcAdj($fd, $datadir, $matdir, "s");
&output_calcCorr($fd, $matdir);
#&output_speccluster($fd, $matdir, $datadir);
close ($fd);

sub output_speccluster {
  my ($fd, $matdir, $datadir) = (@_);
  print $fd "%% Do spectral clustering.\n";
  print $fd "disp('Doing spectral clustering.');\n";
  print $fd "runspeccluster\n";
  print $fd "predfn = '$datadir/predinds.txt';\n";
  print $fd "fd = fopen(predfn, 'w');\nfor i = 1:N, fprintf (fd, '%d\\n', i); end;\n";
  print $fd "fclose (fd);\n";
  print $fd "printspeccluster(rho, bestgroups, bestK, '$datadir', '1-0.25', predfn, predfn);\n\n\n";

  my ($M, $N, $nzmax) = &read_meta("$datadir/ftr.meta");
  print $fd "M = $M;\nN = $N;\nnzmax = $nzmax;\n";
  print $fd "Af = readsp('$datadir/ftr.', nzmax, M, N);\n";
  print $fd "printClusterSummary(Af, bestgroups, bestK, '$datadir', '1-0.25');\n";
}

sub output_calcCorr {
  my ($fd, $matdir) = (@_);
  print $fd "%% Calculate correlation matrices.\n";
  print $fd "disp('Calculating correlation matrices.');\n";
  print $fd "load $matdir/Wf.mat\nload $matdir/Wfobs.mat\nload $matdir/Wfcross.mat\n";
  print $fd "load $matdir/Ws.mat\nload $matdir/Wsobs.mat\nload $matdir/Wscross.mat\n";
  print $fd "calcCorr\n";
  print $fd "save $matdir/Cov.mat Cov\nsave $matdir/rho.mat rho\n%save $matdir/condprob.mat PAB\n";
}

sub output_calcAdj {
  my ($fd, $in, $out, $pref) = (@_);
  my $name = $pref . "tr";
  my ($M, $N, $nzmax) = &read_meta("$in/$name.meta");
  print $fd "%%%%%% Calculate adjacency matrix for $pref files.\n";
  print $fd "%%%%%%\n";
  print $fd "%%%%%% M is the number of runs and N is the number of predicates.\n";
  print $fd "M = $M;\nN = $N;\nnzmax = $nzmax;\n";
  print $fd "A$pref = readsp('$in/$name.', nzmax, M, N);\n";
  print $fd "W$pref = A$pref' * A$pref;\n";
  print $fd "save $out/W$pref.mat W$pref\nclear W$pref\n";

  $name = $pref . "obs";
  ($M, $N, $nzmax) = &read_meta("$in/$name.meta");
  print $fd "M = $M;\nN = $N;\nnzmax = $nzmax;\n";
  print $fd "A$name = readsp('$in/$name.', nzmax, M, N);\n";
  print $fd "W$name = A$name' * A$name;\n";
  print $fd "save $out/W$name.mat W$name\nclear W$name\n";

  print $fd "W${pref}cross = A${pref}obs' * A${pref};\n";
  print $fd "save $out/W${pref}cross.mat W${pref}cross\n";
  print $fd "clear A${pref}obs A${pref} W${pref}cross\n\n";
}

sub output_comments {
  my ($fd) = (@_);
  my $comments = <<END;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% This is an automatically generated file.  DO NOT MODIFY.
%%%%
%%%% This Matlab file loads the sparse predicate-run adjacency matrices
%%%% and computes the pairwise correlation coefficients.
%%%%
%%%% Af, As, Afobs, and Asobs are the adjacency matrices for predicate
%%%% true-ness in failed and successful runs, and predicate observed-ness
%%%% in failed an successful runs, respectively.  That is to say,
%%%% Af(i,j) indicates whether predicate j is found true in run i,
%%%% and 
%%%% Afobs(i,j) indicates whether predicate j is observed in run i.
%%%% (Note: The adjacency matrices could also hold fractional values,
%%%%        indicating the percentage of times a predicate is true out
%%%%        of the times that it's observed.) 
%%%% All of the Ax matrices have nruns number of rows and npredicates number
%%%% of columns.
%%%%  
%%%% The W matrices are inner products between the A matrices.  In general,
%%%%   Wx = Ax' * Ax;
%%%% so that Wx(i,j) is the (possibly fractional) count of the number of
%%%% of runs in which predicate i and j are both true/observed.
%%%% Wxcross (where x = 'f' or 's') is the cross-observed-true co-occurrence
%%%% matrix, i.e., 
%%%% Wxcross(i,j) is the number of runs in which predicate i is observed
%%%%              and predicate j is observed and found to be true.
%%%%
%%%% Wf, Ws, Wfobs, Wsobs, Wfcross, and Wscross are all npreds by npreds.
%%%%
%%%%
END

  print $fd $comments;

}

sub read_meta {
  my ($fn) = (@_);
  my ($M, $N, $nzmax);
  open (IN, "$fn") || die "Open: $!";
  while (<IN>) {
    chomp;
    if (/^nruns = ([0-9]+)/) {
      $M = $1;
    }
    elsif (/^npreds = ([0-9]+)/) {
      $N = $1;
    }
    elsif (/^nzmax = ([0-9]+)/) {
      $nzmax = $1;
    }
    else { die "Unknown meta info $_"; }
  }
  close (IN);

  die "lack info" if !defined $M || !defined $N || !defined $nzmax;
  return ($M, $N, $nzmax);
}

