
import typing, logging
from PyQt5.QtCore import QThread, QObject, pyqtSignal

from axolotl.automation.scan.events import *

logger = logging.getLogger(__name__)


class Mediator(QObject):
    scan_event_signal = pyqtSignal(ScanEvent)

    def __init__(self) -> None:
        super().__init__()
        SCAN_EVENT_BUS.register(ScanEvent, listener=self.__event)
    
    def __event(self, event:ScanEvent):
        self.scan_event_signal.emit(event)
        logger.debug('Signal emitted')

mediator = Mediator()

__all__ = ('mediator', )
    