
# Wire Protocol

## Name

This wire protocol shall be named `ProtoN`, standing for "protocol nimble" and pronounced *proton*.

## Representation Notes

### Numerical Representation Notes
- **0b...** denotes binary digit *(1 bit)*
- **0q...** denotes quaternary digit *(2 bits)*
- **0o...** denotes octal digit *(3 bits)*

### Byte Order
Network Byte Order (Big-Endian)

### Encodings
- int*n*: *n*-bit signed integer
- uint*n*: *n*-bit unsigned integer
- float64: IEEE 754 64-bit signed floating point number
- bool: 1-bit encoding of boolean values {0b0: `False`; 0b1: `True`}
- String: <len, UTF-8 encoded string>
- ShortStr: <uint3, UTF-8 encoded string>
- len: 16-bit unsigned integer

## OpCodes

### Primitives (Prim)

- **PrimNull**: *0o0*
- **PrimString**: *0o1* <String\>
- **PrimInt**: *0o2* <uint2, int8|int16|int32|int64\>
- **PrimFloat**: *0o3* <bool, String|float64\>
- **PrimBool**: *0o4* <bool\>

### Keys (Key)
- **ConPair**: *0o5* <String, Prim|Con>

### Containers (Con)
- **ConList**: *0o6* <len, {Prim|Con}\*>
- **ConObject**: *0o7* <len, {Key}\*>

## Notes

- Primitives must be held in some container and cannot stand on their own.
- `PrimInt`s are encoded as a 2-bit size value `sz` followed by a `2^(sz+3)`-bit integer.
- `PrimFloat`s are encoded as a bool b, followed by either (if b) a float64 or (if not b) a String representation of the float
- `ConPair`s OpCode is followed by a string (it's key) and then the OpCode of another Container or a Primitive (it's value)
- `ConList`s OpCode is followed by the number of 1st-level `Prim`|`Con` it contains and then the same number of subsequent Container or Primitive values
- `ConObject`s OpCode is followed by the number of 1st-level `Key` it contains and then the same number of subsequent Key values
- Each message starts with a version number and is immediately followed by exactly one Container
- Strings are immediately followed by the length of the UTF-8 encoded string in bytes, then followed by the encoded string itself

## Wire Buffer Structure

Order of contents on the wire:

1. Protocol version: `0q1`
3. Exactly one `Con`
