#!/bin/sh

# Set KEY
devmem 0xa0020000 32 0x1d8fad24
devmem 0xa0020004 32 0x2c4bf4f6
devmem 0xa0020008 32 0xe8748930
devmem 0xa002000C 32 0xdb5398ae
devmem 0xa0020010 32 0x6071563c
devmem 0xa0020014 32 0xbd6411c3
devmem 0xa0020018 32 0x8bfa42b8
devmem 0xa002001C 32 0x908b1961

# Set IV
devmem 0xa0020020 32 0x14108d98
devmem 0xa0020024 32 0xe6a2db9e
devmem 0xa0020028 32 0xfc5bc5c6

# Set AAD LENGTH
devmem 0xa002002C 32 0x00000002

# Set PT LENGTH
devmem 0xa0020030 32 0x00000100

# Apply KEY
devmem 0xa0020034 32 0x00000048

# Apply IV
devmem 0xa0020034 32 0x00000044

# Start Operation
devmem 0xa0020034 32 0x00000042

# Send Data to AES GCM Core via AXI DMA
axidma-transfer aad_pt.raw aad_ct_tag_hw.raw -s 4144

# Stop Operation
devmem 0xa0020034 32 0x00000041

# Reset AES GCM Pipeline
devmem 0xa0020034 32 0x00000050

