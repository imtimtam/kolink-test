import os
import ftplib

def download_gz_files(ftp_host, ftp_dir, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login()
        ftp.cwd(ftp_dir)

        files = ftp.nlst()
        gz_files = [f for f in files if f.endswith(".gz")]
        print(f"Found {len(files)} files in {ftp_dir} on {ftp_host}")

        for filename in gz_files:
            local_path = os.path.join(local_dir, filename)
            if os.path.exists(local_path):
                continue

            print(f"Downloading {filename}...")
            with open(local_path, "wb") as f:
                ftp.retrbinary(f"RETR {filename}", f.write)

        ftp.quit()
        print("All files downloaded.")
    except Exception as e:
        print(f"Failed to download files from {ftp_host}: {e}")


def download_target_gz_file(ftp_host, ftp_dir, local_dir, index):
    os.makedirs(local_dir, exist_ok=True)
    filename = f"pubmed25n{index:04d}.xml.gz"
    local_path = os.path.join(local_dir, filename)

    if os.path.exists(local_path):
        print(f"Already exists: {filename}")
        return local_path

    try:
        print(f"Connecting to FTP: {ftp_host}")
        ftp = ftplib.FTP(ftp_host)
        ftp.login()
        ftp.cwd(ftp_dir)

        print(f"Downloading {filename}...")
        with open(local_path, "wb") as f:
            ftp.retrbinary(f"RETR {filename}", f.write)

        ftp.quit()
        print(f"Downloaded → {local_path}")
        return local_path

    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return None