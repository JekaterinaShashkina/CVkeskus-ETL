def classify_content(
    html_text: str | None,
    has_image: bool,
) -> str:
    """Classify the locally available advertisement content."""

    has_html_content = bool(
        html_text and html_text.strip()
    )

    if has_html_content and has_image:
        return "mixed"

    if has_html_content:
        return "html"

    if has_image:
        return "image_only"

    return "insufficient"

def needs_ocr(
    content_type: str,
    description: str | None,
    requirements: str | None,
) -> bool:
    """Determine whether OCR processing is required."""

    if content_type == "image_only":
        return True

    if content_type == "mixed":
        return not (
            description
            and requirements
        )

    return False