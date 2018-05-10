#!/usr/bin/env python3
from sys import argv, exit
from os.path import isdir, join
from random import randint, choice, uniform, randrange
from string import ascii_letters, digits
from json import dump

# Maximum object size for randomly generated objects
MAX_SIZE = 500
# Maximum absolute random float value
MAX_ABS_FLOAT = 999
# Maximum random string length
MAX_STRING_LEN = 50
# Max Object Key String length
MAX_KEY_LEN = 10
# Maximum non-root Object/Key random length
MAX_CHILD_SIZE = 5

# Maximum 52-bit signed int (js stores numbers as 64-bit floats, which only
# support up to a 52-bit integer value)
max64 = 2251799813685247

def random_string(size=0, chars=ascii_letters + digits):
    """ Generates a random key """
    if not size:
        size = randint(1,MAX_KEY_LEN)
    return ''.join(choice(chars) for _ in range(size))

def random_list(size=MAX_CHILD_SIZE):
    """ Return random list value """
    list = []
    members = randrange(size) if size else 0
    for _ in range(members):
        list.append(random_value())
    return list

def random_object(size=MAX_CHILD_SIZE):
    """ Return random object """
    obj = {}
    members = randrange(size) if size else 0
    for _ in range(members):
        obj[random_string()] = random_value()
    return obj

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
        return uniform(-1*MAX_ABS_FLOAT,MAX_ABS_FLOAT)

    def rand_string():
        # Random string value
        return random_string(size=randrange(MAX_STRING_LEN))


    # Select a random type
    rand = choice([rand_bool, rand_null, rand_int, rand_float, rand_string, random_list, random_object])
    # Return the random value
    return rand()

def write_json(object, filename):
    # Write the json output to file
    with open(filename, 'w') as f:
        dump(object, f, indent=4)

def usage():
    print("Usage:", argv[0], "[--list, --object] file size")
    print("      ", argv[0], "[--random] directory number")
    exit()

def main():
    """ Main point of entry for CLI """
    if len(argv) != 4:
        usage()
    # The number of elements to encode
    size = int(argv[3])
    if argv[1] == '--list':
        # Generate a JSON list example
        list = random_list(size)
        write_json(list, argv[2])
    elif argv[1] == '--object':
        # Generate a JSON object example
        obj = random_object(size)
        write_json(obj, argv[2])
    elif argv[1] == '--random':
        # Generate `number` random tests in `directory`
        # Test if dir passed is actually a directory
        if not isdir(argv[2]):
            usage()
        # Write `number` random JSON files
        for test_num in range(int(argv[3])):
            rand = choice([random_list, random_object])
            size = randrange(MAX_SIZE)
            obj = rand(size)
            filename = join(argv[2], "auto_generated_" + str(test_num+1) + ".json")
            write_json(obj, filename)
    else:
        # Malformed options
        usage()

if __name__ == '__main__':
    main()
