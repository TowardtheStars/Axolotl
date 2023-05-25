
from typing import Type
import logging

from PyQt5.QtCore import QObject, pyqtSignal

from axolotl.automation.scan.events import *
from axolotl.instrument import *
from axolotl.util import EventBus, Event, annotation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def event2signal(event_type: Event, bus: EventBus, signal: pyqtSignal):

    def callback(event: Event):
        signal.emit(event)
        logger.debug('Emitted signal for event %s', event)
    bus.register(event_type, listener=callback)


def signal_name(evt_t: Type) -> str:
    return f'__signal_{evt_t.__name__}'


def signal(self, evt_t: Type) -> pyqtSignal:
    ret = getattr(self, signal_name(evt_t), None)
    return ret


@annotation
def event_listener(self, evt_t):

    def annotator(listener: callable):
        logger.debug(
            f'Register listener {listener.__name__} to signal {signal_name(evt_t)}')
        self.signal(evt_t).connect(listener)
        return listener
    return annotator


def EventBusMediator(bus: EventBus, event_types: tuple[type]) -> object:
    """将自定义的事件系统转换为 PyQt5 的信号的信号中继器。
    实现了 event_listener 接口，可以用修饰器的方式修饰事件侦听函数

    Args:
        bus (EventBus): 自定义事件系统总线
        event_types (tuple[type]): 事件系统总线下的事件类型

    Returns:
        object: 信号中继器
    """
    members = {
        'event_listener': event_listener,
        'signal': signal
    }
    members.update({
        # 根据事件列表生成信号
        signal_name(evt_t): pyqtSignal(evt_t) for evt_t in event_types
    })

    __t = type(f'__Mediator_{bus.name}', (QObject, ), members)
    obj = __t()

    for evt_t in event_types:
        event2signal(evt_t, bus, getattr(obj, signal_name(evt_t))
                     )      # 将实例中的信号触发事件侦听器注册到事件总线上

    return obj


# 这里的中介者都是 axolotl_gui 包私有的，不考虑后续增加内容，需要时直接覆盖变量或直接修改这里的代码
SCAN_EVENT_MEDIATOR = EventBusMediator(
    SCAN_EVENT_BUS,
    (
        ScanEvent,
        AxisEvent,
        AxisPreIterateEvent,
        AxisChangeEvent,
        AxisPostIterateEvent,
        PreMeasureEvent,
        PostMeasureEvent,
        ScanStartEvent,
        ScanEndEvent,
    )
)
CHANNEL_EVENT_MEDIATOR = EventBusMediator(
    InstrumentManager.CHANNEL_EVENT_BUS,
    (
        ChannelWriteDoneEvent,
        ChannelWriteStepEvent,
        ChannelEvent,
    )
)

__all__ = ('SCAN_EVENT_MEDIATOR', 'CHANNEL_EVENT_MEDIATOR')
