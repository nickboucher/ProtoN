#!/usr/bin/env python3
###
### wire_protoc.py
### A tool for testing the output of Google Protocol Buffers
###

from sys import argv, exit
import string_int_pb2

# Check arguments
if len(argv) != 3:
    exit("Invalid Number of Argument. Usage: " + argv[0] + " key value")

# Import ProtoBuf
msg = string_int_pb2.KeyStringInt()

# Supply example values
msg.key = argv[1]
msg.val = int(argv[2])

# Encode to bytestring and print
print(msg.SerializeToString())
