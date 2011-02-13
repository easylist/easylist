#!/usr/bin/perl -w
#Originally written by Wladimir Palant
#Adapted for the EasyList repository by Michael

use strict;
use File::Basename;
use Digest::MD5 qw(md5_base64);
use Compress::Zlib;
use POSIX qw(strftime);
require Encode;

my $rootdir = dirname($0);
my $sourcedir = "$rootdir";
my $subsdir = "$rootdir/subscriptions";
my %verbatim = map {$_ => 1} qw(COPYING);

unless (-d "$subsdir")
{
  mkdir ($subsdir) || die "$subsdir does not exist and cannot be created.";
}

if (-f "$subsdir/.lock")
{
  my $pid = readFile("$subsdir/.lock");
  exit if kill(0, $pid);
}

writeFile("$subsdir/.lock", $$);

system("hg", "pull", "--update", $sourcedir);

my %exists = ();

opendir(local *SOURCE, $sourcedir) || die "Could not open directory $sourcedir.";
foreach my $file (readdir(SOURCE))
{
  next unless ($file =~ /\.txt$/ && $file ne "robots.txt") || exists($verbatim{$file});

  my $data = readFile("$sourcedir/$file");

  if (exists($verbatim{$file}))
  {
    $exists{$file} = 1;
    if (-f "$subsdir/$file")
    {
      my $cmp = readFile("$subsdir/$file");
      next if $cmp eq $data;
    }
  }
  else
  {
    my ($header) = ($data =~ /^(.*)/);
    next unless $header =~ /\[Adblock(?:\s*Plus\s*([\d\.]+)?)?\]/i;

    $data = resolveIncludes($data);
    unless ($data)
    {
      warn "Failed to resolve includes in $file.";
      $exists{$file} = -f "$subsdir/$file";
      next;
    }

    $exists{$file} = 1;

    $data =~ s/\r//g;
    $data =~ s/\n+/\n/g;
    $data =~ s/^.*!\s*checksum[\s\-:]+([\w\+\/=]+).*\n//gmi;

    if (-f "$subsdir/$file")
    {
      my $cmp1 = readFile("$subsdir/$file");
      $cmp1 =~ s/^.*!\s*checksum[\s\-:]+([\w\+\/=]+).*\n//gmi;
      $cmp1 =~ s/\s*\d+ \w+ \d+ \d+:\d+ UTC//g;

      my $cmp2 = $data;
      $cmp2 =~ s/\s*\d+ \w+ \d+ \d+:\d+ UTC//g;
      next if $cmp1 eq $cmp2;
    }

    my $checksum = md5_base64($data);
    $data =~ s/\n/\n! Checksum: $checksum\n/;
  }

  writeFile("$subsdir/$file", $data);

  unlink("$subsdir/$file.gz");
  system("7za", "a", "-tgzip", "-mx=9", "-mpass=15", "$subsdir/$file.gz", "$subsdir/$file") && warn "Failed to compress file $subsdir/$file. Please ensure that p7zip is installed on the system.";
}
closedir(SOURCE);

opendir(local *TARGET, $subsdir) || die "Could not open directory $subsdir.";
foreach my $file (readdir(TARGET))
{
  next if $file =~ /^\./ || $file !~ /\.txt$/;

  my $data = readFile("$subsdir/$file");
  $file =~ s/\.txt$/.tpl/;
  $exists{$file} = 1;

  my $converted = convertToTPL($data);
  if (-f "$subsdir/$file")
  {
    my $cmp = readFile("$subsdir/$file");
    next if $cmp eq $converted;
  }
  writeFile("$subsdir/$file", $converted);

  unlink("$subsdir/$file.gz");
  system("7za", "a", "-tgzip", "-mx=9", "-mpass=15", "$subsdir/$file.gz", "$subsdir/$file") && warn "Failed to compress file $subsdir/$file. Please ensure that p7zip is installed on the system.";
}

opendir(local *TARGET, $subsdir) || die "Could not open directory $subsdir.";
foreach my $file (readdir(TARGET))
{
  next if -d "$subsdir/$file" || $file =~ /\.gz$/ || exists($exists{$file});

  unlink("$subsdir/$file");
  unlink("$subsdir/$file.gz");
}
closedir(TARGET);

unlink("$subsdir/.lock");

sub resolveIncludes
{
  my ($data, $level) = @_;
  $level = $level || 0;

  if ($level > 5)
  {
    warn "There are too many instances of \%include\% in the data. It is possible that circular reference is present.";
    return undef;
  }

  my $failures = 0;
  $data =~ s/^\s*%include\s+(.*)%\s*$/my $include = resolveInclude($1, $level);$include ? $include : $failures++/gem;

  my $timestamp = strftime("%e %b %Y %R UTC", gmtime);
  $data =~ s/%timestamp%/$timestamp/g;

  return ($failures ? undef : $data);
}

