import re
import xml.etree.ElementTree as ET

from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse


JOB_ID_PATTERN = re.compile(r"-(\d+)$")


def extract_job_id(url: str) -> int | None:
    """Extract CVKeskus job ID from the end of the URL."""

    url_path = urlparse(url).path.rstrip("/")
    match = JOB_ID_PATTERN.search(url_path)

    if match is None:
        return None

    return int(match.group(1))


def parse_publication_date(value: str | None) -> datetime | None:
    """Convert an RSS publication date into a datetime object."""

    if not value:
        return None

    return parsedate_to_datetime(value)


def parse_rss(file_path: Path) -> list[dict[str, object]]:
    """Read a local CVKeskus RSS file and return job advertisements."""

    tree = ET.parse(file_path)
    root = tree.getroot()
    channel = root.find("channel")

    if channel is None:
        raise ValueError("RSS file does not contain a channel element.")

    job_postings = []

    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        publication_date = parse_publication_date(
            item.findtext("pubDate")
        )

        job_postings.append(
            {
                "source_job_id": extract_job_id(url),
                "title": title,
                "source_url": url,
                "publication_date": publication_date,
            }
        )

    return job_postings