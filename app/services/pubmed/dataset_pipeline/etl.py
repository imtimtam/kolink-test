import os
from dotenv import load_dotenv

from app.services.pubmed.dataset_pipeline.downloader_baseline import download_gz_files, download_target_gz_file
from app.services.pubmed.dataset_pipeline.exporter import parse_export_pubmed, parse_export_pubmed_single_file

load_dotenv()
LOCAL_DAILY_DIR = os.getenv("LOCAL_DAILY_DIR")
LOCAL_BASELINE_DIR = os.getenv("LOCAL_BASELINE_DIR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
os.makedirs(LOCAL_DAILY_DIR, exist_ok=True)
os.makedirs(LOCAL_BASELINE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

FTP_HOST = "ftp.ncbi.nlm.nih.gov"
FTP_BASELINE_DIR = "/pubmed/baseline/"
FTP_DAILY_DIR = "/pubmed/updatefiles/"

if __name__ == "__main__":
    # Just run whatever is necessary
    # python -m app.services.pubmed.dataset_pipeline.etl
    # download_gz_files(FTP_HOST, FTP_DAILY_DIR, LOCAL_DAILY_DIR)
    parse_export_pubmed(LOCAL_BASELINE_DIR, output_dir=OUTPUT_DIR)
    pass