from typing import Any


def deserialize_datetime_fields(
    doc: dict[str, Any], fields: list[str]
) -> dict[str, Any]:
    from datetime import datetime, timezone

    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            try:
                doc[field] = datetime.fromisoformat(doc[field])
            except ValueError:
                if field == "created_at" or field == "posted_at":
                    doc[field] = datetime.now(timezone.utc)
    return doc
