
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, MutableSet

import numpy as np

from axolotl.instrument import *
from axolotl.util import *

__all__ = ['ScanData', 'AxisInfo', 'ScanPlan']

@dataclass
class ScanData:
    x: np.ndarray   # first element is the outmost axis
    data: Union[Tuple['ScanData'], np.ndarray]

    def __init__(self, x, data: Union[Tuple['ScanData'], np.ndarray, int, float, complex]) -> None:
        self.x = np.atleast_1d(x)
        self.data = np.array(data) if isinstance(data, (float, int, complex)) else data
    

    def has_children(self) -> bool:
        return not isinstance(self.data, np.ndarray)
    
    def data_shape(self) -> Tuple[int]:
        return (1, ) if not isinstance(self.data, np.ndarray) else self.data.shape

    
@dataclass
class AxisInfo:
    name: str = ''
    start:float = 0
    step:float = 0
    end:float = 0
    interval:float = 0

    def get_range(self):
        result = list(np.arange(start=self.start, stop=self.end, step=self.step))
        result.append(self.end)
        return result

    def __iter__(self):
        return self.get_range()
    
    def size(self):
        return len(self.get_range())

    def __str__(self):
        return '{name}=({start}:{step}:{end})|{interval}s'.format(**self.__dict__)
    
    def __len__(self):
        return len(self.get_range())


    

@dataclass(repr=True)
class ScanPlan:
    _name:str = ''
    save_path: str = ''
    extra_info: str = ''
    
    channel_formula: Dict[ChannelId, str] = field(default_factory=dict)
    record_env_channel: MutableSet[ChannelId] = field(default_factory=set)
    scan_channel: MutableSet[ChannelId] = field(default_factory=set)

    axes: List[AxisInfo] = field(default_factory=list) # last item is the outermost axis

    plugin_config:Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self._name if len(self._name) > 0 else self.default_name
    
    @property
    def default_name(self) -> str:
        return 'ScanPlan@{0:x}'.format(id(self))
    
    @name.setter
    def name(self, v:str):
        self._name = v

    def axes_count(self) -> int:
        return len(self.axes)
    
    def shape(self) -> tuple[int]:
        return tuple(ax.size() for ax in self.axes)
    
    @staticmethod
    def encoder_cls():
        return ScanPlanEncoder
    
    @staticmethod
    def fromJson(d:dict) -> 'ScanPlan':
        d['_name'] = d['name']
        del d['name']
        o = ScanPlan(**d)
        o.axes = [AxisInfo(**axd) for axd in d['axes']]
        return o
    
    @property
    def workload(self) -> int:
        return np.product([axis.size() for axis in self.axes])

    

class ScanPlanEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ScanPlan):
            result = {
                name: getattr(o, name) for name in ('name', 'save_path', 'extra_info', 'channel_formula', 'record_env_channel', 'scan_channel', 'plugin_config')
            }
            result['axes'] = [axis.__dict__ for axis in o.axes]
            return result
        elif isinstance(o, AxisInfo):
            return o.__dict__
        elif isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)


