

import logging
import time
from concurrent import futures
from enum import Enum
from threading import Lock
from typing import *

import numpy as np

from axolotl.util import *
from .event import *


__all__ = (
        'InstrumentId', 'ChannelId', 
        'Instrument', 'InstrumentManager', 'VirtualInstrument', 
        'ChannelWriteRacePolicy', 
        'Channel',
        'ChannelValue', 'WriteFuncOpt', 'ChannelReadFunc', 'ChannelWriteFunc'
        )

T = TypeVar("T", bound="Instrument")

InstrumentId = str
ChannelId = str

logger = logging.getLogger(__name__)


class DuplicateError(Exception):
    """Key duplication
    """
    pass


class Instrument(object):
    """Instrument class for a single instrument... obviously
    This is only a prototype. `channel_list` is the only method that matters
    """    

    __type_id__ = ''

    @classmethod
    @annotation
    def register(cls, id:str=None) -> Callable[[Type[T]], Type[T]]:
        """Register class as valid instrument type

        Args:
            id (str): Instrument type id for usage in config file.

        Returns:
            Callable[[Type[T]], Type[T]]: @Annotation
        """
        if not id:
            id = cls.__name__
        def _internal(clss:Type[T]):
            # register
            logger.info('Registering instrument type `%s` to id `%s`', clss.__qualname__, id)
            if id in InstrumentManager.__registered_instrument__.keys():
                raise DuplicateError("Duplicated key:'" + id + "'", InstrumentManager.__registered_instrument__[id])
            clss.__type_id__ = id
            InstrumentManager.__registered_instrument__[id] = clss
            return clss
        
        return _internal

    

    def __init__(self, manager:'InstrumentManager', address:str, cfg_path:str) -> None:
        self._lock = Lock()
        self._manager:'InstrumentManager' = manager
        self._address:str = address
        self.interval:float = 0.01

        self._id = ''

        self.locked: Callable[[], bool] = self._lock.locked
        self.release:Callable[[], None] = self._lock.release
        
        

    @property
    def manager(self):
        return self._manager

    @property
    def address(self) -> str:
        return self._address
    
    def channel_list(self) -> Tuple['Channel']:
        """Provide a list of channels to operate

        Returns:
            Tuple: a tuple contains channels
        """        
        return tuple()
    
    def channel_dict(self) -> Dict[str, 'Channel']:
        """Return a dict contains channel id : channel.
        Can only be called after instrument manager is constructed.

        Returns:
            Dict[str, 'Channel']: channel$id : channel
        """        
        return {channel.id : channel for channel in self.channel_list()}

    def open(self):
        """Open and connect instrument
        """        
        pass

    def close(self):
        """Disconnect and close the instrument
        """        
        pass

    def acquire(self, blocking:bool=True, timeout:float=-1):
        return self._lock.acquire(blocking=blocking, timeout=timeout)
    
    def setId(self, id):
        self._id = id
    
    @property
    def id(self) -> str:
        return self._id + '@' + self.__type_id__
    
    def __repr__(self) -> str:
        return '<Instrument {}>'.format(self.id)
    
    @classmethod
    def generate_config() -> Union[Dict, ConfigDictEntry]:
        """用于生成默认配置文件

        Args:
            path (str): 生成的文件名
        """        
        pass


class SystemInstrument(Instrument):
    def __init__(self, manager: 'InstrumentManager') -> None:
        super().__init__(manager, None, None)

    def channel_list(self) -> Tuple['Channel']:
        return (
            NullChannel(self, '（空）', read_func=lambda:None)
            ,)
    
