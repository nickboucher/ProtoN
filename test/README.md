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
./test_generator.py json n
```

## Credits

Credit to the following sources for JSON encoded test strings:

- https://json.org/JSON_checker/
- https://github.com/Julian/jsonschema
