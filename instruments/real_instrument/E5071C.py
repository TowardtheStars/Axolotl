

from typing import *
from numpy import array, ndarray

from axolotl.instrument import *

from pyvisa import ResourceManager

@Instrument.register()
class E5071C(SCPIInstrument):
    def __init__(self, manager: 'InstrumentManager', address: str, cfg_path: str) -> None:
        super().__init__(manager, address, cfg_path)
        self._fp = ResourceManager().open_resource(address)
        channels = {
            'ProbePower': ChannelBuilder(
                value_type=float
            ).accept(
                SCPICmdModifier(
                    nodes=('SOUR1', 'POW'),
                    write_fmt='%g',
                    translator=float
                )
            ),
            'CenterFreq': ChannelBuilder(
                value_type=float
            ).accept(
                SCPICmdModifier(
                    nodes=('SENS1', 'FREQ', 'CENT'),
                    write_fmt='%g',
                    translator=float
                )
            ),
            'CenterPower': ChannelBuilder(
                value_type=float
            ).accept(
                SCPICmdModifier(
                    nodes=('SOUR1', 'POW', 'CENT'),
                    write_fmt='%g',
                    translator=float
                )
            ),
            'BandWidth': ChannelBuilder(
                value_type=float
            ).accept(
                SCPICmdModifier(
                    nodes=('SENS1', 'FREQ', 'SPAN'),
                    write_fmt='%g',
                    translator=float
                )
            ),
            'IFBW': ChannelBuilder(
                value_type=float
            ).accept(
                SCPICmdModifier(
                    nodes=('SENS1', 'BAND'),
                    write_fmt='%g',
                    translator=float
                )
            ),
            'ScanLine': ChannelBuilder(
                value_type=ndarray,
                read_func=self.scan_line,
                value_dimension=0
            ),
            'ScanPoint': ChannelBuilder(
                value_type=ndarray,
                read_func=self.scan_point
            ),
            'WorkType': ChannelBuilder(
                value_type=int,
                write_func=self.set_worktype
            ),
            'CwFreq': ChannelBuilder(
                value_type=float
            ).accept(
                SCPICmdModifier(
                    nodes=('SENS1', 'FREQ', 'CW'),
                    write_fmt='%g',
                    translator=float
                )
            )
        }

    def query(self, cmd: str):
        if not cmd.endswith('\n'):
            cmd += '\n'
        return self._fp.query(cmd)

    def write(self, cmd:str):
        if not cmd.endswith('\n'):
            cmd += '\n'
        self._fp.write(cmd)

    def get_freq_list(self):
        list_str = self.query(':SENS1:FREQ:DATA?')
        return array(map(float, list_str))
    
    def get_amp_list(self):
        self.write(':CALC1:FORM MLIN')
        return array(map(float, self.query(':CALC1:DATA:FDAT?')[::2]))
    
    def get_ext_phase_list(self):
        self.write(':CALC1:FORM UPH')
        return array(map(float, self.query(':CALC1:DATA:FDAT?')[::2]))
    
    def scan_line(self):
        self.singleTrig()
        freq_list = self.get_freq_list()
        amp_list = self.get_amp_list()
        ext_phase_list = self.get_ext_phase_list()
        return array((freq_list, amp_list, ext_phase_list))
    
    def singleTrig(self):
        self.write(':INIT1:CONT 0')
        self.write(':TRIG:SOUR BUS')
        self.write(':INIT1')
        self.write(':TRIG:SING')

    def singleTrigRst(self):
        self.write(':INIT1:CONT 1')
        self.write(':TRIG:SOUR INT')

    def setPolar(self):
        self.write(':CALC1:FORM PLIN')
        self.write(':SENS1:SWE:POIN 2')
        self.write(':SENS1:SWE:TYPE POW')

    def scan_point(self):
        self.singleTrigRst(self)
        return array(map(float, self.query(':CALC1:MARK1:Y?')))

    def set_worktype(self, v:int):
        if v == -2:
            self.singleTrig()
        elif v == -1:
            self.singleTrigRst()
        elif v == 0:
            self.setPolar()
            self.singleTrigRst()
        elif v == 1:
            self.write(':SENS1:SWE:TYPE LIN')
            self.write(':CALC1:FORM MLIN')
        else:
            self.write(f':SENS1:SWE:POIN {v:d}')
            self.write(':SENS1:SWE:TYPE LIN')
            self.write(':CALC1:FORM MLIN')
