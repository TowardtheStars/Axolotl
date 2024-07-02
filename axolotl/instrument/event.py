
from dataclasses import dataclass

# from .instrument import ChannelValue, Channel

@dataclass(repr=True)
class ChannelEvent:
    channel: 'Channel'

@dataclass(repr=True)
class ChannelWriteDoneEvent(ChannelEvent):
    success: bool
    target_value: 'ChannelValue'
    current_value: 'ChannelValue'

@dataclass(repr=True)
class ChannelWriteStepEvent(ChannelEvent):
    value: 'ChannelValue'
    
@dataclass(repr=True)
class ChannelWriteStartEvent(ChannelEvent):
    target_value: 'ChannelValue'
    current_value: 'ChannelValue'