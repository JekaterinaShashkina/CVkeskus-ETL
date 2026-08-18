from pathlib import Path

from backend.app.config import HTML_DIR, IMAGES_DIR
from backend.app.etl.content_classifier import (
    classify_content,
    needs_ocr,
)
from backend.app.etl.html_parser import parse_html
from backend.app.etl.ocr_service import (
    extract_text_from_image,
)


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def find_matching_image(
    html_file: Path,
) -> Path | None:
    for extension in IMAGE_EXTENSIONS:
        image_path = (
            IMAGES_DIR
            / f"{html_file.stem}{extension}"
        )

        if image_path.exists():
            return image_path

    return None


def text_length(value: object) -> int:
    return len(value) if isinstance(value, str) else 0


def apply_ocr(
    job: dict[str, object],
    image_path: Path | None,
    ocr_required: bool,
) -> None:
    job["ocr_required"] = ocr_required
    job["ocr_text"] = None
    job["ocr_error"] = None

    if not ocr_required:
        job["ocr_status"] = "not_required"
        return

    if image_path is None:
        job["ocr_status"] = "image_not_found"
        return

    try:
        job["ocr_text"] = extract_text_from_image(
            image_path
        )
        job["ocr_status"] = "success"
        job["text_extraction_method"] = "ocr"

    except Exception as error:
        job["ocr_status"] = "failed"
        job["ocr_error"] = str(error)


def print_job_result(
    html_file: Path,
    job: dict[str, object],
) -> None:
    print(f"File: {html_file.name}")
    print(f"  ID: {job['source_job_id']}")
    print(f"  Title: {job['title']}")
    print(f"  Company: {job['company']}")
    print(f"  Location: {job['location']}")
    print(f"  Published: {job['publication_date']}")
    print(f"  Deadline: {job['deadline']}")
    print(f"  Salary: {job['salary']}")
    print(f"  Content type: {job['content_type']}")

    print(
        "  Description length: "
        f"{text_length(job['description'])}"
    )
    print(
        "  Requirements length: "
        f"{text_length(job['requirements'])}"
    )
    print(
        "  Offer length: "
        f"{text_length(job['offer'])}"
    )
    print(
        "  Full HTML length: "
        f"{text_length(job['full_html_text'])}"
    )
    print(
        f"  Iframe source: {job['iframe_source']}"
    )
    print(
        f"  Matching image: {job['image_file']}"
    )
    print(
        f"  OCR required: {job['ocr_required']}"
    )
    print(
        f"  OCR status: {job['ocr_status']}"
    )
    print(
        "  OCR text length: "
        f"{text_length(job['ocr_text'])}"
    )
    print(
        "  Extraction method: "
        f"{job['text_extraction_method']}"
    )

    if job["ocr_error"]:
        print(f"  OCR error: {job['ocr_error']}")

    print()


def main() -> None:
    html_files = sorted(HTML_DIR.glob("*.html"))

    print(f"HTML files found: {len(html_files)}")
    print()

    for html_file in html_files:
        try:
            job = parse_html(html_file)
            image_path = find_matching_image(
                html_file
            )

            content_type = classify_content(
                job["full_html_text"],
                image_path is not None,
            )

            ocr_required = needs_ocr(
                content_type,
                job["description"],
                job["requirements"],
            )

            job["content_type"] = content_type
            job["image_file"] = (
                image_path.name
                if image_path
                else None
            )

            apply_ocr(
                job,
                image_path,
                ocr_required,
            )

            print_job_result(
                html_file,
                job,
            )

        except Exception as error:
            print(f"File: {html_file.name}")
            print(f"  ERROR: {error}")
            print()


if __name__ == "__main__":
    main()