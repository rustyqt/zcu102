#!/usr/bin/python3.8

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from datetime import datetime


from aes_gcm import aes_gcm

AES_GCM_BASE_ADDR = 0xa0020000

key = get_random_bytes(32)
iv  = get_random_bytes(12)

aad_len = 32
pt_len  = 2**22

aesgcm = aes_gcm(AES_GCM_BASE_ADDR, key, iv, aad_len, pt_len)

pt = get_random_bytes(pt_len)
tx_id = get_random_bytes(20)

aad = tx_id + iv
aad_pt = aad + pt

tag_length        = 16
aad_pt_length     = aad_len + pt_len
aad_ct_tag_length = aad_len + pt_len + tag_length

print("aad_pt_length: " + str(aad_pt_length))
print("aad_ct_tag_length: " + str(aad_ct_tag_length))


# Put aad_pt
print("Put aad_pt")
for i in range(aad_pt_length):
    aesgcm.dma.buf["aad_pt"][i] = aad_pt[i]

###############################
### Run Software Encryption ###
###############################

# Start Timer
time_sw_start = datetime.now()

# Start Encryption
ct, tag = aesgcm.encrypt_sw()

# Stop Timer
time_sw_end = datetime.now()
time_sw = time_sw_end - time_sw_start

aad_ct_tag_sw = aad + ct + tag


####################################
### Print AES-GCM Configuration  ###
####################################

print("key[" + str(len(key)) + "] = " + str(key.hex()))
print("iv[" + str(len(iv)) + "] = " + str(iv.hex()))
print("tx_id[" + str(len(tx_id)) + "] = " + str(tx_id.hex()))
if len(pt) <= 256:
  print("pt[" + str(len(pt)) + "] = " + str(pt.hex()))
  print("ct[" + str(len(ct)) + "] = " + str(ct.hex()))
print("tag[" + str(len(tag)) + "] = " + str(tag.hex()))


################################
### Run Hardware Encryption  ###
################################


# Start Timer
time_hw_start = datetime.now()

aesgcm.encrypt()

# Stop Timer
time_hw_end = datetime.now()
time_hw = time_hw_end - time_hw_start


###############################
### Run Software Decryption ###
###############################

tx_id = aesgcm.dma.buf["aad_ct_tag"][0:len(aad)-len(iv)]
iv    = aesgcm.dma.buf["aad_ct_tag"][len(aad)-len(iv):len(aad)]
ct    = aesgcm.dma.buf["aad_ct_tag"][len(aad):len(aad)+len(pt)]
tag   = aesgcm.dma.buf["aad_ct_tag"][len(aad)+len(pt):len(aad)+len(pt)+tag_length]

aad = tx_id + iv

# Let's assume that the key is somehow available again
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

# Update the cipher with AAD
cipher.update(aad)

# Decrypt cipher text and verify data authenticity using the TAG
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
print("PT:")
print(aesgcm.dma.buf["aad_pt"][0:16].hex())
print(aesgcm.dma.buf["aad_pt"][16:32].hex())
print(aesgcm.dma.buf["aad_pt"][32:48].hex())
print(aesgcm.dma.buf["aad_pt"][48:64].hex())
print("HW:")
print(aesgcm.dma.buf["aad_ct_tag"][0:16].hex())
print(aesgcm.dma.buf["aad_ct_tag"][16:32].hex())
print(aesgcm.dma.buf["aad_ct_tag"][32:48].hex())
print(aesgcm.dma.buf["aad_ct_tag"][48:64].hex())
print("SW:")
print(aad_ct_tag_sw[0:16].hex())
print(aad_ct_tag_sw[16:32].hex())
print(aad_ct_tag_sw[32:48].hex())
print(aad_ct_tag_sw[48:64].hex())
assert aesgcm.dma.buf["aad_ct_tag"][0:aad_ct_tag_length] == aad_ct_tag_sw, "Error: Hardware and Software aad_ct_tag differ."

print("Success: HW and SW encryption is identical!")
