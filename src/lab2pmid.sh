#!/usr/bin/env bash
usage="$BASH_SOURCE <md>"
if [ $# -lt 1 ];then echo "$usage";exit;fi 

. src/url2pmid.sh

MD_FILE=$1 #"data/lab/cpdr-shresthalab.md"
URL=$( awk -F'pubmed_url:[ \t]*' '/pubmed_url:/ {print $2}' "$MD_FILE" )
if [ -z "$URL" ]; then
    echo "Warning: No pubmed_url found in $MD_FILE" >&2
    exit 1
fi
pmid=$( url2pmid $URL ) 

cat "$MD_FILE" | perl -e ' use strict; use warnings;
    my %h=map{chomp;$_=> 1} split/,/,shift @ARGV || "";
    while (<>) { chomp;
        if ($_ =~ /pmids:/) {
            while (/(\d+)/g) { $h{$1}++; }
            print "pmids:", join(",", sort keys %h), "\n";
        } else {
            print $_, "\n";
        }
    }
' "$pmids" > $MD_FILE.tmp; mv $MD_FILE.tmp $MD_FILE
echo "Updated $MD_FILE with new PMIDs."


