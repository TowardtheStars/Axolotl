from types import MethodType
from typing import *
from pint import Unit

from .instrument import *

class ChannelBuilder:
    
    __slot__ = (
        '_read_func', '_write_func', '_validator', '_value_type', '_value_dimension', '_default_stepping',
        '_data_fixer', '_unit', '_read_func_generator', '_write_func_generator', '_build_check_list'
    )
    
    def __init__(
        self, 
        read_func: Optional[ChannelReadFunc] = None, write_func: Optional[ChannelWriteFunc] = None,
        validator: Optional[Callable[[ChannelValue], None]] = None,
        value_type: Optional[Type[ChannelValue]] = None,
        value_dimension: int = -1,
        default_stepping: Optional[ChannelValue] = None,
        data_fixer: Optional[Callable[[ChannelValue], ChannelValue]] = None,
        unit: Optional[Union[str, Unit]] = None,

        read_func_generator:Optional[Callable[[Instrument, str], ChannelReadFunc]] = None,
        write_func_generator:Optional[Callable[[Instrument, str], ChannelWriteFunc]] = None,
        ):
        self._read_func = read_func
        self._write_func = write_func
        self._validator = validator
        self._value_type = value_type
        self._value_dimension = value_dimension
        self._default_stepping = default_stepping
        self._data_fixer = data_fixer
        self._unit = unit
        self._read_func_generator = read_func_generator
        self._write_func_generator = write_func_generator
        self._build_check_list = list()
        
    def read_func(self, read_func:ChannelReadFunc) -> 'ChannelBuilder':
        self._read_func = read_func
        return self
    
    def write_func(self, write_func:ChannelWriteFunc) -> 'ChannelBuilder':
        self._write_func = write_func
        return self

    def validator(self, validator:Callable[[ChannelValue], None]) -> 'ChannelBuilder':
        self._validator = validator
        return self

    def value_type(self, value_type:Type[ChannelValue]) -> 'ChannelBuilder':
        self._value_type = value_type
        return self
    
    def value_dimension(self, value_dimension:int) -> 'ChannelBuilder':
        self._value_dimension = value_dimension
        return self

    def default_stepping(self, default_stepping:ChannelValue) -> 'ChannelBuilder':
        self._default_stepping = default_stepping
        return self
    
    def data_fixer(self, data_fixer:Callable[[ChannelValue], ChannelValue]) -> 'ChannelBuilder':
        self._data_fixer = data_fixer
        return self

    def unit(self, unit:Union[str, Unit]) -> 'ChannelBuilder':
        self._unit = unit
        return self
    
    def read_func_generator(self, read_func_generator:Callable[[Instrument, str], ChannelReadFunc]) -> 'ChannelBuilder':
        self._read_func_generator = read_func_generator
        return self

    def write_func_generator(self, write_func_generator:Callable[[Instrument, str], ChannelWriteFunc]) -> 'ChannelBuilder':
        self._write_func_generator = write_func_generator
        return self
    
    
    def accept(self, *modifiers:'ChannelModifier'):
        for modifier in modifiers:
            modifier.modify(self)
        return self
    
    def build_check(self, parent:Instrument, name:str) -> None:
        """Throw exceptions when conditions not matched
        """
        for k, validator in self._build_check_list.items():
            validator(self, parent, name)
                

    def build(self, name:str, parent:Instrument=None) -> Channel:
        self.build_check(parent, name)
        return Channel(
            parent = parent, 
            name = name, 
            read_func = self._read_func or (self._read_func_generator(parent, name) if self._read_func_generator else None),
            write_func = self._write_func or (self._write_func_generator(parent, name) if self._write_func_generator else None),
            validator = self._validator,
            value_type = self._value_type,
            value_dimension = self._value_dimension,
            default_stepping = self._default_stepping,
            data_fixer = self._data_fixer,
            unit = self._unit,
            )
        
    def __str__(self):
        return f'ChannelBuilder({self._name or id(self)})'
    
    def __repr__(self) -> str:
        return 'ChannelBuilder' + str((f'{k[1:]}={self.__dict__[k]!r}' for k in self.__slot__))

class ChannelModifier:
    def modify(self, builder:ChannelBuilder) -> None:
        raise NotImplementedError()
    
    def validate_build(self, builder:ChannelBuilder, parent:Instrument, name:str):
        pass


class RangeModifier(ChannelModifier):
    def __init__(self, min=None, max=None, min_closure=True, max_closure=True, add_fixer=True) -> None:
        self._min = min
        self._max = max
        self._min_closure = min_closure
        self._max_closure = max_closure
        self._fixer = add_fixer

    def _make_min_validator(self):
        if self._min:
            if self._min_closure:
                return lambda x: x >= self._min
            else:
                return lambda x: x > self._min
        else:
            return lambda x: True

    def _make_max_validator(self):
        if self._max:
            if self._max_closure:
                return lambda x: x <= self._max
            else:
                return lambda x: x < self._max
        else:
            return lambda x: True

    def modify(self, builder:ChannelBuilder):
        min_validate = self._make_min_validator()
        max_validate = self._make_max_validator()
        builder._validator = lambda x: (min_validate(x) and max_validate(x))
        if self._fixer:
            def fixer(v):
                if not min_validate(v) and self._min_closure and self._min:
                    return self._min
                if not max_validate(v) and self._max_closure and self._max:
                    return self._max
                return v
            builder._data_fixer = fixer


class MakeFloat(ChannelModifier):
    def modify(self, builder: ChannelBuilder):
        if builder._write_func:
            builder._write_func = lambda x: builder._write_func(float(x))
        if builder._read_func:
            builder._read_func = lambda: float(builder._read_func())

        if builder._write_func_generator:
            builder._write_func_generator = lambda parent, str: lambda x: builder._write_func_generator(parent, str)(float(x))
        if builder._read_func_generator:
            builder._read_func_generator = lambda parent, str: lambda: float(builder._read_func_generator(parent, str)())
            
            
class MakeInt(ChannelModifier):
    def modify(self, builder: ChannelBuilder):
        if builder._write_func:
            builder._write_func = lambda x: builder._write_func(int(x))
        if builder._read_func:
            builder._read_func = lambda: int(builder._read_func())

        if builder._write_func_generator:
            builder._write_func_generator = lambda parent, str: lambda x: builder._write_func_generator(parent, str)(int(x))
        if builder._read_func_generator:
            builder._read_func_generator = lambda parent, str: lambda: int(builder._read_func_generator(parent, str)())
            

class InnerVariableModifier(ChannelModifier):
    def __init__(self, var_name=None):
        self._var_name = var_name
        
    def modify(self, builder:ChannelBuilder):
        builder._write_func_generator = lambda parent, channel_name: lambda x: setattr(parent, self._var_name or channel_name, x)
        builder._read_func_generator = lambda parent, channel_name: lambda : getattr(parent, self._var_name or channel_name)
