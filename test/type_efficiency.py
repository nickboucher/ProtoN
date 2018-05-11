#!/usr/bin/env python3
from sys import argv, exit
from json import load, dumps
from random import random, randint
from zlib import compress
from encoder import *
from decoder import *
from test_generator import *

# The number of items in the constructed object to test
TEST_SIZE = 1000

def usage():
    """ Bad CLI options passed """
    print("Usage:", argv[0], "[--list, --object] [--null, --string, --int, --float, --bool, --list, --object, '--smallFloat']")
    exit()

def main():
    """ Main point of entry for CLI """
    # Check for correct arguments
    if len(argv) == 3:
        containers = [argv[1]]
        values = [argv[2]]
    elif len(argv) == 1:
        # If container and value types weren't specified, process all combinations
        containers = ['--list', '--object']
        values = ['--null', '--string', '--int', '--float', '--bool', '--list', '--object', '--smallFloat']
    else:
        usage()
    # Loop through all specified combinations
    for value in values:
        for container in containers:
            # Set the object type and append methods
            if container == '--list':
                obj = []
                add = lambda x, y: x.append(y)
            if container == '--object':
                obj = {}
                add = lambda x, y: x.update({random_string():y})
            # Set the random member generation function from flags
            if value == '--null':
                rand = rand_null
            elif value == '--string':
                rand = rand_string
            elif value == '--int':
                rand = rand_int
            elif value == '--float':
                rand = rand_float
            elif value == '--bool':
                rand = rand_bool
            elif value == '--list':
                rand = lambda: []
            elif value == '--object':
                rand = lambda: {}
            elif value == '--smallFloat':
                rand = lambda: round(random(),randint(1,7))
            else:
                usage()
            # Generate the test object
            for _ in range(TEST_SIZE):
                add(obj, rand())
            # JSON size without added whitespace
            json_sz = len(dumps(obj, separators=(',',':')).encode('utf-8'))
            # ProtoN size
            proton_sz = len(encode(obj))
            ratio = proton_sz/json_sz
            # Print Uncompressed Results
            print("\u001b[1m" + container.replace('-','').title() +
                    "(" + value.replace('-','').title() + ")" +
                    "\u001b[0m \u001b[33mProtoN/JSON Size:\u001b[0m",
                    "\u001b[31m" if ratio > 1 else "\u001b[32m",
                    ratio, "\u001b[0m")
            # Add compressed results
            comp_json_sz = len(compress(dumps(obj, separators=(',',':')).encode('utf-8'), level=9))
            comp_proton_sz =len(compress(encode(obj), level=9))
            comp_ratio = comp_proton_sz/comp_json_sz
            # Print Compressed Results
            print("\u001b[1m" + container.replace('-','').title() +
                    "(" + value.replace('-','').title() + ") Gzip" +
                    "\u001b[0m \u001b[33mProtoN/JSON Size:\u001b[0m",
                    "\u001b[31m" if comp_ratio > 1 else "\u001b[32m",
                    comp_ratio, "\u001b[0m")

if __name__ == '__main__':
    main()
