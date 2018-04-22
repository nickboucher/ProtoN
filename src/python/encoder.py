#! /usr/env python

from constants import *
from struct import pack, unpack, calcsize
from collections import Mapping, Set, Sequence

string_types = (str, bytes)
primitive_types = (int, str, float, type(None))

def pack_message(bytelist):
    bytelist.insert(0, pack('!B', PROTOCOL_VERSION))
    return b''.join(bytelist)

def encode_variable(data):
    """Infers the type of data, then packs it into a network-order
    bytestring in accordance with the wire protocol. Data must be of type:
    int, str, float, boolean, None.
    @param data - the data to pack"""
    if data is None:
        return pack('!B', TYPE_NULL)
    if isinstance(data, str):
        utf = data.encode('utf-8')
        utflen = len(utf)
        return pack('!Bh', TYPE_STRING, utflen) + utf
    if isinstance(data, int):
        if abs(data) < (2**31 - 1):
            return pack('!B?i', TYPE_INT, False, data)
        else:
            return pack('!B?q', TYPE_INT, True, data)
    if isinstance(data, float):
        return pack('!Bd', TYPE_FLOAT, data)

    if isinstance(data, boolean):
        return pack('!B?', TYPE_BOOL, data)

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

        bytelist.append(pack("!Bh", TYPE_OBJECT, len(obj.items())))

        for key, value in obj.items():
            assert(isinstance(key, str))
            bytelist.append(pack("!B", TYPE_PAIR))
            bytelist.append(encode_variable(key))
            encode_object(value, bytelist, memo)
        memo.remove(id(obj))
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        if id(obj) not in memo:
            memo.add(id(obj))
        else:
            raise ValueError("ProtoN does not support circular references within objects")

        bytelist.append(pack("!Bh", TYPE_LIST, len(obj)))

        for elt in obj:
            encode_object(elt, bytelist, memo)
        memo.remove(id(obj))

    elif hasattr(obj, '__dict__'):
        encode_object(vars(obj), bytelist)

def encode(data):
    bytelist = []
    encode_object(data, bytelist)
    msg = pack_message(bytelist)
    return msg
