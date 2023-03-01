# -*- coding: utf-8 -*-
"""
__date:         2018/08/25
__author:       Miracle Shih
__corporation:  OriginQuantum
__usage:
"""
import time

import pyvisa, pyvisa.constants
from .resources import resource_manager

class SR830:

    def __init__(self, visa_address):
        self.__fp:pyvisa.resources.MessageBasedResource = resource_manager.open_resource(visa_address, access_mode=pyvisa.constants.AccessModes.exclusive_lock)
        self.current_input = 1      # 0 for I,1 for V;
        self.current_input = self.check_input_mode()
        self.__fp.timeout = 5000
        self.__fp.open()

        return


    def write(self, cmd):
        self.__fp.write(cmd)

    def query(self, cmd):
        return self.__fp.query(cmd)
    

    def AuxOut(self, port, value):
        order = str('AUXV? %d' %port)
        value_now = eval(self.query(order))
        while abs(value_now - value) > 0.02:
            if value_now < value:
                value_now = value_now + 0.01
                order = str('AUXV%d, %f' %(port, value_now))
                time.sleep(0.1)
            else:
                value_now = value_now - 0.01
                order = str('AUXV%d, %f' % (port, value_now))
                time.sleep(0.1)
            self.write(str(order))
        self.write(str('AUXV%d, %f' % (port, value)))

    def getCH(self, CH):
        data_str = self.query('OUTP? '+str(CH))
        data = eval(data_str)
        return data

    def get(self):
        data_str1 = self.query('OUTP? 1')
        data_str2 = self.query('OUTP? 2')
        CH1 = eval(data_str1)
        CH2 = eval(data_str2)
        return [CH1, CH2]



    def read_current(self, type_):      # X:1 Y:2 R:3 Theta:4
        # 测量信号
        success_flag = 0
        while success_flag == 0:
            try:
                I_read = self.query("OUTP ? {0:d}\n".format(type_))
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.read_current, line 71".format(e))
                    time.sleep(2)

        return float(I_read)



    def read_aux(self, channel):
        # AUX read
        success_flag = 0
        while success_flag == 0:
            try:
                V_read = self.query("AUXV? {0}\n".format(int(channel)))
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.read_aux, line 92".format(e))
                    time.sleep(2)

        return float(V_read)



    def write_aux(self, channel, value):
        # AUX set
        command = "AUXV {0},{1}\n".format(int(channel), value)
        success_flag = 0
        while success_flag == 0:
            try:
                self.write(command)
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.write_aux, line 114".format(e))
                    time.sleep(2)

        return



    def init_aux(self, channel, value, step, delay):
        # AUX 逐步
        channel = int(channel)
        current_value = self.read_aux(channel)
        abs_step = abs(step)
        if current_value > value:
            while current_value - value > abs_step:
                current_value -= abs_step
                self.write_aux(channel, current_value)
                time.sleep(delay)
        else:
            while value - current_value > abs_step:
                current_value += abs_step
                self.query(channel, current_value)
                time.sleep(delay)

        self.write_aux(channel, value)

        return



    def read_freq(self):
        # freqency read
        success_flag = 0
        while success_flag == 0:
            try:
                freq = self.query("FREQ?\n")
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.read_freq, line 157".format(e))
                    time.sleep(2)

        return float(freq)



    def write_freq(self, freq):
        # frequency set
        command = "FREQ {0}\n".format(freq)
        success_flag = 0
        while success_flag == 0:
            try:
                self.write(command)
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.write_freq, line 179".format(e))
                    time.sleep(2)

        return



    def read_amp(self):
        # AMP(输入电压)read
        success_flag = 0
        while success_flag == 0:
            try:
                amp = self.query("SLVL?\n")
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.read_amp, line 200".format(e))
                    time.sleep(2)

        return float(amp)



    def write_amp(self, amp):
        # AMP write
        command = "SLVL {0}\n".format(amp)
        success_flag = 0
        while success_flag == 0:
            try:
                self.write(command)
                success_flag = 1
            except Exception as e:
                if e == "instrument:fprintf:opfailed":
                    success_flag = 0
                    print("{0} : {1}".format(time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), e))
                    time.sleep(2)
                else:
                    # raise Exception("{0}".format(e))
                    print("{0} in SR830.write_amp, line 222".format(e))
                    time.sleep(2)

        return



    def check_output_overload(self):
        status = self.query("LIAS? 2\n")

        return float(status)



    def read_sens(self):
        # sens
        sens = self.query("SENS?\n")

        return float(sens)



    def write_sens(self, sens):
        # sens
        self.write("SENS {0}\n".format(sens))

        return



    def check_input_mode(self):
        r = self.query("ISRC?")
        r = float(r)
        if r == 1 or r == 0:
            mode = 1
        else:
            mode = 0

        return mode



    def set_input_mode(self, mode):
        self.query("ISRC {0}".format(mode))

        return



    def snapRtheta(self):
        r = self.query("SNAP?3,4\n")
        p = r.split(",")

        return float(p[0])