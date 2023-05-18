
from typing import *

from .channel import *
from .instrument import *

class SCPIInstrument(Instrument):
    def query(self, cmd: str):
        raise NotImplementedError()
    
    def write(self, cmd: str):
        raise NotImplementedError()


@dataclass
class SingleLineCmdModifier(ChannelModifier):
    read_cmd: Optional[str] = None
    write_cmd: Optional[str] = None
    translator: Optional[Callable[[str], ChannelValue]] = None

    def modify(self, builder: ChannelBuilder):
        builder.read_func_generator = lambda instr, name: (lambda: self.translator(instr.query(self.read_cmd)))
        builder.write_func_generator = lambda instr, name: (lambda x: instr.write(self.write_cmd % x))

    def validate_build(self, builder: ChannelBuilder, parent: Instrument, name: str):
        if isinstance(parent, SCPIInstrument):
            return
        else:
            # If query or write does not exists, this will throw exception
            q = parent.query('*IDN?')
            w = parent.write


def SCPICmdModifier(
        nodes: Tuple[str],
        write_fmt: str,
        translator: Optional[Callable[[str], ChannelValue]] = None
    ):
    cmd_base = ':'.join(nodes)
    if cmd_base and not cmd_base.startswith(':'):
        cmd_base = ':' + cmd_base
    
    read_cmd = cmd_base + '?'
    write_cmd = None
    if write_fmt:
        write_cmd = cmd_base + ' ' + write_fmt
    
    return SingleLineCmdModifier(
        read_cmd=read_cmd, 
        write_cmd=write_cmd,
        translator=translator
        )

