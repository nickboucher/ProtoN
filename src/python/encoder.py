#! /usr/env python

from constants import *
from struct import pack, unpack, calcsize
from collections import Mapping, Set, Sequence
from bitstring import BitStream, Bits

string_types = (str, bytes)
primitive_types = (int, str, float, type(None))

def pack_message(bytelist):
    bytelist.insert(0, BitStream(uint=PROTOCOL_VERSION, length=2))
    return Bits().join(bytelist)

def encode_variable(data):
    """Infers the type of data, then packs it into a network-order
    bytestring in accordance with the wire protocol. Data must be of type:
    int, str, float, boolean, None.
    @param data - the data to pack"""
    if data is None:
        return pack_type(TYPE_NULL)
    if isinstance(data, str):
        utf = data.encode('utf-8')
        utflen = len(utf)
        return pack_type(TYPE_STRING) + pack_len(utflen) + utf
    if isinstance(data, int):
        if abs(data) < (2**31 - 1):
            return pack_type(TYPE_INT) + pack_bool(False) + BitStream(int=data, length=32)

        else:
            return pack_type(TYPE_INT) + pack_bool(True) + BitStream(int=data, length=64)
    if isinstance(data, float):
        return pack_type(TYPE_FLOAT) + pack('d', TYPE_FLOAT, data)

    if isinstance(data, boolean):
        return pack_bool(boolean)

    else:
        raise TypeError("Wire protocol does not support this data type. \
        Expected: int, str, float, None. Got:", type(data))
def encode_object(obj, bytelist, memo=None):
    if memo is None:
        memo = set()

    if isinstance(obj, primitive_types):
        bytelist.append(encode_variable(obj))
    elif isinstance(obj, Mapping):
        if id(obj) not in memo:
            memo.add(id(obj))
        else:
            raise ValueError("ProtoN does not support circular references within objects")
        bytelist.extend([pack_type(TYPE_OBJECT), pack_len(len(obj.items()))])
        for key, value in obj.items():
            assert(isinstance(key, str))
            bytelist.append(pack_type(TYPE_PAIR))
            bytelist.append(encode_variable(key))
            encode_object(value, bytelist, memo)
        memo.remove(id(obj))
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        if id(obj) not in memo:
            memo.add(id(obj))
        else:
            raise ValueError("ProtoN does not support circular references within objects")
        bytelist.extend([pack_type(TYPE_LIST), pack_len(len(obj))])
        for elt in obj:
            encode_object(elt, bytelist, memo)
        memo.remove(id(obj))

    elif hasattr(obj, '__dict__'):
        encode_object(vars(obj), bytelist)
def pack_type(dtype):
    return BitStream(uint=dtype, length=3)
def pack_len(length):
    return BitStream(uint=length, length=16)
def pack_bool(boolean):
    return BitStream('0b1') if boolean else BitStream('0b0')
def encode(data):
    bytelist = []
    encode_object(data, bytelist)
    msg = pack_message(bytelist)
    return msg
