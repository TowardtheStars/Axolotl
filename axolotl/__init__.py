
import logging
from axolotl.instrument import InstrumentManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)

InstrumentManager.CHANNEL_EVENT_BUS.mute_logger(True)

