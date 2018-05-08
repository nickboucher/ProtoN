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

  // Maximum signed 8-bit number (2^7-1)
  const max8 = 127
  // Maximum signed 16-bit number (2^15-1)
  const max16 = 32767
  // Maximum signed 32-bit number (2^31-1)
  const max32 = 2147483647
  // Maximum signed 64-bit number (2^63-1)
  const max64 = 9223372036854775807;
  // Constant for accessing high 32-bits of 64-bit ints (2^32)
  const BIT32 = 4294967296;

  // BEGIN Modified BitString Library packaged within ProtoN closure
  // Thanks to David Schoonover (https://github.com/dsc/bitstring.js)
  var SEEK_ABSOLUTE, SEEK_RELATIVE, SEEK_FROM_EOF, bin, hex, binlen, mask, chr, ord, BitString;
  SEEK_ABSOLUTE = 0;
  SEEK_RELATIVE = 1;
  SEEK_FROM_EOF = 2;
  bin = function(n){
    var s;
    do {
      s = (n % 2 ? '1' : '0') + (s || '');
      n >>= 1;
    } while (n);
    return s;
  };
  hex = function(n){
    return Number(n).toString(16);
  };
  binlen = function(n){
    return bin(Math.abs(n)).length;
  };
  mask = function(n){
    return (1 << n) - 1;
  };
  chr = function(it){
    return String.fromCharCode(it);
  };
  ord = function(it){
    return String(it).charCodeAt(0);
  };
  /**
   * File-like object for reading/writing bits.
   * @class
   */
  BitString = (function(){
    BitString.displayName = 'BitString';
    var prototype = BitString.prototype, constructor = BitString;
    prototype.buf = null;
    prototype._pos = -1;
    prototype._spill = 0;
    prototype._spillen = 0;
    prototype._peek = 0;
    prototype._peeklen = 0;
    function BitString(source, buf){
      var i, __to;
      source == null && (source = '');
      buf == null && (buf = []);
      this.buf = buf.slice();
      for (i = 0, __to = source.length; i < __to; ++i) {
        this._bufwrite(source.charCodeAt(i));
      }
    }
    prototype.size = function(){
      return this.buf.length + (this._spillen ? 1 : 0);
    };
    prototype.bitsize = function(){
      return this.buf.length * 8 + this._spillen;
    };
    prototype._bufwrite = function(b){
      if (this._pos === -1) {
        this.buf.push(b);
      } else {
        this.buf[this._pos] = b;
        if (++this._pos >= this.buf.length) {
          this._pos = -1;
        }
      }
      return this;
    };
    prototype.writebits = function(n, size){
      var bits, b;
      size = size || binlen(n);
      bits = this._spill << size | n;
      size += this._spillen;
      while (size >= 8) {
        size -= 8;
        b = bits >> size;
        bits &= mask(size);
        this._bufwrite(b);
      }
      this._spill = bits;
      this._spillen = size;
      return this;
    };
    prototype.flush = function(){
      var b;
      b = this._spill;
      if (this._spillen) {
        b <<= 8 - this._spillen;
        this._bufwrite(b);
      }
      this._spill = 0;
      this._spillen = 0;
      return this;
    };
    prototype.truncate = function(){
      this.buf = [];
      this._pos = -1;
      this._spill = 0;
      this._spillen = 0;
      this._peek = 0;
      this._peeklen = 0;
      return this;
    };
    prototype._bufseek = function(n, mode){
      var pos;
      mode == null && (mode = SEEK_ABSOLUTE);
      switch (mode) {
      case 1:
        pos = this._pos + n;
        break;
      case 2:
        pos = this.buf.length + n;
        break;
      default:
        pos = n;
      }
      this._pos = pos >= this.buf.length
        ? -1
        : Math.max(0, pos);
      return this;
    };
    prototype.seek = function(n, mode){
      mode == null && (mode = SEEK_ABSOLUTE);
      this.flush();
      this._peek = 0;
      this._peeklen = 0;
      this._bufseek(n, mode);
      return this;
    };
    prototype.tell = function(){
      if (this._pos === -1) {
        return this.buf.length;
      } else {
        return this._pos;
      }
    };
    prototype._nextbyte = function(){
      var byte;
      if (this._pos === -1) {
        return null;
      }
      byte = this.buf[this._pos++];
      if (this._pos >= this.buf.length) {
        this._pos = -1;
      }
      return byte;
    };
    prototype.readbits = function(n){
      var size, bits, byte;
      if (n == 0) {
        return 0;
      }
      size = this._peeklen;
      bits = this._peek;
      while (size < n) {
        byte = this._nextbyte();
        if (byte == null) {
          break;
        }
        size += 8;
        bits = bits << 8 | byte;
      }
      if (size > n) {
        this._peeklen = size - n;
        this._peek = bits & mask(this._peeklen);
        bits >>= this._peeklen;
      } else {
        this._peeklen = 0;
        this._peek = 0;
      }
      return size ? bits : null;
    };
    prototype.peek = function(n){
      var offset, size, bits, byte, pos;
      offset = 0;
      size = this._peeklen;
      bits = this._peek;
      pos = this._pos;
      while (size < n) {
        byte = this._nextbyte();
        if (byte == null) {
          break;
        }
        offset += 1;
        size += 8;
        bits = bits << 8 | byte;
      }
      if (size == 0) {
        return null;
      }
      if (size > n) {
        bits >>= size - n;
      }
      if (offset) {
        this._bufseek(pos);
      }
      return bits;
    };
    prototype.hasMore = function(){
      return this.peek(1) != null;
    };
    prototype.each = function(fn, cxt){
      cxt == null && (cxt = this);
      this.buf.forEach(fn, cxt);
      return this;
    };
    prototype.map = function(fn, cxt){
      cxt == null && (cxt = this);
      return this.buf.map(fn, cxt);
    };
    prototype.reduce = function(fn, acc, cxt){
      cxt == null && (cxt = this);
      fn = fn.bind(this);
      return this.buf.reduce(fn, acc);
    };
    prototype.bytearray = function(){
      return this.flush().buf.slice();
    };
    prototype.bin = function(byte_sep){
      byte_sep == null && (byte_sep = '');
      return this.flush().buf.map(bin).join(byte_sep);
    };
    prototype.hex = function(){
      return this.flush().buf.map(hex).join('');
    };
    prototype.number = function(){
      this.flush();
      return this.reduce(function(n, byte){
        return n << 8 | byte;
      });
    };
    prototype.dump = function(){
      return this.buf.map(chr).join('') + (this._spillen ? chr(this._spill << 8 - this._spillen) : '');
    };
    prototype.repr = function(dump_buf){
      var s;
      dump_buf == null && (dump_buf = true);
      s = dump_buf
        ? "buf=" + this.dump()
        : "len(buf)=" + this.buf.length;
      return "BitString(" + s + ", spill[" + this._spillen + "]=" + bin(this._spill) + ", tell=" + this.tell() + ", peek[" + this._peeklen + "]=" + bin(this._peek) + ")";
    };
    prototype.toString = function(){
      return this.flush().dump();
    };
    return BitString;
  }());
  BitString.SEEK_ABSOLUTE = SEEK_ABSOLUTE;
  BitString.SEEK_RELATIVE = SEEK_RELATIVE;
  BitString.SEEK_FROM_EOF = SEEK_FROM_EOF;
  // END Modified BitString Library packaged within ProtoN closure

  /*
   * Encodes the passed `obj` with the proton protocol and returns the
   * generated bitstring
   */
   var encode = function(obj) {
    // Internal function which can be called recursively
    function _encode(obj, bits) {
      // Helper function to write strings of max character length 2^`maxlen`
      function _writeString(str, bits, maxlen) {
        // Combines built-in encoding functions to achieve UTF-8 encoding
        var utf8 = unescape(encodeURIComponent(str));
        // Prepend string with length
        bits.writebits(utf8.length, maxlen);
        // Loop through each byte in resulting string and add to bitstring
        for (var i=0; i<utf8.length; i++) {
          bits.writebits(utf8.charCodeAt(i), 8);
        }
        return bits;
      }
      // Helper function to write String
      function writeString(str, bits) {return _writeString(str,bits,16);}
      // Helper function to write ShortStr
      function writeShortStr(str, bits) {return _writeString(str,bits,3);}
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
        // Absolute value of number to write
        var abs = Math.abs(obj);
        if (abs <= max8) {
          // Write flag that number is 8-bits
          bits.writebits(0,2);
          // Pack number as 8-bit signed integer
          var buf = new DataView(new ArrayBuffer(1));
          buf.setInt8(0, obj, false);
          bits.writebits(buf.getUint8(0, false), 8);
        } else if (abs <= max16) {
          // Write flag that number is 16-bits
          bits.writebits(1,2);
          // Pack number as 16-bit signed integer
          var buf = new DataView(new ArrayBuffer(2));
          buf.setInt16(0, obj, false);
          bits.writebits(buf.getUint16(0, false), 16);
        } else if (abs <= max32) {
          // Write flag that number is 32-bits
          bits.writebits(2,2);
          // Pack number as 32-bit signed integer
          var buf = new DataView(new ArrayBuffer(4));
          buf.setInt32(0, obj, false);
          // Due to JS bitwise constraints, can't pack more than 16 bits at once
          for (var i=0; i<4; i+=2) {
            bits.writebits(buf.getUint16(i, false), 16);
          }
        } else if (abs <= max64){
          // Write flag that number is 64-bits
          bits.writebits(3,2);
          // Pack number as 64-bit signed integer
          var low = obj & (0xFFFFFFFF);
          var high = (obj - low) / BIT32;
          var bitArr = [high>>>16, high&(0xFFFF), low>>>16, low&(0xFFFF)];
          for (var i=0; i<bitArr.length; i++) {
            bits.writebits(bitArr[i], 16);
          }
        } else {
          throw new Error("Cannot encode intergers greater than 64 bits.");
        }
        return bits;
      } else if (typeof(obj) === 'number') {
        // Add Float TypeCode
        bits.writebits(codes.PrimFloat, codelen);
        // If the string encoding is smaller than 8 bytes, encode as string
        if ((obj + "").length < 8) {
          // Add flag for encoding float as string
          bits.writebits(0,1);
          // Pack number as a string
          writeShortStr((obj+""), bits);
        } else {
          // Add flag for encoding float as IEEE 654 64-bit float
          bits.writebits(1,1);
          // Pack number as 64-bit signed float
          var buf = new DataView(new ArrayBuffer(8));
          buf.setFloat64(0, obj, false);
          // Due to JS bitwise constraints, can't pack more than 16 bits at once
          for (var i=0; i<8; i+=2) {
            bits.writebits(buf.getUint16(i, false), 16);
          }
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
    var encoded = _encode(obj, bits);
    // Return the value as a binary buffer
    return new Uint8Array(encoded.bytearray());
  }

  /*
   * Decodes the passed `bytearr` using the proton protocol and returns the
   * stored object
   */
  var decode = function(bitarr) {
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
    function _readString(bits, len) {
      // Read each UTF-8 encoded byte into string
      var utf8 = "";
      for (var i=0; i<len; i++) {
        utf8 += String.fromCharCode(bits.readbits(8));
      }
      // Decode UTF-8 string using built-in decoding function composition
      return decodeURIComponent(escape(utf8));
    }
    // Helper function to read Strings
    function readString(bits) {
      // Get the length of the string in bytes
      var len = readLen(bits);
      return _readString(bits, len);
    }
    // Helper function to read ShortStr
    function readShortStr(bits) {
      var len = bits.readbits(3);
      return _readString(bits, len);
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
        // Read value giving number of bits for int encoding
        var bitlen = Math.pow(2, bits.readbits(2) + 3);
        if (bitlen == 64) {
          // Integer value is 64 bits in length
          // Read into buffer
          var buf = new DataView(new ArrayBuffer(8));
          for (var i=0; i<4; i++) {
            buf.setUint16((2*i), bits.readbits(16), false);
          }
          // Thanks to Yusuke Kawasaki for the algorithm
          // (https://github.com/kawanet/int64-buffer)
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
          var bytes = bitlen/8;
          var buf = new DataView(new ArrayBuffer(bytes));
          for (var i=0; i<bytes; i++) {
            buf.setUint8(i, bits.readbits(8), false);
          }
          if (bitlen == 8) {
            return buf.getInt8(0, false);
          } else if (bitlen == 16) {
            return buf.getInt16(0, false);
          } else if (bitlen == 32) {
            return buf.getInt32(0, false);
          } else {
            malformed();
          }
        }
      } else if (code == codes.PrimFloat) {
        // Read boolean specifying whether String or IEEE 754 format
        var is754 = !!(bits.readbits(1));
        if (is754) {
          // Data is in IEEE 754 format
          // Pack bits into buffer
          var buf = new DataView(new ArrayBuffer(8));
          for (var i=0; i<4; i++) {
            buf.setUint16((2*i), bits.readbits(16), false);
          }
          // Interpret buffer as 64-bit float
          return buf.getFloat64(0, false);
        } else {
          // Data is a UTF-8 encoded string
          return parseFloat(readShortStr(bits));
        }
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
    // Assert that argument is a Uint8Array
    if (!(bitarr instanceof Uint8Array)) {
      throw new TypeError("proton.decode argument must be Uint8Array");
    }
    // Interpret the argument as a array of bytes
    var bits = new BitString('', bitarr);
    // Move to the start of the bit string
    bits.seek(0);
    // Verify that the protocol version matches
    if (bits.readbits(2) != version) {
      throw new Error("Unsupported ProtoN version.");
    }
    // Root element must be a container
    return decodeCon(bits);
  }

  /*
   * Creates a new HTTP GET request to the given `URL` passing object`data` via
   * the query string and calling `success` with the ProtoN-decoded response
   */
  var get = function(url, data, success) {
    var xhr = new XMLHttpRequest();
    // Build query string
    url += "?" + Object
          .keys(data)
          .map(function(key){
            return key+"="+encodeURIComponent(data[key])
          })
          .join("&");
    xhr.open('GET', url);
    xhr.responseType = 'arraybuffer';
    xhr.onreadystatechange = function() {
      if (xhr.readyState == XMLHttpRequest.DONE && success) {
        var response = null;
        var arrayBuffer = xhr.response;
        if (arrayBuffer) {
          var byteArray = new Uint8Array(arrayBuffer);
          response = proton.decode(byteArray);
        }
        success(response);
      }
    }
    xhr.send(data);
  }

  /*
   * Creates a new HTTP POST request to the given `URL` passing  a
   * ProtoN-encoded form of `data` and calling `success` with the
   * ProtoN-decoded response
   */
  var post = function(url, data, success) {
    var msg = proton.encode(data);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'proton');
    xhr.responseType = 'arraybuffer';
    xhr.onreadystatechange = function() {
      if (xhr.readyState == XMLHttpRequest.DONE && success) {
        var response = null;
        var arrayBuffer = xhr.response;
        if (arrayBuffer) {
          var byteArray = new Uint8Array(arrayBuffer);
          response = proton.decode(byteArray);
        }
        success(response);
      }
    }
    xhr.send(msg);
  }

  // Encode and decode functions exported by ProtoN, using JS module syntax
  return {
    encode: encode,
    decode: decode,
    get: get,
    post: post
  };
})();
