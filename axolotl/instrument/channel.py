from typing import *
from dataclasses import dataclass, field

from .instrument import *

@dataclass
class ChannelBuilder:
    read_func: Optional[ChannelReadFunc] = None
    write_func: Optional[ChannelWriteFunc] = None
    validator: Optional[Callable[[ChannelValue], None]] = None
    value_type: Optional[Type[ChannelValue]] = None
    value_dimension: int = -1
    default_stepping: Optional[ChannelValue] = None
    data_fixer: Optional[Callable[[ChannelValue], ChannelValue]] = None

    read_func_generator:Optional[Callable[[Instrument, str], ChannelReadFunc]] = None
    write_func_generator:Optional[Callable[[Instrument, str], ChannelWriteFunc]] = None

    _build_check_list:Dict['ChannelModifier', Callable[['ChannelBuilder', Instrument, str], bool]] = field(default_factory=dict)

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
            read_func = self.read_func or (self.read_func_generator(parent, name) if self.read_func_generator else None),
            write_func = self.write_func or (self.write_func_generator(parent, name) if self.write_func_generator else None),
            validator = self.validator,
            value_type = self.value_type,
            value_dimension = self.value_dimension,
            default_stepping = self.default_stepping,
            data_fixer = self.data_fixer
            )

class ChannelModifier:
    def modify(self, builder:ChannelBuilder):
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
        builder.validator = lambda x: (min_validate(x) and max_validate(x))
        if self._fixer:
            def fixer(v):
                if not min_validate(v) and self._min_closure and self._min:
                    return self._min
                if not max_validate(v) and self._max_closure and self._max:
                    return self._max
                return v
            builder.data_fixer = fixer


class MakeFloat(ChannelModifier):
    def modify(self, builder: ChannelBuilder):
        if builder.write_func:
            builder.write_func = lambda x: builder.write_func(float(x))
        if builder.read_func:
            builder.read_func = lambda: float(builder.read_func())

        if builder.write_func_generator:
            builder.write_func_generator = lambda parent, str: lambda x: builder.write_func_generator(parent, str)(float(x))
        if builder.read_func_generator:
            builder.read_func_generator = lambda parent, str: lambda: float(builder.read_func_generator(parent, str)())