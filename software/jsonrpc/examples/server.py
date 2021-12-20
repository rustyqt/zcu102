#!/usr/bin/python

import sys
sys.path.insert(0, '../server/')

from jsonrpc_server import jsonrpc_server     

class myclass():
    def __init__(self, value : int = 0):
        self.value = value

    def echo(self, message : str) -> str:
        return message

    def set_val(self, value : int) -> int:
        self.value = value
        return 0

    def get_val(self) -> int:
        return self.value

    def add(self, a : int, b : int) -> int:
        return a+b

    def mult(self, a : int, b : int) -> int:
        return a*b

class mytftp():
    def __init__(self, ip : str = "127.0.0.1"):
        self.ip = ip
    
    def set_ip(self, ip : str) -> int:
        self.ip = ip
        return 0

    def get_ip(self) -> str:
        return self.ip

class myaes():
    def __init__(self, aes_type : str = "AESGCM", key : int = 0, iv : int = 0):
        self.type = aes_type
        self.key = key
        self.iv = iv

    def config(self, key : int, iv : int) -> int:
        self.key = key
        self.iv = iv
        return 0

    def encrypt(self, source : str, target : str) -> int:
        return 0



rpc = jsonrpc_server()

rpc.add(myclass())
rpc.add(mytftp())
rpc.add(myaes())

rpc.run()