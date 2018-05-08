#!/usr/bin/env python3
from sys import argv, exit
from random import randint, choice, uniform, randrange
from string import ascii_letters, digits
from json import dump

# Maximum 64-bit signed int
max64 = 9223372036854775807

def random_string(size=0, chars=ascii_letters + digits):
    """ Generates a random key """
    if not size:
        size = randint(1,10)
    return ''.join(choice(chars) for _ in range(size))

def random_value():
    def rand_bool():
        # Random boolean value
        return choice([True, False])

    def rand_null():
        # Random null value
        return None

    def rand_int():
        # Random int value
        return randint(-1*max64, max64)

    def rand_float():
        # Random float value
        # Constants are arbitrary, but larger consants yield fewer precision
        # numbers after the decimal point
        return uniform(-999,999)

    def rand_string():
        # Random string value
        return random_string(size=randrange(50))

    def rand_list():
        # Random list value
        list = []
        size = randrange(5)
        for _ in range(size):
            list.append(random_value())
        return list

    def rand_object():
        # Return random object
        obj = {}
        size = randrange(5)
        for _ in range(size):
            obj[rand_string()] = random_value()
        return obj

    # Select a random type
    rand = choice([rand_bool, rand_null, rand_int, rand_float, rand_string, rand_list, rand_object])
    # Return the random value
    return rand()

def usage():
    print("Usage:", argv[0], "[--list, --object] file size")

def main():
    """ Main point of entry for CLI """
    if len(argv) != 4:
        usage()
        exit()
    # The number of elements to encode
    size = int(argv[3])
    if argv[1] == '--list':
        # Generate a JSON list example
        obj = []
        for _ in range(size):
            obj[random_string()] = random_value()
    elif argv[1] == '--object':
        # Generate a JSON object example
        obj = []
        for _ in range(size):
            obj.append(random_value())
    else:
        # Malformed options
        usage()
        exit()
    # Write the json output to file
    with open(argv[2], 'w') as f:
        dump(obj, f, indent=4)


if __name__ == '__main__':
    main()
