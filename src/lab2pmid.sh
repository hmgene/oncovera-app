#!/usr/bin/env bash

MD_FILE="data/lab/cpdr-shresthalab.md"
tmpd=`mktemp -d`
tmpd=tmp
URL=$(grep -oP 'pubmed_url:\s*\K.*' "$MD_FILE" )
echo "Using PubMed source: $URL"
curl -s "$URL" -o $tmpd/tmp_bib.html
grep -oP 'pmid[:=][^\d]*\K[0-9]+' $tmpd/tmp_bib.html > $tmpd/tmp_pmids.txt
echo "Found $(wc -l < $tmpd/tmp_pmids.txt) PMIDs"
PMIDS=$(tr '\n' ',' < "$tmpd/tmp_pmids.txt" | sed 's/,$//')
echo $PMIDS
sed -i "s|pmids:\K[0-9+|pmids:$PMIDS|" "$MD_FILE"
exit 
# 5. Replace the PMID block in the Markdown file
awk '
  BEGIN {in_block=0}
  /^PMID:/ {print; system("cat $tmpd/tmp_block.txt"); in_block=1; next}
  in_block && /^```/ {in_block=0; next}
  !in_block {print}
' "$MD_FILE" > $tmpd/tmp_updated.md

mv $tmpd/tmp_updated.md "$MD_FILE"

echo "Updated $MD_FILE with new PMIDs."

# Cleanup
rm $tmpd/tmp_bib.html $tmpd/tmp_pmids.txt $tmpd/tmp_block.txt

