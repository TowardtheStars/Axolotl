from typing import *

from .instrument import *


def RangedChannel(
        self, parent: Instrument, name: str, 
        read_func: Optional[Callable[[], ChannelValue]] = None, 
        write_func: Optional[Callable[[ChannelValue, WriteFuncOpt], None]] = None, 
        range: Optional[Tuple[Optional[float], Optional[float]]] = None, 
        value_type: Optional[Type[ChannelValue]] = None, 
        value_dimension: int = -1, 
        default_stepping: Optional[ChannelValue] = None
        ) -> (Channel):
    if range:
        validator = lambda x: (x > range[0] if range[0] else True) and (x < range[1] if range[1] else True)
    else:
        validator = None
    return Channel(parent, name, read_func, write_func, validator, value_type, value_dimension, default_stepping)


