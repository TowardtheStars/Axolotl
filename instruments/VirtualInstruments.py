
from axolotl.instrument import *
from axolotl.util import *


def config_template(channel_list):

    return {
        'channel_names': ConfigDictEntry({
            name: ConfigEntry(str, name) for name in channel_list
        }, comment_after='Custom names for channels'),
        'enable': ConfigDictEntry({
            name: ConfigEntry(bool, True) for name in channel_list
        })
    }

@Instrument.register('counter')
class Counter(Instrument):
    def __init__(self, manager: InstrumentManager, address: str, cfg_path: str) -> None:
        super().__init__(manager, address, cfg_path)
        self.data = {}
        template = {
            'channels': ConfigEntry(list, [], comments='自定义通道名，有多少名字就建立多少通道'),
            'interval': ConfigEntry(float, 0.01, comments='步进时间间隔，单位为秒')
        }
        self._cfg = Config(cfg_path, template)
        self._cfg.load()

        channel_dict = {
            k : {
                'name': k,
                'read_func': lambda key=k: self.data.get(key),
                'write_func': lambda v, key=k: self.__set_value(key, v),
                'default_stepping': 0.01,
                'value_type': float
            }
            for k in self._cfg['channels']
        }
        self.data = {
            k: 0 for k in self._cfg['channels']
        }

        self._channel_list = [
            Channel(self, **v) for v in channel_dict.values() # dict as config into initializers
        ]
    
    def __set_value(self, idx, value):
        self.data[idx] = value
        return True

    def channel_list(self) -> tuple:
        return tuple(self._channel_list)

    def open(self):
        pass

    def close(self):
        pass


