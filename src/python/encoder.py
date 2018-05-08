#! /usr/env python

from constants import *
from struct import pack, unpack, calcsize
from collections import Mapping, Set, Sequence
from bitstring import BitStream, Bits

string_types = (str, bytes)
primitive_types = (int, str, float, bool, type(None))


def pack_message(bytelist):
    bytelist.insert(0, BitStream(uint=PROTOCOL_VERSION, length=2))

    return Bits().join(bytelist).tobytes()


def encode_key(data):
    utf = data.encode('utf-8')
    utflen = len(utf)
    return pack_len(utflen) + utf


def encode_variable(data):
    """Infers the type of data, then packs it into a network-order
    bytestring in accordance with the wire protocol. Data must be of type:
    int, str, float, boolean, None.
    @param data - the data to pack"""
    if data is None:
        #         print('packing null')
        return pack_type(TYPE_NULL)
    elif isinstance(data, bool):
        #         print('packing bool')
        return pack_type(TYPE_BOOL) + pack_bool(data)
    elif isinstance(data, str):
        #         print('packing string')
        utf = data.encode('utf-8')
        utflen = len(utf)
        return pack_type(TYPE_STRING) + pack_len(utflen) + utf
    elif isinstance(data, int):
        #         print('packing int')
        if abs(data) < (2**7 - 1):
            return pack_type(TYPE_INT) + BitStream(uint=0, length=2) + BitStream(int=data, length=8)
        if abs(data) < (2**15 - 1):
            return pack_type(TYPE_INT) + BitStream(uint=1, length=2) + BitStream(int=data, length=16)
        if abs(data) < (2**31 - 1):
            return pack_type(TYPE_INT) + BitStream(uint=2, length=2) + BitStream(int=data, length=32)
        if abs(data) < (2**63 - 1):
            return pack_type(TYPE_INT) + BitStream(uint=3, length=2) + BitStream(int=data, length=64)
        else:
            raise ValueError("int values outside +/- 2**63 are not supported.")
    elif isinstance(data, float):
        if len(str(data)) < 8:
            utf = data.encode('utf-8')
            utflen = len(utf)
            assert(utflen < 8)
            return pack_type(TYPE_FLOAT) + pack_bool(False) + pack_len(utflen, short=True) + utf
        else:
            return pack_type(TYPE_FLOAT) + pack_bool(True) + BitStream(float=data, length=64)

    else:
        raise TypeError("Wire protocol does not support this data type. \
        Expected: int, str, float, None. Got:", type(data))


def encode_object(obj, bytelist, memo=None):
    if memo is None:
        memo = set()

    if isinstance(obj, primitive_types):
        encoding = encode_variable(obj)
        bytelist.append(encoding)
    elif isinstance(obj, Mapping):
        if id(obj) not in memo:
            memo.add(id(obj))
        else:
            raise ValueError(
                "ProtoN does not support circular references within objects")
        bytelist.extend([pack_type(TYPE_OBJECT), pack_len(len(obj.items()))])
        for key, value in obj.items():
            assert(isinstance(key, str))
            bytelist.append(pack_type(TYPE_PAIR))
            bytelist.append(encode_key(key))
            encode_object(value, bytelist, memo)
        memo.remove(id(obj))
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        if id(obj) not in memo:
            memo.add(id(obj))
        else:
            raise ValueError(
                "ProtoN does not support circular references within objects")
        bytelist.extend([pack_type(TYPE_LIST), pack_len(len(obj))])
        for elt in obj:
            encode_object(elt, bytelist, memo)
        memo.remove(id(obj))

    elif hasattr(obj, '__dict__'):
        encode_object(vars(obj), bytelist)


def pack_type(dtype):
    return BitStream(uint=dtype, length=3)


def pack_len(length, short=False):
    sz = 16 if not short else 3
    return BitStream(uint=length, length=sz)


def pack_bool(boolean):
    return BitStream(uint=1, length=1) if boolean else BitStream(uint=0, length=1)


def encode(data):
    bytelist = []
    encode_object(data, bytelist)
    msg = pack_message(bytelist)
    return msg
