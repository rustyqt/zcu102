#!/usr/bin/python3.8

import sys
sys.path.insert(0, '../server/')
sys.path.insert(0, '../../tftp/')
sys.path.insert(0, '../../aes-gcm/')
sys.path.insert(0, '../../axidma/')
sys.path.insert(0, '../../demo/')

from jsonrpc_server import jsonrpc_server
from demo import demo
from tftp import tftp
from axidma import axidma
from aes_gcm import aes_gcm

rpc = jsonrpc_server()

# Add demo class
rpc.add(demo())

# Add DMA, AES and TFTP classes
axidma_0 = axidma()
aes_gcm_0 = aes_gcm(axidma_0)
tftp_0 = tftp(axidma_0)

rpc.add(tftp_0)
rpc.add(axidma_0)
rpc.add(aes_gcm_0)

# Run RPC Server
rpc.run()