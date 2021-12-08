#!/usr/bin/python

import sys
sys.path.insert(0, '../client/')

from jsonrpc_pyclient.connectors import socketclient
from jsonrpc_client import jsonrpc_client
    
if __name__ == '__main__':    

    # Create TCP Socket Client
    connector = socketclient.TcpSocketClient("127.0.0.1", 4000)
    
    # Create RPC client
    rpc = jsonrpc_client(connector)

    # Call echo()    
    result = rpc.echo("Hello RPC!")
    print("rpc.echo('Hello RPC!') -> " + str(result))

    # Call mult()
    result = rpc.mult(4, 2)
    print("rpc.mult(4, 2) -> " + str(result))

    # Call add()
    result = rpc.add(2, 2)
    print("rpc.add(2, 2) -> " + str(result))

    # Call set_val()
    result = rpc.set_val(2)
    print("rpc.set_val(2) -> " + str(result))

    # Call get_val()
    result = rpc.get_val()
    print("rpc.get_val() -> " + str(result))