

from typing import Tuple

from .OriginDAC.qdc_python import Qdc
from .RealInstruments import config_template

from axolotl.instrument import *
from axolotl.util import *

@Instrument.register('OriginDAC')
class OriginDAC(Instrument):
    
    def __init__(self, manager, address, cfg_path='OriginDAC'):
        super().__init__(manager, address, cfg_path)
        self._handle = Qdc(self.address)
        channel_dict = {
            'V{0}'.format(i + 1):{
                'read_func': lambda : self._handle.query_dc(i + 1),
                'write_func': lambda v: self._handle.set_dc(i + 1, v),
                'validator': lambda v: -10 <= v <= 10
            } for i in range(8 * len(address))
        }
        self._size = 8 * len(address)
        self._cfg = Config(cfg_path, config_template(channel_dict.keys()))
        self._channel_list = [
            Channel(self, k, **v) for k, v in channel_dict.items()
        ]

    def channel_list(self) -> Tuple:
        return tuple(self._channel_list)

    def open(self):
        self._handle.open()
        for i in range(self._size):
            self._handle.output_on(i + 1)
    
    def close(self):
        self._handle.close()

    pass


