#!/usr/bin/env node

// Import ProtoN JS
var fs = require('fs');
eval(fs.readFileSync('../src/js/proton.min.js')+'');

// Assert correct command line options
if (process.argv.length != 3) {
  console.log("Usage: ./proton_test.js <filename>");
  process.exit(1);
}

// Open JSON file for parsing
var json = fs.readFileSync(process.argv[2])+'';
var obj = JSON.parse(json);

// Assert that proton encoding/decoding is internally correct
if (JSON.stringify(obj) != JSON.stringify(proton.decode(proton.encode(obj)))) {
  console.log("FAIL");
  process.exit(0);
}

// Print the bytes of the encoding
console.log(proton.encode(obj).join());
