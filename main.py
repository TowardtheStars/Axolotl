

import logging

logger = logging.getLogger('axolotl')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)

import axolotl
# 导入仪器包
import VirtualInstruments

axolotl.main()
