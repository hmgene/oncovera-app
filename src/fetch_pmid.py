# fetch_pubmed.py
import os
import time
import yaml
import requests
from pathlib import Path
from Bio import Entrez

CONFIG_PATH = "config.yaml"
PMID_FILE = "data/pmids.txt"
OUTPUT_DIR = Path("data/pubmed")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    Entrez.email = cfg.get("entrez_email")
    if cfg.get("entrez_api_key"):
        Entrez.api_key = cfg["entrez_api_key"]

def read_pmids():
    with open(PMID_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_pubmed_record(pmid):
    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
    records = Entrez.read(handle)
    handle.close()
    return records

def get_pmc_id_and_title(record):
    article = record["PubmedArticle"][0]
    article_data = article["MedlineCitation"]["Article"]
    title = article_data.get("ArticleTitle", f"PMID_{article['MedlineCitation']['PMID']}")
    # Look for PubMed Central ID if present
    pmc_id = None
    for id_list in article.get("PubmedData", {}).get("ArticleIdList", []):
        if id_list.attributes.get("IdType") == "pmc":
            pmc_id = str(id_list)
            break
    return pmc_id, title

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def download_pdf_from_pmc(pmc_id, out_path):
    # Simple heuristic: many PMC articles are available via this pattern
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf"
    r = requests.get(url, stream=True)
    if r.status_code == 200 and "application/pdf" in r.headers.get("Content-Type", ""):
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    return False

def main():
    load_config()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pmids = read_pmids()

    for pmid in pmids:
        print(f"Processing PMID {pmid}...")
        try:
            record = fetch_pubmed_record(pmid)
            pmc_id, title = get_pmc_id_and_title(record)
            safe_title = sanitize_filename(title)[:120]
            pdf_path = OUTPUT_DIR / f"{pmid}_{safe_title}.pdf"

            if pdf_path.exists():
                print(f"  Already exists: {pdf_path}")
                continue

            if pmc_id:
                print(f"  Found PMC ID: {pmc_id}, attempting PDF download...")
                ok = download_pdf_from_pmc(pmc_id, pdf_path)
                if ok:
                    print(f"  Saved: {pdf_path}")
                else:
                    print("  Could not download PDF from PMC.")
            else:
                print("  No PMC ID found; may need manual or publisher access.")
        except Exception as e:
            print(f"  Error for PMID {pmid}: {e}")

        time.sleep(0.4)  # be gentle with NCBI

if __name__ == "__main__":
    main()

