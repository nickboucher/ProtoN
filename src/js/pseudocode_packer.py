
## Pseudo code in Python-like syntax for packing bits into JS uint8 byte arrays

bytes = [0x0] * 64
byte_idx = 0
counter = 0

# What type is bits?
def pack_bit(bits):
  for bit in bits:
    if counter >= 8:
      if byte_idx >= len(bytes)-1:
        bytes += [0x0] * 64
      byte_idx += 1
      counter = 0
    # What type is bit? Does this shift create the correct result?
    bytes[counter] = bytes[counter] & (bit << counter)

def get_bytes():
  # Currently end-pads with zeros to next byte. How to remove this?
  return bytes[:byte_idx]
