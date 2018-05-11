#! /usr/env python

from constants import *
from struct import pack, unpack, calcsize
from bitstring import Bits, BitStream
primitive_type_codes = set([TYPE_NULL, TYPE_BOOL, TYPE_INT, TYPE_STRING, TYPE_FLOAT])


def decode(payload):
    payload = BitStream(payload)
    version, payload = decode_version(payload)
    assert(version == PROTOCOL_VERSION)
    return decode_object(payload)[0]


def decode_version(payload):
    version, payload = payload.readlist(['uint:2, bits'])
    return version, payload


def decode_object(payload):
    assert(payload is not None)
    if len(payload) == 0:
        return
    dtype, payload = unpack_dtype(payload)
    # print('dtype:', dtype, 'payload:', payload[:8])

    if dtype in primitive_type_codes:
        return unpack_primitive(payload, dtype)
    elif dtype == TYPE_LIST:
        length, payload = unpack_len(payload)
        list_obj = []
        for _ in range(length):
            elt, payload = decode_object(payload)
            list_obj.append(elt)
        return list_obj, payload
    elif dtype == TYPE_OBJECT:
        length, payload = unpack_len(payload)
        dict_obj = {}
        for _ in range(length):
            key, value, payload = decode_pair(payload)
            dict_obj[key] = value
        return dict_obj, payload


def unpack_dtype(payload):
    """Reads the type of data stipulated at the head of a bytestring"""
    dtype, payload = payload.readlist(['uint:3, bits'])
#     print("unpacked dtype", dtype)
    return dtype, payload


def unpack_primitive(payload, dtype):
    """ Unpacks a primitive from the given payload and returns the remaining
        subsequent payload. Infers the type of data via the dtype at the beginning.
    @param {bytes} payload - the raw bytes of data to unpack as per the
        spec in wire_protocol.md
    """
    if dtype == TYPE_NULL:
        return unpack_null(payload)
    elif dtype == TYPE_STRING:
        return unpack_string(payload)
    elif dtype == TYPE_INT:
        return unpack_int(payload)
    elif dtype == TYPE_BOOL:
        return unpack_boolean(payload)
    elif dtype == TYPE_FLOAT:
        return unpack_float(payload)
    else:
        raise ValueError("Primitive dtype not recognized. Got:", dtype, ". Please\
        consult the specification for acceptable primitive type codes.")


def unpack_float(payload):
    """ Unpacks a float from the given payload and returns the remaining
        subsequent payload
    @param {bytes} payload - raw bytes at whose head is float data to
        unpack as per the spec in wire_protocol.md
    """
    is_float64, payload = unpack_boolean(payload)
    if is_float64:
        float_value, payload = payload.readlist(['float:64, bits'])
    else:
        float_str, payload = unpack_string(payload, short=True)
        float_value = float(float_str)
    return float_value, payload


def unpack_boolean(payload):
    """ Unpacks a boolean from the given payload and returns the remaining
        subsequent payload
    @param {bytes} payload - raw bytes at whose head is boolean data to
        unpack as per the spec in wire_protocol.md
    """

    boolean_value, payload = payload.readlist(['bool', 'bits'])
    return boolean_value, payload


def unpack_int(payload):
    """ Unpacks an int from the given payload and returns the remaining
        subsequent payload
    @param {bytes} payload - raw bytes at whose head is int data to
        unpack as per the spec in wire_protocol.md
    """
    # Calculate the size of the int
    sz, payload = payload.readlist(['uint:2', 'bits'])
    sz = 2**(sz + 3)
    int_fmt = 'int:' + str(sz)

    num, payload = payload.readlist([int_fmt, 'bits'])

    # Return the int and any remaining payload
    return num, payload


def unpack_null(payload):
    """Unpacks null from start of payload and returns None and the payload"""
    return None, payload


def unpack_string(payload, short=False):
    """Unpacks string and returns it along with the remaining payload"""
    length, payload = unpack_len(payload, short)
    # Slice the string and the remaining payload
    string, payload = payload[:length*8].tobytes(), payload[length*8:]
    # Return the decoded string and remianing bytes payload
    return string.decode('utf-8'), payload


def unpack_len(payload, short=False):
    """Unpacks a len-headed block of data, such as that which corresponds
    to a string, list, or dictionary."""

    # Calculate the size of the number representing the lenght of the str`
    # Slice the length of the string from the data and unpack it
    if short:
        length, payload = payload.readlist(['uint:3', 'bits'])
    else:
        sz, payload = payload.readlist(['uint:2', 'bits'])
        fmt_str = "uint:" + str(2**(sz+3))
        length, payload = payload.readlist([fmt_str, 'bits'])
    return length, payload


def decode_pair(payload):
    dtype, payload = unpack_dtype(payload)
#     print('dtype_pair:', dtype)
    assert(dtype == TYPE_PAIR)
    key, payload = unpack_string(payload)
    value, payload = decode_object(payload)
    return key, value, payload
