import os
import ftplib
from dotenv import load_dotenv

load_dotenv()
FTP_HOST = "ftp.ncbi.nlm.nih.gov"
FTP_DIR = "/pubmed/updatefiles/"
LOCAL_DAILY_DIR = os.getenv("LOCAL_DAILY_DIR")
os.makedirs(LOCAL_DAILY_DIR, exist_ok=True)

ftp = ftplib.FTP(FTP_HOST)
ftp.login()
ftp.cwd(FTP_DIR)

def download_gz_files():
    files = ftp.nlst()
    gz_files = [f for f in files if f.endswith(".gz")]
    print(f"Found {len(files)} files in {FTP_DIR} on {FTP_HOST}")

    for filename in gz_files:
        local_path = os.path.join(LOCAL_DAILY_DIR, filename)
        if os.path.exists(local_path):
            continue
        
        print(f"Downloading {filename}...")
        with open(local_path, "wb") as f:
            ftp.retrbinary(f"RETR {filename}", f.write)

    ftp.quit()
    print("All files downloaded.")

def download_target_gz_files(index: int):
    filename = f"pubmed25n{index:04d}.xml.gz"
    local_path = os.path.join(LOCAL_DAILY_DIR, filename)

    if os.path.exists(local_path):
        print(f"Already exists: {filename}")
        return local_path

    try:
        print(f"Connecting to FTP: {FTP_HOST}")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login()
        ftp.cwd(FTP_DIR)

        print(f"Downloading {filename}...")
        with open(local_path, "wb") as f:
            ftp.retrbinary(f"RETR {filename}", f.write)

        ftp.quit()
        print(f"Downloaded → {local_path}")
        return local_path

    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return None