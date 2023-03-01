# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 15:39:42 2020

@author: hanwe
"""


#    %% Abstract
#    PBiasDac：itek
#    transmission protocol: +instrument/Protocol
#    %% Index
#    @read(channel)(volt)
#    @set(channel,value)(volt)
#    %% Comments
#    channel range: 1~16
#    set_volt range: -10V ~ +10V

import pyvisa
from .resources import resource_manager

class Itek():
    # connect
    def __init__(self, *address):
        self.__fp:pyvisa.resources.MessageBasedResource = resource_manager.open_resource(address)
        self.delay = 0.001
        self.__fp.timeout = 6000

    def query(self, cmd):
        return self.__fp.query(cmd, delay=self.delay)

    def write(self, cmd):
        return self.__fp.write(cmd)

    # read (channel) (volt)
    def read_volt(self, channel):
        ch = int(channel)
        if ch in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            order = "R{0}\n".format(ch - 1)
        elif ch in [11, 12, 13, 14, 15, 16]:
            order = "R{0:c}\n".format(97 + ch - 11)
        else:
            return 0

        result = self.query(order)
        volt = float(result)  # type: ignore

        return volt



    # set (channel, value) (volt)
    def set_volt(self, channel, value):
        ch = int(channel)
        if ch in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            order = "S{0:d}{1:g}\n".format(ch - 1, value)
        elif ch in [11, 12, 13, 14, 15, 16]:
            order = "S{0:c}{1:g}\n".format(97 + ch - 11, value)

        a = self.query(order)
        return a

