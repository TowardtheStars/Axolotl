# -*- coding: utf-8 -*-

# This code is part of pyQCat.
#
# Copyright (c) 2017-2021 Origin Quantum Computing. All Right Reserved.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# @Time   : 2021/6/25 14:51
# @Author : ZA
import struct
from socket import AF_INET, SOCK_STREAM, socket


class TcpClient(object):
    def __init__(self, ip, port, family=AF_INET, typ=SOCK_STREAM):
        self.ip = ip
        self.port = port
        self.family = family
        self.typ = typ
        self.measure_data = None
        self._sock = None
        self._connect()

    def _connect(self):
        self._sock = socket(self.family, self.typ)
        self._sock.connect((self.ip, self.port))

    def close(self):
        self._sock.close()

    @staticmethod
    def send_data(sock: socket, data):
        if not isinstance(data, bytes):
            data = bytes(data, 'utf-8')  # 转换字节格式
        sock.sendall(data)  # 发送数据

    @staticmethod
    def rec_data(sock: socket, rec_len=1024):
        rec_data = sock.recv(rec_len)
        return rec_data

    def connect_config(self, send_data, rec_flag=0):
        rec_data = None
        self.send_data(self._sock, send_data)
        if rec_flag == 1:
            rec_data = self.rec_data(self._sock)
        return rec_data


HEAD = 0X55
END = 0XAA


