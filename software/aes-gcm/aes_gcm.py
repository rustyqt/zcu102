#!/usr/bin/python3.8
import sys
sys.path.insert(0, '../axidma/')

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from axidma import axidma

import mmap

class aes_gcm():
    """ Class for AES GCM encryption"""
    def __init__(self, dma, base_addr = 0xa0020000):
        """ 
        Description:
            AES GCM class constructor.
        
        Parameters:
            base_addr<int>   : Physical base addres of the AES GCM module
        """
        self.aad_length = None
        self.pt_length  = None
        self.tag_length = 16

        self.aad_pt_length     = None
        self.aad_ct_tag_length = None

        self.aad_words = None
        self.pt_words  = None

        self.iv = None
        self.key = None

        # Mmap devmem
        self.f_mem = open("/dev/mem", "r+b")
        self.devmem = mmap.mmap(self.f_mem.fileno(), 4096, offset=base_addr)
        
        self.dma = dma

    def config(self, key0x : str, iv0x : str, aad_len : int, pt_len : int) -> int:
        """ 
        Description:
           Allocates physical memory for DMA purposes
        
        Parameters:
            key     <str> : 32 Byte HEX String, e.g. '0x8785fb65432b201f1b4d2687c9d7fc44d4ec93669c5d14d60785252ab1452916'
            iv      <str> : 12 Byte HEX String, e.g. '0xc92f43ceb2ea700e8703e8f1'
            aad_len <int> : Additional Authenticated Data (AAD) lengths in bytes, has to be 128-bit aligned
            pt_len  <int> : Plain Text (PT) length in bytes, has to be 128-bit aligned
        Returns:
            ret     <int> : 0 = Success
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

        self.iv = int(iv0x, 0).to_bytes(32, byteorder='big')
        self.key = int(key0x, 0).to_bytes(32, byteorder='big')
        
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

        return 0

    def encrypt(self, ibuf : str, obuf : str) -> int:
        
        # Start Hardware Encryption
        self.devmem[0x34] = 0x42

        # Start DMA Transfer
        self.dma.twoway_transfer(0, ibuf, self.aad_pt_length, \
                                 0, obuf, self.aad_ct_tag_length)

        # Stop Operation
        self.devmem[0x34] = 0x41
        
        # Reset AES GCM Pipeline
        self.devmem[0x34] = 0x50

        return 0

    def __exit__(self):
        self.f_mem.close()
        self.devmem.close()
