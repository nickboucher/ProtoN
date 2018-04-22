#! /usr/env python

from constants import *
from struct import pack, unpack, calcsize


primitive_type_codes = set([TYPE_NULL, TYPE_BOOL, TYPE_INT, TYPE_STRING, TYPE_FLOAT])


def decode(payload):
    assert(isinstance(payload, bytes))

    version, payload = decode_version(payload)
    assert(version == PROTOCOL_VERSION)
    return decode_object(payload)[0]


def decode_version(payload):
    version_sz = calcsize('!B')
    version_bin, payload = payload[:version_sz], payload[version_sz:]
    (version,) = unpack('!B', version_bin)
    return version, payload


def decode_object(payload):
    assert(payload is not None)
    assert(len(payload) > 0)
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
    dtype_sz = calcsize('!B')
    dtype_bin, payload = payload[:dtype_sz], payload[dtype_sz:]
    (dtype,) = unpack('!B', dtype_bin)
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
    float_sz = calcsize('!d')
    float_bin, payload = payload[:float_sz], payload[float_sz:]
    float_value = unpack('!d', float_bin)
    return float_value, payload


def unpack_boolean(payload):
    """ Unpacks a boolean from the given payload and returns the remaining
        subsequent payload
    @param {bytes} payload - raw bytes at whose head is boolean data to
        unpack as per the spec in wire_protocol.md
    """

    boolean_sz = calcsize('!?')
    boolean_bin, payload = payload[:boolean_sz], payload[boolean_sz:]
    boolean_value = unpack('!?', boolean_bin)
    return boolean_value, payload


def unpack_int(payload):
    """ Unpacks an int from the given payload and returns the remaining
        subsequent payload
    @param {bytes} payload - raw bytes at whose head is int data to
        unpack as per the spec in wire_protocol.md
    """
    # Calculate the size of the int
    int_64_flag_sz = calcsize('!?')
    int_64_flag_bin, payload = payload[
        :int_64_flag_sz], payload[int_64_flag_sz:]
    (int_64_flag,) = unpack('!?', int_64_flag_bin)
    int_unpack_fmt = "!q" if int_64_flag else "!i"

    int_sz = calcsize(int_unpack_fmt)
    # Separate the int from any remaining payload
    num_bin, payload = payload[:int_sz], payload[int_sz:]
    # Convert the binary data
    (num,) = unpack(int_unpack_fmt, num_bin)
    # Return the int and any remaining payload
    return num, payload


def unpack_null(payload):
    """Unpacks null from start of payload and returns None and the payload"""
    return None, payload


def unpack_string(payload):
    """Unpacks string and returns it along with the remaining payload"""
    length, payload = unpack_len(payload)
    # Slice the string and the remaining payload
    string, payload = payload[:length], payload[length:]
    # Return the decoded string and remianing bytes payload
    return string.decode('utf-8'), payload


def unpack_len(payload):
    """Unpacks a len-headed block of data, such as that which corresponds
    to a string, list, or dictionary."""

    # Calculate the size of the number representing the lenght of the str`
    len_sz = calcsize('!h')
    # Slice the length of the string from the data and unpack it
    len_bin, payload = payload[:len_sz], payload[len_sz:]
    (length,) = unpack('!h', len_bin)
    return length, payload


def decode_pair(payload):
    dtype, payload = unpack_dtype(payload)
    assert(dtype == TYPE_PAIR)

    dtype, payload = unpack_dtype(payload)
    assert(dtype == TYPE_STRING)
    key, payload = unpack_string(payload)

    value, payload = decode_object(payload)
    return key, value, payload

bstring = b'\x01\x07\x00\x05\x05\x01\x00\x01s\x01\x00\x05hello\x05\x01\x00\x01l\x06\x00\x04\x02\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x03\x05\x01\x00\x01d\x07\x00\x01\x05\x01\x00\x03key\x01\x00\x05value\x05\x01\x00\x01x\x02\x00\x00\x00\x00\x00\x05\x01\x00\x01D\x07\x00\x05\x05\x01\x00\x01s\x01\x00\x05hello\x05\x01\x00\x01l\x06\x00\x04\x02\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x03\x05\x01\x00\x01d\x07\x00\x01\x05\x01\x00\x03key\x01\x00\x05value\x05\x01\x00\x01x\x02\x00\x00\x00\x00\x00\x05\x01\x00\x01D\x07\x00\x05\x05\x01\x00\x01s\x01\x00\x05hello\x05\x01\x00\x01l\x06\x00\x04\x02\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x03\x05\x01\x00\x01d\x07\x00\x01\x05\x01\x00\x03key\x01\x00\x05value\x05\x01\x00\x01x\x02\x00\x00\x00\x00\x00\x05\x01\x00\x01D\x07\x00\x05\x05\x01\x00\x01s\x01\x00\x05hello\x05\x01\x00\x01l\x06\x00\x04\x02\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x03\x05\x01\x00\x01d\x07\x00\x01\x05\x01\x00\x03key\x01\x00\x05value\x05\x01\x00\x01x\x02\x00\x00\x00\x00\x00\x05\x01\x00\x01D\x07\x00\x05\x05\x01\x00\x01s\x01\x00\x05hello\x05\x01\x00\x01l\x06\x00\x04\x02\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x03\x05\x01\x00\x01d\x07\x00\x01\x05\x01\x00\x03key\x01\x00\x05value\x05\x01\x00\x01x\x02\x00\x00\x00\x00\x00\x05\x01\x00\x01D\x07\x00\x04\x05\x01\x00\x01s\x01\x00\x05hello\x05\x01\x00\x01l\x06\x00\x04\x02\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x02\x00\x00\x00\x00\x03\x05\x01\x00\x01d\x07\x00\x01\x05\x01\x00\x03key\x01\x00\x05value\x05\x01\x00\x01x\x02\x00\x00\x00\x00\x00'
import pprint
pprint.pprint(decode(bstring))