class Qdc:
    def __init__(self, ip_list, port=8080):
        self.tcp_client = list()
        for ip in ip_list:
            self.tcp_client.append(TcpClient(ip, port))

    def output_on(self, channel):
        tcp_client, channel = self.get_channel_sock(channel)
        dc_output = DcOutput()
        dc_output.work_type = 1
        dc_output.channel_code = channel
        protocol = dc_output.get_protocol()
        ver = verify(protocol)
        dc_output.verify = ver
        protocol = dc_output.get_protocol()
        # for i in range(len(protocol)):
        #     print('%d = %02X' % (i, protocol[i]))
        recv = tcp_client.connect_config(protocol, 1)
        recv_data = DcRec()
        recv_data.copy(recv)
        recv_data.verify()

    def output_off(self, channel):
        tcp_client, channel = self.get_channel_sock(channel)
        dc_output = DcOutput()
        dc_output.work_type = 2
        dc_output.channel_code = channel
        protocol = dc_output.get_protocol()
        ver = verify(protocol)
        dc_output.verify = ver
        protocol = dc_output.get_protocol()
        # for i in range(len(protocol)):
        #     print('%d = %02X' % (i, protocol[i]))
        recv = tcp_client.connect_config(protocol, 1)
        recv_data = DcRec()
        recv_data.copy(recv)
        recv_data.verify()

    def set_dc(self, channel, vol):
        tcp_client, channel = self.get_channel_sock(channel)
        assert -10 <= vol <= 10
        dc_set = DcSet()
        dc_set.channel = channel
        vol_code = ADC(vol)
        dc_set.dc_code = vol_code
        protocol = dc_set.get_protocol()
        ver = verify(protocol)
        dc_set.verify = ver
        protocol = dc_set.get_protocol()
        # for i in range(len(protocol)):
        #     print('%d = %02X' % (i, protocol[i]))
        recv = tcp_client.connect_config(protocol, 1)
        recv_data = DcRec()
        recv_data.copy(recv)
        recv_data.verify()

    def query_dc(self, channel):
        tcp_client, channel = self.get_channel_sock(channel)
        query_dc = DcQuery()
        query_dc.channel = channel
        protocol = query_dc.get_protocol()
        ver = verify(protocol)
        query_dc.verify = ver
        protocol = query_dc.get_protocol()
        # for i in range(len(protocol)):
        #     print('%d = %02X' % (i, protocol[i]))
        recv = tcp_client.connect_config(protocol, 1)
        recv_data = DcRec()
        recv_data.copy(recv)
        recv_data.verify()
        dc = DAC(recv_data.dc_code)
        return dc

    def get_channel_sock(self, channel):
        channel -= 1
        device_id = int(round(channel//8))
        channel = channel % 8 + 1
        return self.tcp_client[device_id], channel

    def test(self):
        print("This is test function")

    def close(self):
        for client in self.tcp_client:
            client.close()

    def open(self):
        pass
        


class Head:
    def __init__(self):
        self._head = struct.pack('B', 0x55)
        self._device_id = struct.pack('B', 0x00)
        self._type = struct.pack('B', 0x00)

    def get_protocol(self):
        protocol = [self._head, self._device_id, self._type]
        return protocol

    def copy(self, recv_data):
        self._head = struct.unpack('B', recv_data[0:1])[0]
        self._device_id = struct.unpack('B', recv_data[1:2])[0]
        self._type = struct.unpack('B', recv_data[2:3])[0]

    @property
    def head(self):
        return self._head

    @property
    def device_id(self):
        return self._device_id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        type_list = [0x11, 0x21, 0x51, 0x53]
        assert (value in type_list)
        self._type = struct.pack('B', value)


class End:
    def __init__(self):
        self._verify = struct.pack('B', 0x00)
        self._end = struct.pack('B', 0xAA)

    def get_protocol(self):
        protocol = [self._verify, self._end]
        return protocol

    def copy(self, recv_data):
        self._verify = struct.unpack('B', recv_data[0:1])[0]
        self._end = struct.unpack('B', recv_data[1:2])[0]

    @property
    def end(self):
        return self._end

    @property
    def verify(self):
        return self._verify

    @verify.setter
    def verify(self, value):
        self._verify = struct.pack('B', value)


class DcSet:
    def __init__(self):
        self._head = Head()
        self._channel = struct.pack('B', 0x00)
        self._dc_code = struct.pack('>I', 0x01)
        self._reserved = struct.pack('B' * 6, *([0x00] * 6))
        self._head.type = 0x11
        self._end = End()

    def get_protocol(self):
        protocol = self._head.get_protocol()
        protocol.extend([self._channel, self._dc_code, self._reserved])
        protocol.extend(self._end.get_protocol())
        return b''.join(protocol)

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        assert 1 <= value <= 8
        self._channel = struct.pack('B', value)

    @property
    def dc_code(self):
        return self._dc_code

    @dc_code.setter
    def dc_code(self, value):
        self._dc_code = struct.pack('>I', value)

    @property
    def verify(self):
        return self._end.verify

    @verify.setter
    def verify(self, value):
        self._end.verify = value


class DcOutput:
    def __init__(self):
        self._head = Head()
        self._channel_code = struct.pack('B', 0x00)
        self._work_type = struct.pack('B', 0x00)
        self._reserved = struct.pack('B' * 9, *[0x00] * 9)
        self._head.type = 0x21
        self._end = End()

    def get_protocol(self):
        protocol = self._head.get_protocol()
        protocol.extend([self._channel_code, self._work_type, self._reserved])
        protocol.extend(self._end.get_protocol())
        return b''.join(protocol)

    @property
    def channel_code(self):
        return self._channel_code

    @channel_code.setter
    def channel_code(self, value):
        assert 1 <= value <= 8
        work_type, = struct.unpack('B', self._work_type)
        channel_c = 0X01
        channel_c = channel_c << (value - 1)
        if work_type == 1:
            pass
        elif work_type == 2:
            channel_c ^= 0xFF
        else:
            raise Exception("Please set the work type of the dc")
        channel_c &= 0xFF
        self._channel_code = struct.pack('B', channel_c)

    @property
    def work_type(self):
        return self._work_type

    @work_type.setter
    def work_type(self, value):
        self._work_type = struct.pack('B', value)

    @property
    def verify(self):
        return self._end.verify

    @verify.setter
    def verify(self, value):
        self._end.verify = value


class DcQuery:
    def __init__(self):
        self._head = Head()
        self._channel = struct.pack('B', 0x00)
        self._reserved = struct.pack('B' * 10, *[0x00] * 10)
        self._head.type = 0x51
        self._end = End()

    def get_protocol(self):
        protocol = self._head.get_protocol()
        protocol.extend([self._channel, self._reserved])
        protocol.extend(self._end.get_protocol())
        return b''.join(protocol)

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        assert 1 <= value <= 8
        self._channel = struct.pack('B', value)

    @property
    def verify(self):
        return self._end.verify

    @verify.setter
    def verify(self, value):
        self._end.verify = value


class DcRec:
    def __init__(self):
        self._head = Head()
        self._result = None
        self._error_code = None
        self._reserved = None
        self._dc_code = None
        self._end = End()

    @property
    def dc_code(self):
        return self._dc_code

    def copy(self, rec_data):
        self._head.copy(rec_data[0:3])
        self._result = struct.unpack('B', rec_data[3:4])[0]
        self._error_code = struct.unpack('B', rec_data[4:5])[0]
        if self._head.type == 0X51:
            self._dc_code = struct.unpack('I', rec_data[5:9])[0]
            # print("%08x" % self._dc_code)
            # self._dc_code &= 0XFFFFFF
            # print("%08x" % self._dc_code)
            # self._dc_code >>= 8
            # print("%06x" % self._dc_code)
        self._end.copy(rec_data[14:16])

    def verify(self):
        head = self._head.head
        end = self._end.end
        if head != HEAD:
            raise Exception("Received tcp data head is not right! %02X != %02X" % (head, HEAD))
        if end != END:
            raise Exception("Received tcp data end is not right! %02X != %02X" % (end, END))
        if self._result != 0X11:
            if self._error_code == 0X01:
                raise Exception("Received tcp param error")
            elif self._error_code == 0X02:
                raise Exception("Received tcp verify error")


def ADC(value):
    vol_code = round((value + 10) * (pow(2, 20) - 1) / 20)
    return int(vol_code)


def DAC(value):
    vol = value * 20 / (pow(2, 20) - 1) - 10
    return vol


def verify(protocol):
    value, = struct.unpack('B', protocol[1:2])
    for i in range(2, len(protocol) - 1):
        a, = struct.unpack('B', protocol[i:i + 1])
        value ^= a
    return value


