# ProtoN
**Protocol: Nimble**

*Nicholas Boucher		Aron Szanto*

## Introduction
We seek to develop a system that enables space-efficient wire protocol communication with trivial developer effort. This work is specifically targeted at web developers creating services that would traditionally use XML or JSON to serve data. Our system will be built by extending the Protocol Buffer model created by Google to automatically serialize arbitrary data into a bytestring comprising concatenated, appropriately-typed key-value pairs.

## Deliverables
For this project, we will produce a version of this system which enables space-efficient wire protocol communication between Python web servers and JavaScript clients. The deliverable components of this project will be:

Wire protocol specification enabling space-efficient transfer between machines
Python3 library which serializes arbitrary python objects into space-efficient buffers
JavaScript library which deserializes space-efficient buffers into JavaScript objects

## Theoretical Model
Google’s Protocol Buffer system allows data to be sent in a space-efficient serialized manner over websockets. However, a major barrier to using protocol buffers is having to design and compile a new protocol buffer for each version of the protocol, which is both time-intensive and error-prone. We seek to develop a system which is able to construct a complex protocol buffer for an arbitrary python object automatically by synthesizing a series of generic key-value protocol buffers implied by the object’s members.

In premise, we seek to create a communication protocol that understands data in a similar manner to NoSQL databases. A buffer is composed of a series of key-type-value triplets. Each triplet has a key of type string, an int denoting the primitive type of the value, and the value. This model seeks to provide the flexibility of XML or JSON in its extensibility while removing the need to transfer data as a UTF-8 encoded string. Additionally, this model seeks to leverage the space-efficient nature of typed buffers without necessitating the rigidity of Google’s Protocol Buffers.

## Implementation Details
This model is founded upon the premise of a key-type-value data store. Specifically, we propose that arbitrarily complex data can be encoded by grouping a collection of key-type-value data stores. We leverage this proposition by designing a protocol which “wraps” a given number of key-type-value data stores into an encoded bytes representation of a supplied programmatic object.

Keys will always be represented as a protocol-specified encoding of strings. Types will be represented numerically in a protocol-specified indexing system. A preliminary set of value types includes a protocol-specified encoding of int, string, char, float, and bool.

The system will implement the automatic encoding via module function call of Python objects, specifically by applying a protocol-specified restructuring and element-wise transformation of a supplied Python objects underlying __dict__.

### Example
We give an example encoding of the Python object alice, as specified below.

*Python Code*
```python
from protocol import protocol_encode

Class Person():
	def __init__(self, name, age, student):
		self.name = name
		self.age = age
		self.student = student

alice = Person(“Alice”, 21, True)
print(protocol_encode(alice))
```

*Bytestring Output, Visualized Conceptually*


Version, Length, Key, Type, Value, Key, Type, Value, Key, Type, Value
1, 3, “name”, 4 (string), “Alice”, “age”, 1 (int), 21, “student”, 2 (bool), 1
