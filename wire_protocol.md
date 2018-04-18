
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
- int64: 64-bit signed integer
- float64: IEEE 754 64-bit signed floating point number
- int32: 32-bit signed integer
- float32: IEEE 754 32-bit signed floating point number
- bool: 1-bit encoding of boolean values {0b0: `False`; 0b1: `True`}
- len: unsigned 16-bit integer
- String: <len, UTF-8 encoded string>

## OpCodes

### Primitives (Prim)

- **PrimNull**: *0o0*
- **PrimString**: *0o1* <String\>
- **PrimInt**: *0o2* <bool, int32|int64\>
- **PrimFloat**: *0o3* <bool, float32|float64\>
- **PrimBool**: *0o4* <bool\>

### Keys (Key)
- **ConPair**: *0o5* <String, Prim|Con>

### Containers (Con)
- **ConList**: *0o6* <len, {Prim|Con}\*>
- **ConObject**: *0o7* <len, {Key}\*>

## Notes

- Primitives must be held in some container and cannot stand on their own.
- `PrimInt`'s and `PrimFloat`'s are both immediately followed by a bool which is True if the subsequent number is 64-bits in length and False if the subsequent number is 32-bits in length
- `ConPair`'s OpCode is followed by a string (it's key) and then the OpCode of another Container or a Primitive (it's value)
- `ConList`'s OpCode is followed by the number of 1st-level `Prim`|`Con` it contains and then the same number of subsequent Container or Primitive values
- `ConObject`s OpCode is followed by the number of 1st-level `Key` it contains and then the same number of subsequent Key values
- Each message starts with a version number and is immediately followed by exactly one Container

## Wire Buffer Structure

Order of contents on the wire:

1. Protocol version: `0q1`
3. Exactly one `Con`
