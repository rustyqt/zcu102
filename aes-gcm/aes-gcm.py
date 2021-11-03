#!/usr/bin/python3.8

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from datetime import datetime

import os
import mmap

AES_GCM_BASE_ADDR = 0xa0020000




######################################
### Generate AES-GCM configuration ###
######################################

#pt = b'Hello World!!!!!'
pt    = get_random_bytes(4096)
key   = get_random_bytes(32)
iv    = get_random_bytes(12)
tx_id = get_random_bytes(20)

aad = tx_id + iv
aad_pt = aad + pt



###############################
### Run Software Encryption ###
###############################

# Start Timer
time_sw_start = datetime.now()

# Start Encryption
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
cipher.update(aad)
ct, tag = cipher.encrypt_and_digest(pt)

# Stop Timer
time_sw_end = datetime.now()
time_sw = time_sw_end - time_sw_start


aad_ct_tag = aad + ct + tag



#############################################
### Write AES-GCM configuration to Files  ###
#############################################

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



####################################
### Print AES-GCM Configuration  ###
####################################

print("key[" + str(len(key)) + "] = " + str(key.hex()))
print("iv[" + str(len(cipher.nonce)) + "] = " + str(cipher.nonce.hex()))
print("tx_id[" + str(len(tx_id)) + "] = " + str(tx_id.hex()))
if len(pt) <= 256:
  print("pt[" + str(len(pt)) + "] = " + str(pt.hex()))
  print("ct[" + str(len(ct)) + "] = " + str(ct.hex()))
print("tag[" + str(len(tag)) + "] = " + str(tag.hex()))




################################
### Run Hardware Encryption  ###
################################

# Mmap devmem
f = open("/dev/mem", "r+b")
m = mmap.mmap(f.fileno(), 4096, offset=AES_GCM_BASE_ADDR)

# Start Timer
time_hw_start = datetime.now()


# Start Hardware Encryption
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

# Stop Timer
time_hw_end = datetime.now()
time_hw = time_hw_end - time_hw_start

# Close mmap and devmem
m.close()
f.close()



###############################
### Run Software Decryption ###
###############################

file_in = open("aad_ct_tag_hw.raw", "rb")
tx_id, iv, ct, tag = [ file_in.read(x) for x in (len(aad)-len(iv), len(iv), len(pt), 16) ]
aad = tx_id + iv

# Let's assume that the key is somehow available again
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

# Update the cipher with AAD
cipher.update(aad)

# Decrypt cipher test and verify data authenticity using the TAG
decrypted_plaintext = cipher.decrypt_and_verify(ct, tag)



#################################
## Perform Verification Checks ##
#################################

print("Time Software Encryption: " + str(time_sw.seconds) + "s " + str(time_sw.microseconds) + "us")
print("Time Hardware Encryption: " + str(time_hw.seconds) + "s " + str(time_hw.microseconds) + "us")

assert decrypted_plaintext == pt, "Decrypted message is not plaintext."
print("\nDecrypt. OK.")

# Print plaintext in case of short messages
if len(pt) <= 256:    
  print("decrypted_plaintext = " + str(decrypted_plaintext.hex()))

# Check for differences in software vs hardware encryption
os.system("diff -s aad_ct_tag.raw aad_ct_tag_hw.raw")



