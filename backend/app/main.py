from backend.app.config import HTML_DIR, IMAGES_DIR
from backend.app.etl.content_classifier import (
    classify_content,
)
from backend.app.etl.html_parser import parse_html


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def has_matching_image(html_file):
    return any(
        (IMAGES_DIR / f"{html_file.stem}{extension}").exists()
        for extension in IMAGE_EXTENSIONS
    )


def text_length(value):
    return len(value) if value else 0


def main():
    html_files = sorted(HTML_DIR.glob("*.html"))

    print(f"HTML files found: {len(html_files)}")
    print()

    for html_file in html_files:
        try:
            job = parse_html(html_file)
            has_image = has_matching_image(html_file)

            content_type = classify_content(
                job["full_html_text"],
                has_image,
            )

            print(f"File: {html_file.name}")
            print(f"  ID: {job['source_job_id']}")
            print(f"  Title: {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Location: {job['location']}")
            print(f"  Published: {job['publication_date']}")
            print(f"  Deadline: {job['deadline']}")
            print(f"  Salary: {job['salary']}")
            print(f"  Content type: {content_type}")
            print(
                f"  Description length: "
                f"{text_length(job['description'])}"
            )
            print(
                f"  Requirements length: "
                f"{text_length(job['requirements'])}"
            )
            print(
                f"  Offer length: "
                f"{text_length(job['offer'])}"
            )
            print(
                f"  Full HTML length: "
                f"{text_length(job['full_html_text'])}"
            )
            print(
                f"  Iframe source: "
                f"{job['iframe_source']}"
            )
            print()

        except Exception as error:
            print(f"File: {html_file.name}")
            print(f"  ERROR: {error}")
            print()


if __name__ == "__main__":
    main()