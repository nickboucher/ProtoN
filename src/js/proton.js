/*
 * proton.js
 * An implementation of the proton protocol in pure javascript
 * Nicholas Boucher & Aron Szanto
 * April 2018
 */

var proton = (function() {
  'use strict';

  // Codes defined within ProtoN protocol spec
  const codes = {
    PrimNull: 0x0,
    PrimString: 0x1,
    PrimInt: 0x2,
    PrimFloat: 0x3,
    PrimBool: 0x4,
    ConPair: 0x5,
    ConList: 0x6,
    ConObject: 0x7
  };

  // Length (bits) of the defined codes
  const codelen = 3;

  // Protocol Version and length of version encoding
  const version = 0x1;
  const versionlen = 2;

  // Maximum signed 32-bit number (2^31-1)
  const max32 = 2147483647

  // Use JS module syntax
  return {
    /*
     * Encodes the passed `obj` with the proton protocol and returns the
     * generated bitstring
     */
    encode: function(obj) {
      // Internal function which can be called recursively
      function _encode(obj, bits) {
        // Helper function to write strings
        function writeString(str, bits) {
          // Combines built-in encoding functions to achieve UTF-8 encoding
          var utf8 = unescape(encodeURIComponent(str));
          // Prepend string with length
          bits.writebits(utf8.length, 16);
          // Loop through each byte in resulting string and add to bitstring
          for (var i=0; i<utf8.length; i++) {
            bits.writebits(utf8.charCodeAt(i), 8);
          }
          return bits;
        }
        // Find the proton type of the passed variable
        if (obj === null || obj === undefined) {
          return bits.writebits(codes.PrimNull, codelen);
        } else if (typeof(obj) === 'string') {
          // Add String TypeCode
          bits.writebits(codes.PrimString, codelen);
          // Write string
          return writeString(obj, bits);
        } else if (typeof(obj) === 'boolean') {
          bits.writebits(codes.PrimBool, codelen);
          return bits.writebits(obj?1:0, 1);
        } else if (Number.isInteger(obj)) {
          // Add Int TypeCode
          bits.writebits(codes.PrimInt, codelen);
          if (Math.abs(obj) < max32) {
            // Write flag that number is 32-bits
            bits.writebits(0,1);
            // Pack number as 32-bit signed integer
            var buf = new DataView(new ArrayBuffer(4));
            buf.setInt32(0, obj, false);
            // Due to JS bitwise constraints, can't pack more than 16 bits at once
            for (var i=0; i<4; i+=2) {
              bits.writebits(buf.getUint16(i, false), 16);
            }
          } else {
            // Write flag that number is 64-bits
            bits.writebits(1,1);
            // Pack number as 64-bit signed integer
            // TODO: Find a way to handle ints between 32-52 bits
            throw new Error("64 bit integers not natively supported.")
          }
          return bits;
        } else if (typeof(obj) === 'number') {
          // Add Float TypeCode
          bits.writebits(codes.PrimFloat, codelen);
          // Pack number as 64-bit signed float
          var buf = new DataView(new ArrayBuffer(8));
          buf.setFloat64(0, obj, false);
          // Due to JS bitwise constraints, can't pack more than 16 bits at once
          for (var i=0; i<8; i+=2) {
            bits.writebits(buf.getUint16(i, false), 16);
          }
          return bits;
        } else if (Object.prototype.toString.call(obj) === '[object Array]') {
          // Add List Container TypeCode
          bits.writebits(codes.ConList, codelen);
          // Prepend list with length
          bits.writebits(obj.length, 16);
          // Recursively encode each subcomponent
          for (var i=0; i<obj.length; i++) {
            bits = _encode(obj[i], bits);
          }
          return bits;
        } else if (obj === Object(obj)) {
          // Add Object Container TypeCode
          bits.writebits(codes.ConObject, codelen);
          // Prepend object items with length
          bits.writebits(Object.keys(obj).length, 16);
          // Encode each subcomponent
          Object.keys(obj).forEach(function(key) {
              // Add Key-Value pair TypeCode
              bits.writebits(codes.ConPair, codelen);
              // Write the key
              bits = writeString(key, bits)
              // Recursively encode value
              bits = _encode(obj[key], bits);
          });
          return bits;
        }
        // Should never get to this point
        throw new Error("Error encoding object into ProtoN.");
      }
      // Ensure that the object being encoded is within a valid container
      if (!(Object.prototype.toString.call(obj) === '[object Array]'
          || obj === Object(obj))) {
        throw new TypeError("ProtoN Encoding Requires a List or Object.");
      }
      // Object to build the ProtoN message
      var bits = new BitString();
      // Write the ProtoN protocol version
      bits.writebits(version, versionlen);
      // Call the recursive function starting with our header-encoded buffer
      return _encode(obj, bits).toString();
    },

    /* Decodes the passed `bytestr` using the proton protocol and returns the
     * stored object
     */
    decode: function(bitstr) {
      // Helper function to throw malformed error
      function malformed() {
        throw new Error("Malformed ProtoN message.");
      }
      // Helper function to read one TypeCode
      function readCode(bits) {
        return bits.readbits(codelen);
      }
      // Hepler function to read one unsigned 16-bit integer
      function readLen(bits) {
        return bits.readbits(16);
      }
      // Helper function to read strings
      function readString(bits) {
        // Get the length of the string in bytes
        var len = readLen(bits);
        // Read each UTF-8 encoded byte into string
        var utf8 = "";
        for (var i=0; i<len; i++) {
          utf8 += String.fromCharCode(bits.readbits(8));
        }
        // Decode UTF-8 string using built-in decoding function composition
        return decodeURIComponent(escape(utf8));
      }
      // Helper function to determine if element is container (return true)
      // or not a container (return false) without moving cursor
      function isCon(bits) {
        var code = bits.peek(codelen);
        return (code == codes.ConList || code == codes.ConObject);
      }
      // Helper function to decode a primitive
      function decodePrim(bits) {
        // Check that element is not Con or Key
        var code = bits.readbits(codelen);
        if (code == codes.PrimNull) {
          // We will return null, but could also return undefined
          return null;
        } else if (code == codes.PrimString) {
          return readString(bits);
        } else if (code == codes.PrimInt) {
          // Read boolean specifying whether int32 or int64
          var is64Bit = !!(bits.readbits(1));
          if (is64Bit) {
            // Integer value is 64 bits in length
            // Read into buffer
            var buf = new DataView(new ArrayBuffer(8));
            for (var i=0; i<4; i++) {
              buf.setUint16((2*i), bits.readbits(16), false);
            }
            // Thanks to Yusuke Kawasaki for the algorithm
            // (https://github.com/kawanet/int64-buffer)
            const BIT32 = 4294967296;
            var high = buf.getInt32(0, false);
            // JS can only handle integers up to 32 bits, so we will return
            // Infinity for values greater than we can handle
            if (high > 0xFFFFF) {
              return Infinity;
            }
            var low = buf.getInt32(4, false);
            high |= 0; // a trick to get signed
            return high ? (high * BIT32 + low) : low;
          } else {
            var buf = new DataView(new ArrayBuffer(4));
            for (var i=0; i<2; i++) {
              buf.setUint16((2*i), bits.readbits(16), false);
            }
            return buf.getInt32(0, false);
          }
        } else if (code == codes.PrimFloat) {
          // Pack bits into buffer
          var buf = new DataView(new ArrayBuffer(8));
          for (var i=0; i<4; i++) {
            buf.setUint16((2*i), bits.readbits(16), false);
          }
          // Interpret buffer as 64-bit float
          return buf.getFloat64(0, false);
        } else if (code == codes.PrimBool) {
          // Double-not casts number to boolean
          return !!(bits.readbits(1));
        } else {
          malformed();
        }
      }
      // Helper function to decode a container
      function decodeCon(bits) {
        var code = readCode(bits);
        if (code == codes.ConList) {
          // This is the start of a list
          // Get the length of the list
          var len = readLen(bits);
          // Create the list
          var list = [];
          // Process each element of the list
          for (var i=0; i<len; i++) {
            if (isCon(bits)) {
              // The element is another container
              list.push(decodeCon(bits));
            } else {
              // The element is a primitive
              list.push(decodePrim(bits));
            }
          }
          // Return the constructed list
          return list;
        } else if (code == codes.ConObject) {
          // This is the start of an object
          // Get the number of object members
          var members = readLen(bits);
          // Create the list
          var obj = {}
          // Process each member of the object
          for (var i=0; i<members; i++) {
            // Ensure that each element of the object is correctly
            // encoded as a key-value pair
            if (bits.readbits(codelen) != codes.ConPair) {
              malformed();
            }
            // Read the key of the member
            var key = readString(bits);
            // Decode and set the member
            if (isCon(bits)) {
              // The element is another container
              obj[key] = decodeCon(bits);
            } else {
              // The element is a primitive
              obj[key] = decodePrim(bits);
            }
          }
          // Return the constructed object
          return obj;
        } else {
          malformed();
        }
      }
      // Interpret the argument as a sequence of bits
      var bits = new BitString(bitstr);
      // Move to the start of the bit string
      bits.seek(0);
      // Verify that the protocol version matches
      if (bits.readbits(2) != version) {
        throw new Error("Unsupported ProtoN version.");
      }
      // Root element must be a container
      return decodeCon(bits);
    }

  };
})();
