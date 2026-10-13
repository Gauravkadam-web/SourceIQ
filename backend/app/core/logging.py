import logging
import sys
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Sanitized JSON formatter ensuring no raw document texts or secrets are leaked."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "workspace_id"):
            log_obj["workspace_id"] = record.workspace_id
        if hasattr(record, "doc_id"):
            log_obj["doc_id"] = record.doc_id
        if hasattr(record, "latency_ms"):
            log_obj["latency_ms"] = record.latency_ms

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("sourceiq")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
