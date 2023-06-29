import os
import os.path
from copy import deepcopy
from os.path import exists as fileexists
from os.path import join as joinpath
from typing import Any, Iterable, Optional, Union

from numpy import inf
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

program_root = joinpath(os.path.dirname(__file__), '..')
# cfg_root = joinpath(program_root, 'config')

cfg_root = joinpath(os.getcwd(), 'config')

__all__ = ['Config', 'ConfigDictEntry', 'ConfigEntry', 'program_root', 'cfg_root']

indent = 2

yaml = YAML()
yaml.allow_unicode = True
yaml.indent(mapping=indent, sequence=indent, offset=indent)
yaml.preserve_quotes = True  # type: ignore


translations = {
    'zh_cn': {
        'config_entry.type.name' : '类型',
        'config_entry.range.name' : '范围',
        'config_entry.default.name': '默认值'
    }
}

translation = translations['zh_cn']
encoding = 'utf8'

class ConfigEntry:

    AVAILABLE_TYPES = {
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'bool': bool
    }

    def __init__(self, type_, default=None, comments=None, range_:Optional[tuple]=None, no_comment=False) -> None:
        if type_ in ConfigEntry.AVAILABLE_TYPES.values() or ConfigEntry.AVAILABLE_TYPES.keys():
            self. _type = type_ 
        else:
            raise TypeError('Unsupported type: \'{}\''.format(type(type_).__name__))
        self._comment = []
        self._min = -inf
        self._max = inf
        self.set_comment(comments)
        self.no_comment = no_comment
        self.set_range(range_)
        self._default = default or type_()
    
    @property
    def comment(self) -> str:
        if self.no_comment:
            return ''
        result:list[Any] = deepcopy(self._comment)  # type: ignore
        result.append(r'%config_entry.type.name%: ' + self.typename)
        
        if self.isnumeric():
            result.append(r'%config_entry.range.name%: {0} ~ {1}'.format(*self.range))
        
        result.append(r'%config_entry.default.name%: {0}'.format(self.default_value))
        result_str = '\n'.join(result)
        for k, v in translation.items():
            result_str = result_str.replace('%' + k + '%', v)
        return result_str
        

    @property
    def typename(self) -> str:
        return self._type.__name__
    
    @property
    def default_value(self):
        return self._default

    @property
    def range(self) -> tuple[Any, Any]:
        return (self._min, self._max) if self.isnumeric() else None

    def validator(self, value) -> bool:
        if not isinstance(value, self._type):
            try:
                value = self._type(value)
            except:
                return False
        if self.isnumeric():
            return (value > self._min or self._min is None) and (value < self._max or self._max is None)
        
        return True

    def isnumeric(self) -> bool:
        return self._type is int or self._type is float

    def set_comment(self, cmt):
        if cmt is not None:
            self._comment = cmt if not isinstance(cmt, str) and isinstance(cmt, Iterable) else [cmt]
        return self

    def set_range(self, range_):
        if range_:
            self.set_min(range_[0])
            self.set_max(range_[-1])
        return self

    def set_min(self, min_):
        self._min = min_ if min_ else -inf
        return self

    def set_max(self, max_):
        
        self._max = max_ if max_ else inf
        return self

    def set_default(self, v):
        self._default = v if self.validator(v) else self._type()
        return self


class ConfigDictEntry:
    def __init__(self, data: dict, comment_before: Optional[Union[str, list, tuple]]=None, comment_after: Optional[Union[str, list, tuple]]=None, no_comment=False) -> None:
        self._comment_before = []
        if comment_before:
            if isinstance(comment_before, str):
                self._comment_before.append(comment_before)
            else:
                self._comment_before.extend(comment_before)
        self._comment_after = []
        if comment_after:
            if isinstance(comment_after, str):
                self._comment_after.append(comment_after)
            else:
                self._comment_after.extend(comment_after)
        self._data = data
        self.no_comment = no_comment

    def __getitem__(self, idx):
        return self._data[idx]

    def __setitem__(self, idx, value):
        return self._data.__setitem__(idx, value)

    @property
    def comment_before(self):
        return '\n'.join(self._comment_before) if not self.no_comment else ''

    @property
    def comment_after(self):
        return '\n'.join(self._comment_after) if not self.no_comment else ''

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def update(self, **kwargs):
        return self._data.update(**kwargs)



