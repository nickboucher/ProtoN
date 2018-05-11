# Testing

Use this tool to test the ProtoN implementation. Note: In order to use this testing tool, you much have both Python3.x and Node.js installed on your system.

1. Either use the pre-generated tests in the *json/* directory or generate new tests using the process described below.
2. Run the test script, supplying the directory of the test JSON files:
```bash
./test.py json/
```

## Test Generation

To generate `n` new tests, run:

```bash
./test_generator.py directory n
```
Where directort is the directory you want to store the results, such as `json/`.

# Space Efficiency Testing

## General Efficiency

To test general efficiency, run the following command in the `/test/` directory:

```bash
./efficiency.py directory
```
Where directory is the directory containing the test files, such as `json/`.

This program tests the space-efficiency of all JSON files in the passed
directory, comparing ProtoN to whitespace-removed JSON.
It also outputs the results of the same test using GZip compression on the results.

*Note: GZip in this context is defined as an implementation of the [DEFLATE algorithm](https://www.ietf.org/rfc/rfc1950.txt)*


## Type Specific Efficiency

To test type-specific efficiency, run the following command in the `/test/` directory:

```bash
./type_efficiency.py
```
This generates a test json file containing 1000 randomly generated values of the same type.
The size ratio of ProtoN/JSON encoding is then compared.
Additionally, the same results are shown using GZip-ed results set to maximum space-efficient compression settings.

Note: you can also limit the program to specific test (run `./type_efficiency.py --help`)

## Credits

Credit to the following sources for JSON encoded test strings:

- https://json.org/JSON_checker/
- https://github.com/Julian/jsonschema
