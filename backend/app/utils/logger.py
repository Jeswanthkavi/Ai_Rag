import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# =========================================================
# LOG DIRECTORY
# =========================================================

LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


LOG_FILE = (
    LOG_DIR / "app.log"
)


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger(
    "rag_backend"
)


logger.setLevel(
    logging.INFO
)


# =========================================================
# PREVENT DUPLICATE HANDLERS
# =========================================================

if not logger.handlers:

    # -----------------------------------------------------
    # Console handler
    # -----------------------------------------------------

    console_handler = (
        logging.StreamHandler()
    )

    # -----------------------------------------------------
    # File handler
    # -----------------------------------------------------

    file_handler = (
        RotatingFileHandler(

            LOG_FILE,

            maxBytes=5 * 1024 * 1024,

            backupCount=3,

            encoding="utf-8"
        )
    )

    # -----------------------------------------------------
    # Formatter
    # -----------------------------------------------------

    formatter = logging.Formatter(

        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    console_handler.setFormatter(
        formatter
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )