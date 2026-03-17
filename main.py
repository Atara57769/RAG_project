import logging
import ssl
from errors import RagProjectError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

try:
    # Log SSL paths for environment debugging
    logger.info("SSL verify paths: %s", ssl.get_default_verify_paths())
except Exception as exc:
    logger.exception("Unable to read SSL default verify paths")
    raise RagProjectError("Unable to read SSL default verify paths") from exc

