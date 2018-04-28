
## Pseudo code in Python-like syntax for packing bits into JS uint8 byte arrays

bytes = [0x0] * 64
byte_idx = 0
counter = 0

# bytes is Uint8Array
def pack_bit(length, bytes):
  def incr_idx():
      if byte_idx >= len(bytes)-1:
        bytes += [0o0] * 64
      byte_idx += 1
      counter = 0
  for byte in bytes:
    # Calculate how many bits are left to pack in this byte
    if length <= 8:
        remaining = length
        length = 0
    else:
        remaining = 8
        length -= 8

    if counter >= 8:
      incr_idx()
    if counter != 0:
        bytes[byte_idx] = bytes[byte_idx] | (byte >>> counter)
        incr_idx()
        bytes[byte_idx] = byte << counter
        counter = 8 - counter
    else:
        bytes[byte_idx] = byte

def get_bytes():
  # Currently end-pads with zeros to next byte. How to remove this?
  return bytes[:byte_idx]
