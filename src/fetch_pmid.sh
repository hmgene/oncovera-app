#!/usr/bin/env bash

AUTHOR="Ellis L[Author]"
OUTDIR="data/pubmed"
mkdir -p "$OUTDIR"

echo "Searching PubMed for: $AUTHOR"

# 1. Search for PMIDs
curl -s \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${AUTHOR}&retmax=500" \
  -o esearch.xml

grep -oP '(?<=<Id>)[0-9]+' esearch.xml > pmids.txt
echo "Found $(wc -l < pmids.txt) PMIDs"

# 2. Loop through PMIDs
while read PMID; do
    echo "Processing PMID $PMID"

    XML="tmp_${PMID}.xml"

    # Fetch metadata
    curl -s \
      "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${PMID}&retmode=xml" \
      -o "$XML"

    # Extract PMC ID
    PMC_ID=$(grep -oP '(?<=<ArticleId IdType="pmc">)PMC[0-9]+' "$XML")

    if [ -z "$PMC_ID" ]; then
        echo "  No PMC ID found — skipping"
        rm "$XML"
        continue
    fi

    echo "  Found PMC ID: $PMC_ID"

    # 3. Download PDF
    PDF="${OUTDIR}/${PMC_ID}.pdf"

    curl -L \
      "https://www.ncbi.nlm.nih.gov/pmc/articles/${PMC_ID}/pdf/" \
      -o "$PDF"

    echo "  Saved PDF → $PDF"

    rm "$XML"
done < pmids.txt

