
from typing import *

from .instrument import *

class SCPIInstrument(Instrument):
    def query(self, cmd: str):
        raise NotImplementedError()
    
    def write(self, cmd: str):
        raise NotImplementedError()

def SCPIChannel(
            parent: SCPIInstrument, name: str, 
            read_cmd: Optional[str] = None, 
            write_cmd: Optional[str] = None, 
            validator: Optional[Callable[[ChannelValue], bool]] = None, 
            value_type: Optional[Type[ChannelValue]] = None, 
            value_dimension: int = -1, 
            default_stepping: Optional[ChannelValue] = None
            ) -> Channel:
        read_func = lambda: parent.query(read_cmd)
        write_func = lambda x: parent.write(write_cmd.format(x))
        return Channel(parent, name, read_func, write_func, validator, value_type, value_dimension, default_stepping)



