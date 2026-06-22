
url2pmid() {
    local input="$1"

    if [[ "$input" == *"myncbi"* ]]; then
        # Handle MyNCBI Scraping
        curl -s "$input" | \
            grep -oE 'pubmed/[0-9]+' | \
            grep -oE '[0-9]+' | \
            sort -nu | \
            paste -sd, -

    elif [[ "$input" == *"eutils"* ]]; then
        # Handle E-utilities JSON Parsing with native Unix tools
        curl -s "$input" | \
            grep -oE '"idlist":\s*\[[^]*]+\]' | \
            tr -cd '0-9,\n' | \
            sed 's/^,//;s/,$//'
            
    else
        echo "Error: Unsupported input format" >&2
        return 1
    fi
}


url2pmid-test() {
echo "myncbi style:"
url2pmid "https://www.ncbi.nlm.nih.gov/myncbi/raunak.shrestha.1/bibliography/public/"

echo "author name:"
url2pmid "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Leigh+Ellis&sort=pub_date&retmode=json"
}
