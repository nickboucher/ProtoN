
# Wire Protocol

## Proposed Name

Nicholas proposes naming the project `ProtoN`, standing for "protocol nimble" and pronounced *proton*.

## Representation Notes

### Numerical Representation Notes
- **0b...** denotes binary digit *(1 bit)*
- **0q...** denotes quaternary digit *(2 bits)*
- **0o...** denotes octal digit *(3 bits)*

### Byte Order
Network Byte Order (Big-Endian)

### Encodings
- int: 64-bit signed integer
- float: IEEE 754 64-bit signed floating point number
- logical: 2-bit encoding of special logical values {0q0: `False`; 0q1: `True`; 0q2: `null`; 0q3: "Error State"}
- len: unsigned 32-bit integer
- String: <len, UTF-8 encoded string>

## OpCodes

### Primitives (Prim)

- **PrimString**: *0q0* <String\>
- **PrimInt**: *0q1* <int\>
- **PrimFloat**: *0q2* <float\>
- **PrimLogical**: *0q3* <logical\>

### Containers (Con)

- **ConPair**: *0b0* <String, Prim|Con>
- **ConList**: *0b1* <String, len, {Prim|Con}\*>

## Notes

- Primitives must be held in some container and cannot stand on their own.
- `ConPair`'s OpCode is followed by a string (it's key) and then the OpCode of another Container or a Primitive (it's value)
- `ConList`'s OpCode is followed by a string (it's key) and then the number of 1st-level `Prim`|`Con` it contains and then the same number of subsequent Container or Primitive values
- "Dictionaries" are represented as `ConList`s containing one or more `ConPair`s
- Each message starts with a version number and is immediately followed by exactly one Container

## Wire Buffer Structure

Order of contents on the wire:

1. Protocol version: `0q1`
2. Number of 1st level (oldest ancestor) containers: *len* `n`
3. `n` number of `Con`