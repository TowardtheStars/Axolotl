
from typing import Type
import logging

from PyQt5.QtCore import QThread, QObject, pyqtSignal

from axolotl.automation.scan.events import ScanEvent, SCAN_EVENT_BUS
from axolotl.instrument import InstrumentManager, ChannelEvent
from axolotl.util import EventBus, Event

logger = logging.getLogger(__name__)

def event2signal(event_type: Event, bus:EventBus, signal:pyqtSignal):
        
    def callback(event:Event):
        signal.emit(event)
        logger.debug('Emitted signal for event %s', event)
    bus.register(event_type, listener=callback)

class Mediator(QObject):
    scan_event_signal = pyqtSignal(ScanEvent)
    channel_event_signal = pyqtSignal(ChannelEvent)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        event2signal(ScanEvent, SCAN_EVENT_BUS, self.scan_event_signal)
        event2signal(ChannelEvent, InstrumentManager.CHANNEL_EVENT_BUS, self.channel_event_signal)


mediator = Mediator()

__all__ = ('mediator', )
    