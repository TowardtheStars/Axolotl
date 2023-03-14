
from typing import *

from .channel import *
from .instrument import *

class SCPIInstrument(Instrument):
    def query(self, cmd: str):
        raise NotImplementedError()
    
    def write(self, cmd: str):
        raise NotImplementedError()


@dataclass
class SCPIModifier(ChannelModifier):
    read_cmd: Optional[str] = None
    write_cmd: Optional[str] = None   

    def modify(self, builder: ChannelBuilder):
        builder.read_func_generator = lambda instr, name: (lambda: instr.query(self.read_cmd))
        builder.write_func_generator = lambda instr, name: (lambda x: instr.write(self.write_cmd))

    def validate_build(self, builder: ChannelBuilder, parent: Instrument, name: str):
        if isinstance(parent, SCPIInstrument):
            return
        else:
            # If query or write does not exists, this will throw exception
            q = parent.query('*IDN?')
            w = parent.write

