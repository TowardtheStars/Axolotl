
from typing import Tuple
from axolotl.instrument.instrument import *
from axolotl.instrument.channel import *
from axolotl.instrument.scpi import *

from pyvisa import ResourceManager


@Instrument.register('34410A')
class MM34410A(SCPIInstrument):
    def __init__(self, manager: InstrumentManager, address: str, cfg_path: str) -> None:
        super().__init__(manager, address, cfg_path)
        self._fp = ResourceManager().open_resource(address)
        channels = {
            'Voltage': ChannelBuilder(
                value_type = float
            ).accept(
                SCPICmdModifier(
                    nodes=('READ', ),
                    translator=float
                )
            )
        }
        self._channels = (builder.build(k, self) for k , builder in channels.items())



    def channel_list(self) -> Tuple[Channel]:
        return self._channels
    
    def query(self, cmd: str):
        if not cmd.endswith('\n'):
            cmd += '\n'
        return self._fp.query(cmd)

    def write(self, cmd:str):
        if not cmd.endswith('\n'):
            cmd += '\n'
        self._fp.write(cmd)

    def open(self):
        self._fp.open()
    
    def close(self):
        self._fp.close()
    

