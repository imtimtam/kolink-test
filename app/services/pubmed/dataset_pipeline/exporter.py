import os
from dotenv import load_dotenv
from lxml import etree
import json

from app.services.pubmed.dataset_pipeline.parser import parse_pubmed_article
from app.services.pubmed.dataset_pipeline.streamer import stream_pubmed_gz

def parse_export_pubmed(input_dir, output_dir, sample_limit=None, starting_index=1):
    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".gz"):
            continue

        try:
            idx = int(filename.replace("pubmed25n", "").replace(".xml.gz", ""))
        except ValueError:
            continue
        if idx < starting_index:
            continue

        local_path = os.path.join(input_dir, filename)
        print(f"Processing {filename}...")

        year_buffers = {}
        def load_existing(year, out_path):
            if os.path.exists(out_path):
                existing = {}
                with open(out_path, "r", encoding="utf-8") as fr:
                    for line in fr:
                        try:
                            row = json.loads(line)
                            existing[row["pmid"]] = row
                        except:
                            continue
                return existing
            return {}

        count = 0
        for elem in stream_pubmed_gz(local_path):
            article = parse_pubmed_article(elem)
            if article is None:
                continue

            year = article["date_published"][:4] if article["date_published"] else "UNKNOWN"
            year_dir = os.path.join(output_dir, year)
            os.makedirs(year_dir, exist_ok=True)
            output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))

            if year not in year_buffers:
                year_buffers[year] = load_existing(year, output_path)
            year_buffers[year][article["pmid"]] = article
            count += 1

            if sample_limit and count >= sample_limit:
                break
            if count % 1000 == 0:
                print(f"{count} articles processed in {filename}...")

        for year, pmid_map in year_buffers.items():
            year_dir = os.path.join(output_dir, year)
            output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))
            with open(output_path, "w", encoding="utf-8") as fw:
                for row in pmid_map.values():
                    json.dump(row, fw, ensure_ascii=False)
                    fw.write("\n")

        print(f"Finished {filename}, total articles processed: {count}")


def parse_export_pubmed_single_file(local_path, filename, output_dir):
    year_buffers = {}

    def load_existing(year, out_path):
        if os.path.exists(out_path):
            existing = {}
            with open(out_path, "r", encoding="utf-8") as fr:
                for line in fr:
                    try:
                        row = json.loads(line)
                        existing[row["pmid"]] = row
                    except:
                        continue
            return existing
        return {}

    print(f"Processing {filename}...")
    count = 0

    for elem in stream_pubmed_gz(local_path):
        article = parse_pubmed_article(elem)
        if article is None:
            continue
        
        year = article["date_published"][:4] if article["date_published"] else "UNKNOWN"
        year_dir = os.path.join(output_dir, year)
        os.makedirs(year_dir, exist_ok=True)
        output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))

        if year not in year_buffers:
            year_buffers[year] = load_existing(year, output_path)

        year_buffers[year][article["pmid"]] = article
        count += 1

        if count % 1000 == 0:
            print(f"{count} articles processed...")

    for year, pmid_map in year_buffers.items():
        year_dir = os.path.join(output_dir, year)
        output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))
        with open(output_path, "w", encoding="utf-8") as fw:
            for row in pmid_map.values():
                json.dump(row, fw, ensure_ascii=False)
                fw.write("\n")

    print(f"Finished {filename}, total articles processed: {count}")
