from backend.app.config import RSS_DIR
from backend.app.etl.rss_parser import parse_rss


def find_rss_file():
    rss_files = sorted(RSS_DIR.glob("*.xml"))

    if not rss_files:
        raise FileNotFoundError(
            f"No XML files found in {RSS_DIR}"
        )

    return rss_files[0]


def main():
    rss_file = find_rss_file()
    job_postings = parse_rss(rss_file)

    print(f"RSS file: {rss_file.name}")
    print(f"Job postings found: {len(job_postings)}")
    print()

    for job in job_postings[:5]:
        print(
            f"{job['source_job_id']} | "
            f"{job['title']} | "
            f"{job['publication_date']}"
        )


if __name__ == "__main__":
    main()