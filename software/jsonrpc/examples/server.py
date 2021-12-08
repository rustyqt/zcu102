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


inst = myclass()

rpc = jsonrpc_server(inst)

rpc.run()