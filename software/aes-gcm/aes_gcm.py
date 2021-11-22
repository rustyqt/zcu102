#!/usr/bin/python3.8

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from axidma import axidma

import mmap

class aes_gcm():
    """ Class for AES GCM encryption"""
    def __init__(self, base_addr, key, iv, aad_len, pt_len):
        """ 
        Description:
            AES GCM class constructor.
        
        Parameters:
            base_addr<int>   : Physical base addres of the AES GCM module
            key      <bytes> : 256-bit AES key
            aad_len  <int>   : Length of Addition Authenticated Data in Bytes 
            pt_len   <int>   : Length of Plaintext in Bytes
        """
        # Check if requested length is 128-bit word aligned
        assert aad_len % 16 == 0, "Error: aad_len (in bytes) has to be 128-bit aligned"
        assert pt_len % 16 == 0, "Error: pt_len (in bytes) has to be 128-bit aligned"

        self.aad_length = aad_len
        self.pt_length  = pt_len
        self.tag_length = 16

        self.aad_pt_length     = self.aad_length + self.pt_length
        self.aad_ct_tag_length = self.aad_length + self.pt_length + self.tag_length

        self.aad_words = round(self.aad_length/16)
        self.pt_words  = round(self.pt_length/16)

        self.iv = iv
        self.key = key

        # Mmap devmem
        self.f_mem = open("/dev/mem", "r+b")
        self.devmem = mmap.mmap(self.f_mem.fileno(), 4096, offset=base_addr)
        

        self.dma = axidma()

        self.dma.malloc("aad_pt", self.aad_pt_length)
        self.dma.malloc("aad_ct_tag", self.aad_ct_tag_length)

    def encrypt(self):
        
        # Start Hardware Encryption
        # Set KEY
        self.devmem[0x00:0x20] = (int.from_bytes(self.key, byteorder='big')).to_bytes(32, byteorder='little')

        # Set IV and AAD_LENGTH
        self.devmem[0x20:0x30] = (int.from_bytes(self.iv, byteorder='big')).to_bytes(12, byteorder='little') + \
                                        self.aad_words.to_bytes(4, byteorder='little')

        # Set PT_LENGTH
        self.devmem[0x30:0x34] = self.pt_words.to_bytes(4, byteorder='little')

        # Apply KEY
        self.devmem[0x34] = 0x48

        # Apply IV
        self.devmem[0x34] = 0x44

        # Start Operation
        self.devmem[0x34] = 0x42

        self.dma.twoway_transfer(self.dma.tx_ch[0], "aad_pt", self.aad_pt_length, \
                                 self.dma.rx_ch[0], "aad_ct_tag", self.aad_ct_tag_length)

        # Stop Operation
        self.devmem[0x34] = 0x41
        
        # Reset AES GCM Pipeline
        self.devmem[0x34] = 0x50
    
    def encrypt_sw(self):
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=self.iv)
        cipher.update(self.dma.buf["aad_pt"][0:self.aad_length])
        return cipher.encrypt_and_digest(self.dma.buf["aad_pt"][self.aad_length:self.aad_pt_length])

    def __exit__(self):
        self.f_mem.close()
        self.devmem.close()
