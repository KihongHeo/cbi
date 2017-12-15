#!/usr/bin/perl -w
# -*- cperl -*-
#line 4 stamps.pl.in

use strict;

use DBI;
use File::Basename;
use File::Find;
use FileHandle;

use lib '../populate';
use Common;
use Site;


########################################################################


print "stamps :=\n";


my $dbh = Common::connect;

##### Selects all builds that have at least two failed runs
my $query = join('', (new FileHandle('stamps.sql'))->getlines);
my $sth = $dbh->prepare($query);
$sth->execute;

my ($name, $version, $release, $distro);
$sth->bind_columns(\$name, \$version, \$release, \$distro);
while ($sth->fetch) {
  my $build = "$version-$release";
  die unless $distro =~ /^\w+-\d+-i386$/;
  my $stamp = "results/$distro/$name-$build/stamp";
  my $rpmname = "/afs/cs.wisc.edu/p/cbi/public/html/downloads/rpm/$distro/RPMS.apps/$name-samplerinfo-$build.i386.rpm";
  if (! -e $rpmname) {
    $rpmname = "/afs/cs.wisc.edu/p/cbi/archives/rpm/$distro/RPMS.apps/$name-samplerinfo-$build.i386.rpm";
  }
  print <<"EOT";
stamps += $stamp
$stamp: $rpmname modernize one
	./one \$< \$(\@D)
EOT
}

$dbh->disconnect;
