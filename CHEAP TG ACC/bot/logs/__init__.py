import logging, sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir="logs"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if root.handlers:
        return logging.getLogger("bot")
    fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter(fmt))
    root.addHandler(sh)
    for name, fn in [("bot","bot.log"),("errors","errors.log")]:
        h = RotatingFileHandler(Path(log_dir)/fn, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
        h.setFormatter(logging.Formatter(fmt))
        logging.getLogger(name).addHandler(h)
    return logging.getLogger("bot")
