
from typing import *
from itertools import product

from numpy import array

from axolotl.instrument import *
from axolotl.util import *
from pyvisa import ResourceManager, constants

from functools import partial

@Instrument.register('SR830')
class SR830(SCPIInstrument):

    SENS_LEVELS_AMP = tuple(
        base * exponent 
        for base, exponent in product(
            (10**exp for exp in range(-15, -6)), 
            (2,5,10)
        )
    )

    SENS_LEVELS_VOL = tuple(array(SENS_LEVELS_AMP) * 1e6)

    def __init__(self, manager: 'InstrumentManager', address: str, cfg_path: str) -> None:
        super().__init__(manager, address, cfg_path)
        self._fp = ResourceManager().open_resource(address)
        self.interval = 0.01
        channels = {
            'Freq': ChannelBuilder(
                value_type=float,
                value_dimension=0
            ).accept(
                # SingleLineCmdModifier(
                #     read_cmd = 'FREQ?',
                #     write_cmd = 'FREQ {0:f}',
                #     translator = float
                # ),
                SCPICmdModifier(
                    nodes=('FREQ', ),
                    write_fmt='%f',
                    translator=float,
                    colon_start=False
                ),
                RangeModifier(
                    min=0.001, 
                    max=102000
                )
            ),
            'Amp': ChannelBuilder(
                value_type = float,
                value_dimension = 0,
                default_stepping=0.004
            ).accept(
                # SingleLineCmdModifier(
                #     read_cmd='SLVL?',
                #     write_cmd='SLVL {0:f}',
                #     translator = float
                # ),
                SCPICmdModifier(
                    nodes=('SLVL', ),
                    write_fmt='%f',
                    translator=float,
                    colon_start=False
                ),
                RangeModifier(
                    min=0.004,
                    max=5
                )
            ),
            'Phase': ChannelBuilder(**{
                'value_type': float,
                'value_dimension': 0,
                'default_stepping': 0
            }).accept(
                # SingleLineCmdModifier(
                #     read_cmd = 'PHAS?',
                #     write_cmd = 'PHAS {0:f}',
                #     translator = float
                # ),
                SCPICmdModifier(
                    nodes=('PHAS', ),
                    write_fmt='%f',
                    translator=float,
                    colon_start=False
                ),
                RangeModifier(
                    min = -180,
                    max = 180
                )
            ),
        }
        channels.update({
            f'Aux{i:d}': ChannelBuilder(
                value_type=float
            ).accept(
                SingleLineCmdModifier(
                    read_cmd = f'AUXV? {i:d}',
                    write_cmd = f'AUXV {i:d}, {{0:f}}',
                    translator = float
                ),
                RangeModifier(
                    min=-10.5,
                    max=10.5
                )
            )
            for i in (1, 2, 3, 4)
        })
        channels.update({
            f'I_{s:s}': ChannelBuilder(
                value_type=float,
                read_func=partial(self.__read_with_auto_adjust_sens, i),
                value_dimension=0
            )
            for i, s in enumerate(('x','y','r','θ'))
        })

        cfg_template = {
            'Names': ConfigDictEntry(
                {
                    k: ConfigEntry(str, default=k) for k in channels.keys()
                }, comment_before='Names for each channels'
            ),
            'Aux Output Limit': ConfigDictEntry(
                {
                    'min': ConfigEntry(float, -10.5, comments='Unit: V'),
                    'max': ConfigEntry(float, 10.5, comments='Unit: V')
                }
            )
        }

        _cfg = Config('SR830', cfg_template)
        _cfg.load()

        for i in range(1, 5):
            channels[f'Aux{i:d}'].accept(RangeModifier(
                **_cfg['Aux Output Limit']
            ))

        self.__channels = tuple(builder.build(_cfg['Names'][k], self) for k, builder in channels.items())
    
    def __read_with_auto_adjust_sens(self, idx:int) -> float:
        def read_sens():
            return int(self.query('SENS?'))
        
        def write_sens(s:int):
            self.write(f'SENS {s:d}')
        
        if 0 <= idx < 3:
            result = float(self.query(f'OUTP ? {idx:d}'))
            sens = read_sens()

            def refresh_sens(s):
                write_sens(s)
                result = float(self.query(f'OUTP ? {idx:d}'))
                sens = read_sens()
                return result, sens

            while abs(result / self.SENS_LEVELS_AMP[sens]) > 0.9 and sens < len(self.SENS_LEVELS_AMP) - 1:
                sens += 1
                result, sens = refresh_sens(sens)
            
            while abs(result / self.SENS_LEVELS_AMP[sens]) < 0.1 and sens > 0:
                sens -= 1
                result, sens = refresh_sens(sens)
            return result
        
        return float(self.query(f'OUTP ? {idx:d}'))


    def channel_list(self) -> Tuple['Channel']:
        return self.__channels
    
    def query(self, cmd: str):
        if not cmd.endswith('\n'):
            cmd += '\n'
        return self._fp.query(cmd)
    
    def write(self, cmd: str):
        return self._fp.write(cmd)

    def open(self):
        self._fp.open()
        self._fp.set_visa_attribute(constants.VI_ATTR_TERMCHAR_EN, constants.VI_TRUE)