class Config:
    CFG_ROOT = cfg_root

    def __init__(self, name:str, template:Union[dict, ConfigDictEntry]) -> None:
        self._name = name
        self._template = template
        self._data = {}
        self.header_comment = []
        # self.__getitem__ = self._data.__getitem__
        self.keys = self._data.keys
        self.items = self._data.items
        self.values = self._data.values
        

    @property
    def name(self):
        return self._name

    @property
    def template(self):
        return self._template

    @property
    def abspath(self):
        if self.name.endswith(('.yml', 'yaml')):
            s = self.name
        else:
            s = self.name + '.yml'
        return os.path.abspath(joinpath(self.CFG_ROOT, s))

    def load(self):
        if fileexists(self.abspath):
            self._load_with_template()
        else:
            self._create_default()

    def _load_with_template(self):
        self._create_default(write_file=False)

        with open(self.abspath, 'r', encoding=encoding) as file:
            self._data.update(yaml.load(file))
        

        def iterate_check(data_dict, template_dict, current_path:list):
            err_current_path = []
            for k, v in template_dict.items():
                current_path.append(k)
                if k in data_dict.keys():
                    if isinstance(v, ConfigEntry):
                        if not v.validator(data_dict[k]):
                            err_current_path.append(deepcopy(current_path))
                    elif isinstance(v, (dict, ConfigDictEntry)):
                        result, errs = iterate_check(data_dict[k], template_dict[k], current_path)
                        if not result:
                            err_current_path.extend(errs)
                else:
                    err_current_path.append(deepcopy(current_path))
                    
                current_path.pop()
            return len(err_current_path) == 0, err_current_path

        iterate_check(self._data, self.template, [])

    def _create_default(self, write_file=True):

        def iterate_gen(d: Union[dict, ConfigDictEntry], current_path:list) -> CommentedMap:
            result = CommentedMap()
            
            for k, v in d.items():
                current_path.append(k)
                if isinstance(v, ConfigEntry):
                    result[k] = v.default_value
                    result.yaml_set_comment_before_after_key(k, before='\n' + v.comment, indent=(len(current_path) - 1) * indent)
                elif isinstance(v, dict):
                    result[k] = iterate_gen(v, current_path)
                elif isinstance(v, ConfigDictEntry):
                    result[k] = iterate_gen(v, current_path)
                    result.yaml_set_comment_before_after_key(k, before='\n' + v.comment_before, after=v.comment_after)
                current_path.pop()
                
            return result
        
        yaml_struct = iterate_gen(self._template, [])
        if len(self.header_comment) > 0:
            yaml_struct.yaml_set_start_comment('\n'.join(self.header_comment))
        if not os.path.exists(os.path.dirname(self.abspath)):
            os.makedirs(os.path.dirname(self.abspath))
        if write_file:
            with open(self.abspath, 'w', encoding=encoding) as file:
                yaml.dump(yaml_struct, file) 
        self._data = dict(yaml_struct)

   
    def get(self, index, default=None):
        return self._data.get(index, default)
        
    def __getitem__(self, index):
        return self._data.__getitem__(index)
    
    


    

if __name__ == '__main__':
    import sys
    
    template = {
        'int': ConfigEntry(int, 0, range_=(-1,1), comments='Integer Test'),
        'float': ConfigEntry(float, 1.1, comments=['Float Test', 'Multiline cmt test']),
        'dict': {
            'str': ConfigEntry(str, default='This is a string', comments=''),
            'str2': ConfigEntry(str, 'Another String', comments= 'Another test')
        },
        'config_dict': ConfigDictEntry({
            'a': ConfigEntry(int, 0 , comments='entry')
        }, "Comment Before Dict", "Comment After Dict"),
        'config_list': ConfigEntry(list, [1,2,3], comments='List Test')
    }
    t = Config('testcfg', template)
    t.load()
    print(t['int'])
 