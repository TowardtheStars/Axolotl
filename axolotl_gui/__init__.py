
import logging
import sys
from typing import Tuple

from PyQt5.QtWidgets import QApplication


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)

def self_check() -> Tuple[bool, list]:
    logger.info('Running self checks...')
    result = True
    errinfo = []
    # python package check
    checklist = {
        'numpy', 
        'scipy', 
        'matplotlib.pyplot', 
    }

    missing_module = []
    for module_name in checklist:
        try:
            __import__(module_name)
        except ModuleNotFoundError as e:
            missing_module.append(module_name)
    if len(missing_module) > 0:
        result = False
        errinfo.append('Some python package not installed: ' + ', '.join(missing_module))

    return result, errinfo


def main():
    from axolotl.instrument import InstrumentManager
    from .mainwindow import MainWindow
    result, info = self_check()
    if not result:
        logger.error(info)
    else:
        logger.info('Check done, launching app...')

    app = QApplication(sys.argv)
    manager = InstrumentManager()
    manager.load_instruments()
    manager.open_all()
    ex = MainWindow(manager)
    sys.exit(app.exec_())
