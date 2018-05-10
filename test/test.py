#!/usr/bin/env python3
from sys import argv, exit
from os.path import isdir, join
from os import listdir
from subprocess import check_output
from json import load
from encoder import *
from decoder import *

def usage():
    """ Bad CLI options passed """
    print("Usage:", argv[0], "directory")
    exit()

def main():
    """ Main point of entry for CLI """
    # Check for correct arguments
    if len(argv) != 2 or not isdir(argv[1]):
        usage()
    dir = argv[1]
    succ = 0
    fail = 0
    for filename in listdir(dir):
        if filename.endswith(".json"):
            with open(join(dir,filename), 'r') as f:
                obj = load(f)
            # Do the PY testing
            print("Testing \u001b[1m" + filename + "\u001b[0m PY...", end="")
            if (obj == decode(encode(obj))):
                print("\u001b[1m\u001b[32mPASS\u001b[0m\u001b[0m");
                succ += 1
            else:
                print("\u001b[0m\u001b[1mFAIL\u001b[0m\u001b[0m")
                fail += 1
            # Get JS encoded bytes
            js = check_output(['./proton_test.js', join(dir,filename)]).decode('utf-8').rstrip()
            # Do the JS testing
            print("Testing \u001b[1m" + filename + "\u001b[0m JS...", end="")
            if js == 'FAIL':
                print("\u001b[0m\u001b[31mFAIL\u001b[0m\u001b[0m")
                print("Testing \u001b[1m" + filename + "\u001b[0m PY-JS...", end="")
                print("\u001b[0m\u001b[31mFAIL (SKIP)\u001b[0m\u001b[0m")
                fail += 2
            else:
                print("\u001b[1m\u001b[32mPASS\u001b[0m\u001b[0m");
                succ += 1
                print("Testing \u001b[1m" + filename + "\u001b[0m PY-JS...", end="")
                bin = bytes(list(map(int,js.split(','))))
                if obj == decode(bin):
                    print("\u001b[1m\u001b[32mPASS\u001b[0m\u001b[0m");
                    succ += 1
                else:
                    print("\u001b[0m\u001b[31mFAIL\u001b[0m\u001b[0m")
                    fail += 1

    print("\n" + ('-'*30))
    print("\n\u001b[33mPass:", succ, "\nFail:", fail, "\u001b[0m")
    print("\n" + ('-'*30))

if __name__ == '__main__':
    main()
