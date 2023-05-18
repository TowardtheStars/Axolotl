
from typing import * 

import socket

from axolotl.instrument import *
from axolotl.util import *

@Instrument.register()
class AMI(SCPIInstrument):
    def __init__(self, manager: 'InstrumentManager', address: str, cfg_path: str) -> None:
        super().__init__(manager, address, cfg_path)
        
        self.cfg = Config('AMI', {
            'Port': ConfigEntry(int, 7180, comments='Port of AMI TCPIP interface', range_=(1, 65534)),
            'Max Field': ConfigEntry(float, 6000, 'Max magnet field in mT', range_=(0, ))
        })

        self.cfg.load()

        self._fp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        channel_builders = {
            'P.Switch': ChannelBuilder()
                .accept(
                    SCPICmdModifier(
                        nodes=(''),
                        write_fmt='%d'
                    )
                ),
            'Field': ChannelBuilder()
                .accept(
                    SCPICmdModifier(
                        nodes=('',)
                    )
                )
        }

    def open(self):
        self._fp.connect((self.address, self.cfg['Port']))

    def write(self, cmd:str):
        self._fp.send(cmd.encode('utf-8'))

    def query(self, cmd:str):
        self._fp.send(cmd.encode('utf-8'))
        return self._fp.recv(1024).decode('utf-8')
    
    def close(self):
        self._fp.close()
        return super().close()
