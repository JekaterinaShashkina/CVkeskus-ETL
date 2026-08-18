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