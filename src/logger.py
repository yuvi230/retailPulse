import logging
from datetime import datetime
from src.config import LOG_DIR


def get_logger(name: str) -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh = logging.FileHandler(LOG_DIR / f"pipeline_{datetime.now():%Y%m%d}.log")
    sh = logging.StreamHandler()
    for h in (fh, sh):
        h.setFormatter(fmt)
        logger.addHandler(h)
    return logger