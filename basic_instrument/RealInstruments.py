


from typing import Tuple
from axolotl.backend.instrument import *
from axolotl.backend.util import *
from .raw.SR830 import SR830 as Raw_SR830
from .raw.Itek import Itek as Raw_Itek
from .raw.qdc_python import Qdc


def config_template(channel_list):

    return {
        'channel_names': ConfigDictEntry({
            name: ConfigEntry(str, name) for name in channel_list
        }, comment_after='Custom names for channels'),
        'include_channel': ConfigDictEntry({
            name: ConfigEntry(bool, True) for name in channel_list
        }),
        'change_interval': ConfigEntry(float, 0.001, comments='仪器两条指令之间最小 delay 单位：秒')
    }


@Instrument.register('SR830')
class SR830(Instrument):

    def __init__(self, manager, address, cfg_path='SR830') -> None:
        Instrument.__init__(self, manager, address, cfg_path)
        self._handle = Raw_SR830(address)

        channel_dict = {
            'I_x': {
                'read_func': lambda : self._handle.read_current(1)
            },
            'I_y': {
                'read_func': lambda : self._handle.read_current(2)
            },
            'R': {
                'read_func': lambda : self._handle.read_current(3)
            },
            'θ': {
                'read_func': lambda : self._handle.read_current(4)
            },
            'freq' : {
                'read_func': lambda : self._handle.read_freq(),
                'write_func': lambda v: self._handle.write_freq(v),
                'validator' : lambda v: 0 < v < 100e6 
            },
            'AMP' : {
                'read_func': lambda : self._handle.read_amp(),
                'write_func' : lambda v: self._handle.write_amp(v),
                'validator': lambda v: 0.004 < v < 3
            }
        }
        channel_dict.update(
            {
                'Aux{0}'.format(i): {
                    'read_func': lambda : self._handle.read_aux(i),
                    'write_func': lambda v : self._handle.write_aux(i, v),
                    'validator': lambda x : -10 < x < 10
                } for i in range(1, 5)
            }
        )

        self._cfg = Config('cfg_path', config_template(channel_dict.keys()))

        self._channel_list = [
            Channel(self, self._cfg['channel_names'][k], **v) for k, v in channel_dict.items() # dict as config into initializers
        ]

    def channel_list(self) -> tuple:
        return tuple(self._channel_list)

    def open(self):
        self._handle.open()

    def close(self):
        self._handle.close()


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



