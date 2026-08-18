import re

from datetime import date, datetime
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag


DETAIL_HEADINGS = ("Info", "Job details")

DESCRIPTION_HEADINGS = (
    "Töö kirjeldus",
    "Job Description",
    "Your main day to day activities include:",
)

REQUIREMENT_HEADINGS = (
    "Ootused kandidaadile",
    "Qualifications",
    "We would be excited if you would match the following:",
)

OFFER_HEADINGS = (
    "Omalt poolt pakume",
    "Additional Information",
    "We offer you:",
)


def clean_text(element: Tag | None) -> str | None:
    if element is None:
        return None

    text = " ".join(element.stripped_strings)
    return text or None


def load_saved_html(file_path: Path) -> BeautifulSoup:
    saved_content = file_path.read_text(encoding="utf-8")
    saved_page = BeautifulSoup(saved_content, "lxml")

    source_lines = saved_page.select("td.line-content")

    if source_lines:
        original_html = "\n".join(
            line.get_text() for line in source_lines
        )
    else:
        original_html = saved_content

    return BeautifulSoup(original_html, "lxml")


def find_heading(
    container: Tag | BeautifulSoup,
    tag_names: tuple[str, ...],
    heading_texts: tuple[str, ...],
) -> Tag | None:
    for heading in container.find_all(list(tag_names)):
        if clean_text(heading) in heading_texts:
            return heading

    return None


def find_details_block(
    soup: BeautifulSoup,
) -> Tag | None:
    heading = find_heading(
        soup,
        ("h2",),
        DETAIL_HEADINGS,
    )

    return heading.parent if heading else None


def extract_info_value(
    details_block: Tag | None,
    labels: tuple[str, ...],
) -> str | None:
    if details_block is None:
        return None

    for label in labels:
        label_element = details_block.find(
            "div",
            string=lambda value: (
                value is not None
                and value.strip() == label
            ),
        )

        if label_element is not None:
            value_element = (
                label_element.find_next_sibling("div")
            )
            return clean_text(value_element)

    return None


def parse_date(value: str | None) -> date | None:
    if not value:
        return None

    date_formats = ("%d.%m.%Y", "%d/%m/%Y")

    for date_format in date_formats:
        try:
            return datetime.strptime(
                value,
                date_format,
            ).date()
        except ValueError:
            continue

    return None


def extract_section(
    job_offer: Tag | None,
    heading_texts: tuple[str, ...],
) -> str | None:
    if job_offer is None:
        return None

    heading = find_heading(
        job_offer,
        ("h2", "h3"),
        heading_texts,
    )

    if heading is None:
        return None

    section_text = clean_text(heading.parent)
    actual_heading = clean_text(heading)

    if not section_text or not actual_heading:
        return None

    if section_text.startswith(actual_heading):
        section_text = section_text[
            len(actual_heading):
        ].strip()

    return section_text or None


def extract_skills(
    soup: BeautifulSoup,
) -> list[str]:
    heading = find_heading(
        soup,
        ("h3",),
        ("Oodatud oskused",),
    )

    if heading is None:
        return []

    skills = []

    for row in heading.parent.select("div.flex.gap-2"):
        spans = row.find_all("span", recursive=False)

        if not spans:
            continue

        skill = clean_text(spans[-1])

        if skill and skill not in skills:
            skills.append(skill)

    return skills


def extract_job_id(
    file_path: Path,
    canonical_url: str | None,
    info_value: str | None,
) -> int | None:
    if info_value:
        match = re.search(r"\d+", info_value)

        if match:
            return int(match.group())

    if canonical_url:
        match = re.search(
            r"(\d+)/?$",
            canonical_url,
        )

        if match:
            return int(match.group(1))

    filename_match = re.match(
        r"(\d+)",
        file_path.stem,
    )

    if filename_match:
        return int(filename_match.group(1))

    return None


def parse_html(
    file_path: Path,
) -> dict[str, object]:
    soup = load_saved_html(file_path)

    title_element = soup.select_one(
        "h1 .main-lang-block"
    )
    company_element = soup.select_one(
        "h1 + div a"
    )
    canonical_element = soup.select_one(
        'link[rel~="canonical"]'
    )

    canonical_url = (
        canonical_element.get("href")
        if canonical_element
        else None
    )

    details_block = find_details_block(soup)
    job_offer = soup.select_one(".job-offer")
    iframe = soup.select_one(
        'iframe[src*="/jobs/"]'
    )

    job_id_text = extract_info_value(
        details_block,
        (
            "Tööpakkumise number:",
            "Job offer:",
        ),
    )

    categories_text = extract_info_value(
        details_block,
        ("Valdkond", "Industry"),
    )

    categories = []

    if categories_text:
        categories = [
            category.strip()
            for category in categories_text.split(",")
            if category.strip()
        ]

    full_html_text = clean_text(job_offer)

    return {
        "source_file": file_path.name,
        "source_job_id": extract_job_id(
            file_path,
            canonical_url,
            job_id_text,
        ),
        "title": clean_text(title_element),
        "company": clean_text(company_element),
        "company_description": clean_text(
            soup.select_one("#description")
        ),
        "location": extract_info_value(
            details_block,
            ("Asukoht", "Location"),
        ),
        "publication_date": parse_date(
            extract_info_value(
                details_block,
                (
                    "Kuulutus sisestati",
                    "Published",
                ),
            )
        ),
        "deadline": parse_date(
            extract_info_value(
                details_block,
                ("Aegub", "Expires"),
            )
        ),
        "salary": extract_info_value(
            details_block,
            ("Palk", "Gross salary"),
        ),
        "employment_type": extract_info_value(
            details_block,
            ("Töö tüüp", "Job type"),
        ),
        "additional_info": extract_info_value(
            details_block,
            ("Lisainfo", "Additional info"),
        ),
        "categories": categories,
        "description": extract_section(
            job_offer,
            DESCRIPTION_HEADINGS,
        ),
        "requirements": extract_section(
            job_offer,
            REQUIREMENT_HEADINGS,
        ),
        "offer": extract_section(
            job_offer,
            OFFER_HEADINGS,
        ),
        "skills": extract_skills(soup),
        "full_html_text": full_html_text,
        "source_url": canonical_url,
        "iframe_source": (
            iframe.get("src") if iframe else None
        ),
        "text_extraction_method": (
            "html" if full_html_text else "none"
        ),
    }