import json

from datetime import date, datetime
from pathlib import Path


def serialize_value(value: object) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    raise TypeError(
        f"Object of type {type(value).__name__} "
        "is not JSON serializable"
    )


def save_jobs_to_json(
    jobs: list[dict[str, object]],
    output_file: Path,
) -> None:
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_content = json.dumps(
        jobs,
        ensure_ascii=False,
        indent=2,
        default=serialize_value,
    )

    output_file.write_text(
        json_content + "\n",
        encoding="utf-8",
    )