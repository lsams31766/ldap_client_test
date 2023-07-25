#!/usr/bin/perl -w
# need Cryption.pm

use strict;
#use lib "$ENV{HOME}/netauth";
use lib "/usr/local/lib";
use Cryption;
use IO::Socket;

#my @svrs = ("smlxdir01.net.bms.com", "smlxdir02.net.bms.com", "smusdir04.net.bms.com");
#my @svrs = ("lvldir01.bms.com", "lvldir02.bms.com", "lvldir03.bms.com");
my @svrs = ("access11.aws.bms.com");
#my @svrs = ("smlxdir01.net.bms.com", "smlxdir02.net.bms.com", "smlxdir03.net.bms.com");
#my @svrs = ("usabhbmsast133.net.bms.com");
#my @svrs = ("ahccess.bms.com");
#my @svrs = ("smlxdir01.net.bms.com");
#my @svrs = ("smlxdir02.net.bms.com");
#my @svrs = ("smlxdir01.net.bms.com", "smlxdir02.net.bms.com", "smlxdir03.net.bms.com",
#  "ushpwbmsasp121.net.bms.com", "ushpwbmsasp122.net.bms.com", "ushpwbmsasp123.net.bms.com");
my ($key, $svr, $sock, $request, $r);
$key = "app13pie";

my ($dir, $arg);
# $dir = "plxalphas01";
$dir = "smlxroo01";
if (@ARGV && $ARGV[0] ne "") {
  $dir = $ARGV[0];
}
$arg = "pass";	# fqdn, authdn, pass, port, note
if (@ARGV && $ARGV[1] && $ARGV[1] ne "") {
  $arg = $ARGV[1];
}

foreach $svr (@svrs) {
  #print "----------- $svr ------------------\n";
  #&sockreq($svr, "DCON $dir $arg");
  #&sockreq($svr, "DCON $dir cred");
  &sockreq($svr, "DCON $dir credpipe");
  #sockreq($svr, "DCON $dir credcomma");
}

#================================================================================

sub sockreq {
  my ($svr, $cmd) = @_;
  $sock = new IO::Socket::INET(
    PeerAddr => $svr,
    PeerPort => '1606',
    Proto => 'tcp',
    );
  if (!defined($sock)) { print "sock undefined - is $svr netauth.pl down?\n"; }
  $request = pack('u*', Cryption::encrypt($key, $cmd));
  print $sock $request, "\n";
  #print $sock "testing 1 2 3\n";

  $r = "";
  $r .= $_ while(<$sock>);
  close($sock);
  chomp($r);
  #print "r=$r";
  $r = unpack('u*', "$r");

  unless ($r) {print "no response\n"}
  elsif ($r eq "\0") {print "response came back negative\n"}
  else {print Cryption::decrypt($key, "$r")}
}