class InstrumentManager:

    __registered_instrument__:dict[str, type['Instrument']] = {}
    CHANNEL_EVENT_BUS:EventBus = EventBus('ChannelEventBus')

    @staticmethod
    def config_template():
        return {
            'instruments': ConfigEntry(list, [], comments="""\
仪器列表
格式：
    - # 一个仪器
        type: 仪器类型名称，需要用 @Instrument.register(id:str) 在仪器类前注册
        id: 仪器自定义 id，不可重复，可选，便于保存和迁移扫描设置
        address: 地址，可以是一个地址列表，例如本源的 DAC
        config: config 文件夹中的配置文件路径
"""),
            'max_threads': ConfigEntry(int, default=16, range_=(0, 64), comments="""\
多线程控制数量，0 时禁用
            """
                )
        }

    def __init__(self) -> None:
        self.cfg:Config = Config('system', InstrumentManager.config_template())
        self.cfg.load()
        
        # self._instrument_types = import_instruments()

        self._instruments_by_id:Dict[str, 'Instrument'] = {}
        self._instruments_by_type:Dict[str, List['Instrument']] = {}
        self._channel_list:Dict[str, 'Channel'] = {}
        self._thread_executor = futures.ThreadPoolExecutor(self.cfg['max_threads'], thread_name_prefix='ChannelSetter')

        self.__sys_instr = SystemInstrument(self)
        
        

    def load_instruments(self):
        self._load_instruments()
        self._create_channel_list()

    
    def _load_instruments(self):
        logger.info('Loading instruments from config file...')
        for connect_info in self.cfg['instruments']:
            type_key = connect_info['type']
            if type_key in self.instrument_types.keys():
                _type:type['Instrument'] = self.instrument_types[type_key]
                inst:'Instrument' = _type(self, connect_info['address'], connect_info['config'])
                
                # Default id format: type_key + No. of instrument
                inst.setId((type_key + '{0:d}'.format(len(self._instruments_by_type.get(type_key, [])))) if 'id' not in connect_info.keys() else connect_info['id'])

                logger.info('Found instrument <{id}> of type [{type}]'.format(id=inst.id, type=inst.__type_id__))

                self._instruments_by_id[inst.id] = inst
                if type_key not in self._instruments_by_type:
                    self._instruments_by_type[type_key] = list()
                self._instruments_by_type[type_key].append(inst)
            else:
                logger.error('Cannot recognize instrument type `%s`', type_key)
        logger.info('Instrument load complete')
    
    def _create_channel_list(self):
        channel_list:List['Channel'] = []
        logger.info('Create channel list...')
        for instr in self.instruments:
            try:
                for i, channel in enumerate(instr.channel_list()):
                    # channel.setId(i)
                    
                    channel_list.append(channel)
                
                
                logger.info('Included channel {ch} from instrument {ins}'.format(ch=instr.channel_list(), ins=instr))
            except :
                
                raise TypeError('Instrument `%(instr)s` cannot provide channel list.'.format(instr=instr))

        for i, channel in enumerate(channel_list):
            self._channel_list[channel.id] = channel
            channel._set_integer_index(i)
        
    def open_all(self):
        for instr in self.instruments:
            instr.open()

    def close_all(self):
        for instr in self.instruments:
            instr.close()


    @property
    def instrument_types(self):
        return self.__class__.__registered_instrument__

    @property
    def instruments(self) -> Tuple[Instrument]:
        return (self.__sys_instr, ) + tuple(self._instruments_by_id.values())

    @property
    def channel_list(self):
        return tuple(self._channel_list.values())
    
    def get_channel(self, idx:str) -> Optional['Channel']:
        return self._channel_list.get(idx, None)
    
    def get_channel_strong(self, idx:str) -> 'Channel':
        return self._channel_list[idx]
    
    def get_instrument(self, idx:str) -> Optional['Instrument']:
        return self._instruments_by_id.get(idx, None)
    
    def get_instrument_strong(self, idx:str) -> 'Instrument':
        return self._instruments_by_id[idx]
    
    @property
    def thread_executor(self):
        return self._thread_executor


class VirtualInstrument(Instrument):
    def __init__(self, instruments:List[Instrument], manager:InstrumentManager, address:str, cfg_path:str) -> None:
        super().__init__(manager, address, cfg_path)
        self.instruments = instruments

    def acquire(self, blocking:bool=True, timeout:float=-1) -> None:
        for ins in self.instruments:
            ins.acquire(blocking=blocking, timeout=timeout)
    
    def locked(self) -> bool:
        return any(ins.locked() for ins in self.instruments)
    
    def release(self) -> None:
        for ins in self.instruments:
            ins.release()

    pass


class ChannelWriteRacePolicy(Enum):
    WAIT = 0                    # block
    ABORT = 1                   # abort new
    CHANGE_ENDPOINT = 2         # abort old
    APPEND_PATH = 3             # append path to current queue

    EXCEPTION = 0xf0            # throw exceptions


ChannelValue = TypeVar('ChannelValue')
class WriteFuncOpt(TypedDict):
    interval:Optional[ChannelValue]

ChannelReadFunc = Callable[[], ChannelValue]
ChannelWriteFunc = Callable[[ChannelValue, WriteFuncOpt], None]

