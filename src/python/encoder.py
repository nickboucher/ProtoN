#! /usr/env python

from constants import *
import struct


class Encoder:
    def __init__():
        self.blist = [pack('!B', PROTOCOL_VERSION)]

    def clear():
        self.blist = [pack('!B', PROTOCOL_VERSION)]

    def pack_message():
        return b''.join(self.blist)

    def encode_variable(data):
        if data is None:
            return pack('!B', TYPE_NULL)
        if isinstance(data, str):
            utf = data.encode('utf-8')
            utflen = len(utf)
            return pack('!Bh', TYPE_STRING, utflen) + utf
        if isinstance(data, int):
            if (2**31 + 1) < data < (2**31 - 1):
                return pack('!B?i', TYPE_INT, False, data)
            else:
                return pack('!B?q', TYPE_INT, True, data)
        if isinstance(data, float):
            return pack('!Bd', TYPE_FLOAT, data)