sub resolveInclude
{
  my ($file, $level) = @_;

  if ($file =~ /^[\w\-\+][\w\.\-\+]*(?:\/[\w\-\+][\w\.\-\+]*)*$/ && -f "$sourcedir/$file")
  {
    my $data = readFile("$sourcedir/$file");
    $data =~ s/\r//g;
    $data =~ s/^.*?%timestamp%.*?$//gm;
    $data =~ s/\n+/\n/g;

    my ($header) = ($data =~ /^(.*)/);
    $data =~ s/^.*\n// if $header =~ /\[Adblock(?:\s*Plus\s*([\d\.]+)?)?\]/i;
    $data = "! *** $file ***\n" . $data;
    $data = resolveIncludes($data, $level + 1);
    return $data;
  }
  elsif ($file =~ /^https?:\/\//)
  {
    my $param = $file;
    $param =~ s/\W/\\$&/g;
    my $data = `wget -q -O - $param`;

    return undef unless $data;

    $data = Compress::Zlib::memGunzip($data) || $data;

    $data =~ s/\r//g;
    $data =~ s/\n+/\n/g;

    my ($header) = ($data =~ /^(.*)/);
    return undef unless $header =~ /\[Adblock(?:\s*Plus\s*([\d\.]+)?)?\]/i;
    $data =~ s/^.*\n//;

    $data = "! *** Fetched from: $file ***\n" . $data;
    return $data;
  }
  return undef;
}

sub convertToTPL
{
  my $data = shift;

  my @result;

  #Add necessary definitions
  push @result, "msFilterList";
  push @result, ": Expires=5";

  foreach my $line (split(/\n/, $data))
  {
    my $original = $line;
    #Translate comments, not including Adblock Plus specific values
    if ($line =~m/\[.*?\]/i)
    {
    }
    elsif ($line =~ m/^!/)
    {
      if ($line =~m/Expires/i)
      {
        #Eventually use this for the : Expires= value
      }
      elsif ($line !~ m/\!\s*checksum/i)
      {
        $line =~ tr/\!/#/;
        push @result, $line;
      }
    }
    else
    {
      #Remove lone third party options
      $line =~ s/\$third-party$//;

      #Translate domain blocks
      if ($line =~ /^(|@@)\|\|.*?\^/)
      {
        $line =~ s/\^/ /;
      }
      elsif ($line =~ /^(|@@)\|\|.*?\//)
      {
        $line =~ s/\// \//;
      }
      #Remove unnecessary asterisks
      $line =~ s/\*$//;
      $line =~ s/ \*/ /;
      #Remove unnecessary slashes and spaces
      $line =~ s/ \/$//;
      $line =~ s/ $//;
		
      #Remove beginning and end anchors
      unless ($line =~ m/^\|\|/)
      {
        $line =~ s/^\|//;
      }
      $line =~ s/\|($|\$)//;
		
      #Translate the script option to "*.js"
      $line =~ s/\$script$/\*\.js/;
		
      #Translate whitelists, making them wider if necessary
      if ($line =~ m/^@@\|\|.*?(^|\/)/)
      {
        $line =~ s/@@\|\|/\+d /;
        #Remove all options
        $line =~ s/\$.*?$//;
      }
      #Comment out all other whitelists, as a domain must be specified in Internet Explorer
      elsif ($line =~ m/^@@/)
      {
        $line = "# " . $original;
      }
      #Comment out all filters with options or element hiding rules, as this functionality is not available in Internet Explorer
      elsif ($line =~ m/(\$|##)/)
      {
        $line = "# " . $original;
      }
      #Translate all domain filters
      elsif ($line =~ m/^\|\|.*?(^|\/)/)
      {
        $line =~ s/^\|\|/\-d /;
      }
      #Translate all other double anchored filters
      elsif ($line =~ m/^\|\|/)
      {
        $line =~ s/^\|\|/\- http:\/\//;
      }
      #Translate all remaining filters as general
      else
      {
        $line = "- " . $line;
      }
      push @result, $line;
    }
  }

  return join("\n", @result) . "\n";
}

sub readFile
{
  my $file = shift;

  open(local *FILE, "<", $file) || die "Could not read file '$file'.";
  binmode(FILE);
  local $/;
  my $result = <FILE>;
  close(FILE);

  return $result;
}

sub writeFile
{
  my ($file, $contents) = @_;

  open(local *FILE, ">", $file) || die "Could not write file '$file'.";
  binmode(FILE);
  print FILE $contents;
  close(FILE);
}