class Channel:
    """Abstract channel for every readable / writeable parameter of instruments.
    """

    
    def __init__(self, parent:Instrument, name:str,
        read_func: Optional[ChannelReadFunc]=None,  
        write_func: Optional[ChannelWriteFunc]=None, 
        validator: Optional[Callable[[ChannelValue], bool]]=None, 
        value_type: Optional[Type[ChannelValue]]=None, 
        value_dimension: int=-1,
        default_stepping: Optional[ChannelValue]=None,
        data_fixer: Optional[Callable[[ChannelValue], ChannelValue]]=None
        ):
        """Create Channel

        Args:
            parent (Instrument): parent instrument

            name (str): channel name

            read_func (Callable, optional): read function, requires return value and should not need any argument. Defaults to None.

            write_func (Callable, optional): write function, should take 1 argument and 1 keyword arguments with key 'interval'. Defaults to None.
                Example: write_func(value, interval:float=None)

            value_type (type, optional): type of the channel. Defaults to None.

            value_dimension (int, optional): dimension of data of this channel, only valid when the channel is readable. Defaults to -1 for auto detection.

            default_stepping (float, optional): default stepping distance of this channel. Defaults to 0.01.

            data_fixer (Callable, Optional): fix write input when invalid input detected
        Returns:
            Channel: a readable/writeable parameter interface
        """         
        

        self._parent: Instrument = parent
        self._manager: InstrumentManager = parent.manager

        self._read: Optional[ChannelReadFunc] = read_func
        self._write: Optional[ChannelWriteFunc] = write_func
        self._validate: Callable[[ChannelValue], bool] = validator or (lambda x:True)
        self._fix_value: Optional[Callable[[ChannelValue], ChannelValue]] = data_fixer

        self.stepping: ChannelValue = default_stepping or 0.01
        self.name:str = name

        self._dimension: int = value_dimension
        self._value_type: Type[ChannelValue] = value_type

        # self._write_thread:Timer = Timer(1, lambda:None)
        self.__occupied = False
        self.__stepping_list = []
        self.__stepping_lock = Lock()
        self._ft:futures.Future = futures.Future()

        self.__id = name

        self.__integer_index:int = None

        self.__validate_type_and_dimension()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Channel):
            return __o.id == self.id
        return False

    
    def __validate_type_and_dimension(self):
        # Validate value type and dimension
        if self.readable():
            data = self._read() # type: ignore
            if self._value_type is not None:
                if np.issubdtype(type(data), np.number) and np.issubdtype(self._value_type, np.number):
                    type_includes = {
                        int: 0,
                        float: 1, 
                        complex: 2
                    }
                    a = min(v for k, v in type_includes.items() if np.issubdtype(type(data), k))
                    b = min(v for k, v in type_includes.items() if np.issubdtype(self._value_type, k))
                    if a > b:
                        logger.warn('Unmatched Channel value type for %s:\n\tGiven %s, but reading returns %s', self, self._value_type, type(data))
                    
                elif not np.issubdtype(type(data), self._value_type):

                    logger.warn('Unmatched Channel value type for %s:\n\tGiven %s, but reading returns %s', self, self._value_type, type(data))
            else:
                self._value_type = type(data)
            if self._dimension == -1:
                if np.issubdtype(self._value_type, np.ndarray):
                    if self._value_type != np.ndarray:
                        data = np.ndarray(data)
                    _dimension = len(data.shape)
                else:
                    _dimension = 0
                
                # self._dimension = _dimension
                if self._dimension != _dimension and self._dimension != -1:
                    logger.warn('Unmatched Channel dimension for %s:\n\tGiven %s, but reading returns %s',self, self._dimension, _dimension)
                self._dimension = _dimension

    @property
    def parent(self) -> Instrument:
        """Parent instrument of this channel, read only

        Returns:
            Instrument: parent instrument
        """        
        return self._parent
    
    @property
    def index(self) -> int:
        return self.__integer_index
    
    # Do not call this!
    def _set_integer_index(self, v:int):
        self.__integer_index = v

    @property
    def manager(self) -> InstrumentManager:
        """Manager of this channel, read only

        Returns:
            InstrumentManager: manager
        """        
        return self._manager

    def read(self) -> ChannelValue:
        """Read current value of this channel
            Should not throw error or warning under any circumstances, when failed to read, return None
        Returns:
            Any: read value, convert into numpy array if value is number or matrix
        """        
        if self.readable():
            try:
                value = self._read() # type: ignore
                if np.issubdtype(self._value_type, np.number):
                    value = np.array(value)
                return value
            except Exception as e:
                logger.error('An error while reading a readable channel: ' + str(self), exc_info=True)
                raise e
        return None
            
    @property
    def dimension(self) -> int:
        """Dimension of the channel data, defined in constructor, read only

        Returns:
            int: dimension of the channel data, 0 for point data, 1 for line data, 2 for matrix data, etc.
        """        
        return self._dimension

    @property
    def value_type(self) -> Optional[Type[ChannelValue]]:
        """Value type of the channel data, defined in constructor, read only

        Returns:
            _type_: a value type
        """        
        return self._value_type

    def write(self, value: ChannelValue, race_policy:ChannelWriteRacePolicy = ChannelWriteRacePolicy.CHANGE_ENDPOINT) -> futures.Future:
        """Set value of this channel
        If called again when is_setting, launch racing policy

        Args:
            value (Any): target value, its type must be consistent with predefined value_type

        """        
        def stepped_write() -> futures.Future[bool]:
            if self.is_setting():
                logger.info('Stepping list is not empty, triggering racing policy %s', race_policy)

                # Trigger race policy
                if race_policy is ChannelWriteRacePolicy.WAIT:
                    while len(self.__stepping_list) > 0: pass
                if race_policy is ChannelWriteRacePolicy.ABORT:
                    logger.warn('Racing policy is %s, abort new target value', race_policy)
                if race_policy is ChannelWriteRacePolicy.APPEND_PATH:
                    with self.__stepping_lock:
                        init_value = self.__stepping_list[-1]
                        self.__stepping_list.extend(list(np.arange(init_value, value, self.stepping * np.sign(value - init_value))))
                        self.__stepping_list.append(value)
                if race_policy is ChannelWriteRacePolicy.CHANGE_ENDPOINT:
                    with self.__stepping_lock:
                        init_value = self.read()
                        self.__stepping_list = list(np.arange(init_value, value, self.stepping * np.sign(value - init_value)))
                        self.__stepping_list.append(value)
                if race_policy is ChannelWriteRacePolicy.EXCEPTION:
                    raise Exception() # TODO

                        
            else:
                init_value = self.read()
                self.__stepping_list = list(np.arange(init_value, value, self.stepping if value > init_value else -self.stepping))
                self.__stepping_list.append(value)

                def run() -> bool:
                    try:
                        while len(self.__stepping_list) > 0:
                            
                            # Acquire instrument lock to perform actions
                            self.parent.acquire()
                            # Acquire stepping lock to read and pop data
                            with self.__stepping_lock:
                                V = self.__stepping_list.pop(0)
                                self.fire_event(ChannelWriteStepEvent(self, V))
                                self._write(V) # type: ignore. Ignore possible None check because self.writable() has checked that
                            
                            time.sleep(self.parent.interval)
                            self.parent.release()
                    except Exception as e:
                        print(e)
                        return False
                    return True
                
                
                self._ft = self.manager.thread_executor.submit(run)
                self._ft.add_done_callback(self.__set_done(value))
            return self._ft

        if self.writable():
            if (not self._validate(value)) and self._fix_value: # fix value if necessary and possible
                value = self._fix_value(value)
            if self._validate(value):
                if self.readable() and self.stepping and self.parent.interval > 0 and np.abs(self.stepping) > 0 and self.value_type is not str:
                    return stepped_write()
                else:
                    self._ft = self.manager.thread_executor.submit(self._write, value) # type: ignore
                    self._ft.add_done_callback(self.__set_done(value))
                
            return self._ft
        
        return self._ft
    
    def fire_event(self, event):
        self.manager.CHANNEL_EVENT_BUS.fire_event(event)
    
    def stop_writing(self):
        if self._ft:
            result = self._ft.cancel()
            
            if result and len(self.__stepping_list) > 0:
                self.fire_event(ChannelWriteDoneEvent(self, False, self.__stepping_list[-1], self.read()))
                with self.__stepping_lock:
                    self.__stepping_list.clear()
                
            pass
        return False
    
    def __set_done(self, target_value) -> Callable[[futures.Future[bool]], None]:
        def callback(ret: futures.Future[bool]):
            self.manager.CHANNEL_EVENT_BUS.fire_event(
                ChannelWriteDoneEvent(self, ret.result(), target_value, self.read() if self.readable() else None)
            )
        return callback
        

    def readable(self) -> bool: 
        """If this channel is readable

        Returns:
            bool: If this channel is readable
        """        
        return self._read is not None

    def writable(self) -> bool: 
        """If this channel is writeable

        Returns:
            bool: If this channel is writeable
        """        
        return self._write is not None
    
    def is_setting(self) -> bool:
        return self._ft.running()
    
    def __str__(self) -> str:
        return f'<Channel {self.name} attached to {self.parent:s}>'
    
    def __repr__(self) -> str:
        return f'<Channel {self.id}>'
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    
    def occupied(self) -> bool:
        return self.__occupied
    
    def setOccupied(self, value:bool) -> None:
        self.__occupied = value
        return None
    
    @property
    def id(self) -> ChannelId:
        return f'{self.parent.id}:{self.__id}'
    
    def setId(self, idx):
        self.__id = idx

class NullChannel(Channel):
    @property
    def id(self) -> ChannelId:
        return None



