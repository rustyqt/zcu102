#!/usr/bin/python3.8

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import struct
import os
import mmap

aes_gcm_base_addr = 0xa0020000





#######################
### Encryption Part ###
#######################

print("Encrypt.")

#pt = b'Hello World!!!!!'
pt    = get_random_bytes(4096)
#pt    = get_random_bytes(16)
key   = get_random_bytes(32)
iv    = get_random_bytes(12)
tx_id = get_random_bytes(20)

#pt    = b'\x85@\x9c$\xfe\xdfg\x9a\x8b\xf7\xf7\xe46\xde\x13~'
#key   = b'an%\xe6\xe9H \xf6b\xa9\x7f7\x05MX\x81s\x82\xad[m\xdb\x9f\x8a\xcd\xff\xfd\xe4wg\xe4q'
#iv    = b'\xfc\x1aK\xc7\xae\x16\xf1\x04\xe0\xff\xd7\x80'
#tx_id = b's\x84~B\xb2\x00\x0eaJ/^P\x9a\x16\x08wU\xbc\x9c\x9f'


aad = tx_id + iv
aad_pt = aad + pt

cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
cipher.update(aad)
ct, tag = cipher.encrypt_and_digest(pt)

aad_ct_tag = aad + ct + tag

pt_length = round(len(pt)/16)
file_out = open("pt_length.raw", "wb")
file_out.write(pt_length.to_bytes(4, byteorder='big'))
file_out.close()

aad_length = round(len(aad)/16)
file_out = open("aad_length.raw", "wb")
file_out.write(aad_length.to_bytes(4, byteorder='big'))
file_out.close()

aad_pt_length = aad_length + pt_length
aad_ct_tag_length = aad_pt_length + 1

file_out = open("key.raw", "wb")
file_out.write(key)
file_out.close()

file_out = open("aad_pt.raw", "wb")
file_out.write(aad_pt)
file_out.close()

file_out = open("aad_ct_tag.raw", "wb")
file_out.write(aad_ct_tag) 
file_out.close()


print("key[" + str(len(key)) + "] = " + str(key.hex()))
print("iv[" + str(len(cipher.nonce)) + "] = " + str(cipher.nonce.hex()))
print("tx_id[" + str(len(tx_id)) + "] = " + str(tx_id.hex()))
if len(pt) <= 256:
  print("pt[" + str(len(pt)) + "] = " + str(pt.hex()))
  print("ct[" + str(len(ct)) + "] = " + str(ct.hex()))
print("tag[" + str(len(tag)) + "] = " + str(tag.hex()))




#######################
###  Run Hardware   ###
#######################

f = open("/dev/mem", "r+b")
m = mmap.mmap(f.fileno(), 4096, offset=aes_gcm_base_addr)

# Set KEY
m[0x00:0x20] = (int.from_bytes(key, byteorder='big')).to_bytes(32, byteorder='little')

# Set IV and AAD_LENGTH
m[0x20:0x30] = (int.from_bytes(iv, byteorder='big')).to_bytes(12, byteorder='little') + \
                               aad_length.to_bytes(4, byteorder='little')

# Set PT_LENGTH
m[0x30:0x34] = pt_length.to_bytes(4, byteorder='little')

# Apply KEY
m[0x34] = 0x48

# Apply IV
m[0x34] = 0x44

# Start Operation
m[0x34] = 0x42

# Send data to AES GCM via AXI DMA
os.system("axidma-transfer aad_pt.raw aad_ct_tag_hw.raw -s 4144")

# Stop Operation
m[0x34] = 0x41

# Reset AES GCM Pipeline
m[0x34] = 0x50

#print("key: " + m[0x00:0x20].hex())
#print("iv: " + m[0x20:0x30].hex())
#print("aad_length: " + m[0x2C:0x30].hex())
#print("pt_length: " + m[0x30:0x34].hex())

m.close()
f.close()


#######################
### Decryption Part ###
#######################


file_in = open("aad_ct_tag_hw.raw", "rb")
tx_id, iv, ct, tag = [ file_in.read(x) for x in (len(aad)-len(iv), len(iv), len(pt), 16) ]
aad = tx_id + iv

# let's assume that the key is somehow available again
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
cipher.update(aad)
decrypted_plaintext = cipher.decrypt_and_verify(ct, tag)

assert decrypted_plaintext == pt, "Decrypted message is not plaintext."
print("\nDecrypt. OK.")

if len(pt) <= 256:    
  print("decrypted_plaintext = " + str(decrypted_plaintext.hex()))

# Check for differences
os.system("diff -s aad_ct_tag.raw aad_ct_tag_hw.raw")



