import logging

logger = logging.getLogger("AzizAI")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
fmt = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
handler.setFormatter(fmt)
logger.addHandler(handler)
