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
          var strlen = Struct.Pack('!H', [utf8.length]);
          for (var i=0; i<strlen.length; i++) {
            bits.writebits(strlen[i], 8);
          }
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
            var num = Struct.Pack('!i', [obj]);
            for (var i=0; i<num.length; i++) {
              bits.writebits(num[i]);
            }
          } else {
            // Write flag that number is 64-bits
            bits.writebits(1,1);
            // Pack number as 64-bit signed integer
            throw new Error("64 bit integers not natively supported.")
          }
          return bits;
        } else if (typeof(obj) === 'number') {
          // Add Float TypeCode
          bits.writebits(codes.PrimFloat, codelen);
          // Pack number as 64-bit signed float
          var num = Struct.Pack('!d', [obj]);
          for (var i=0; i<num.length; i++) {
            bits.writebits(num[i]);
          }
          return bits;
        } else if (Object.prototype.toString.call(obj) === '[object Array]') {
          // Add List Container TypeCode
          bits.writebits(codes.ConList, codelen);
          // Prepend list with length
          var listlen = Struct.Pack('!H', [obj.length]);
          for (var i=0; i<listlen.length; i++) {
            bits.writebits(listlen[i], 8);
          }
          // Recursively encode each subcomponent
          for (var i=0; i<obj.length; i++) {
            bits = _encode(obj[i], bits);
          }
          return bits;
        } else if (obj === Object(obj)) {
          // Add Object Container TypeCode
          bits.writebits(codes.ConObject, codelen);
          // Prepend object items with length
          var members = Struct.Pack('!H', [Object.keys(obj).length]);
          for (var i=0; i<members.length; i++) {
            bits.writebits(members[i], 8);
          }
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
      return _encode(obj, bits);
    },

    /* Decodes the passed `bytestr` using the proton protocol and returns the
     * stored object
     */
    decode: function(bytestr) {
      var output = "";
      for (var i = 0; i < bytestr.length; i++) {
        output += input[i].charCodeAt(0).toString(2) + " ";
      }
      return {}
    }

  };
})();
