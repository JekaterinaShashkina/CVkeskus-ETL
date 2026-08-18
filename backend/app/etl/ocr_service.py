from pathlib import Path
import shutil

import pytesseract
from PIL import Image, ImageOps


WINDOWS_TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def configure_tesseract() -> None:
    """Находит Tesseract или указывает путь к Windows-установке."""

    if shutil.which("tesseract"):
        return

    if WINDOWS_TESSERACT_PATH.exists():
        pytesseract.pytesseract.tesseract_cmd = str(
            WINDOWS_TESSERACT_PATH
        )
        return

    raise FileNotFoundError(
        "Tesseract was not found. "
        "Check the installation path."
    )


def prepare_image(image_path: Path) -> Image.Image:
    """Подготавливает изображение для распознавания."""

    with Image.open(image_path) as source_image:
        image = ImageOps.exif_transpose(source_image).convert("RGB")

    # Увеличиваем небольшое изображение, чтобы текст читался лучше.
    if image.width < 1800:
        image = image.resize(
            (image.width * 2, image.height * 2),
            Image.Resampling.LANCZOS,
        )

    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)

    return image


def extract_text_from_image(image_path: Path) -> str:
    """Извлекает эстонский и английский текст из изображения."""

    if not image_path.exists():
        raise FileNotFoundError(f"Image was not found: {image_path}")

    configure_tesseract()
    image = prepare_image(image_path)

    raw_text = pytesseract.image_to_string(
        image,
        lang="est+eng",
        config="--oem 1 --psm 11",
    )

    lines = [
        " ".join(line.split())
        for line in raw_text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    test_image = Path("data/raw/images/1043494-DevOps.jpg")

    extracted_text = extract_text_from_image(test_image)

    print(f"Image: {test_image.name}")
    print(f"Extracted text length: {len(extracted_text)}")
    print()
    print(extracted_text)