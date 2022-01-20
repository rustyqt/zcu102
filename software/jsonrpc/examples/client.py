#!/usr/bin/python

import sys
sys.path.insert(0, '../client/')

from jsonrpc_pyclient.connectors import socketclient
from jsonrpc_example_client import jsonrpc_example_client
    
if __name__ == '__main__':    

    # Create TCP Socket Client
    connector = socketclient.TcpSocketClient("127.0.0.1", 4000)
    
    # Create RPC client
    rpc = jsonrpc_example_client(connector)

    # Use myclass methods
    result = rpc.myclass_echo("Hello RPC!")
    print("rpc.myclass_echo('Hello RPC!') -> " + str(result))

    result = rpc.myclass_mult(4, 2)
    print("rpc.myclass_mult(4, 2) -> " + str(result))

    result = rpc.myclass_add(2, 2)
    print("rpc.myclass_add(2, 2) -> " + str(result))

    result = rpc.myclass_set_val(2)
    print("rpc.myclass_set_val(2) -> " + str(result))

    result = rpc.myclass_get_val()
    print("rpc.myclass_get_val() -> " + str(result))

    # Use mytftp methods
    result = rpc.mytftp_get_ip()
    print("rpc.mytftp_get_ip() -> " + str(result))
    
    result = rpc.mytftp_set_ip("192.168.0.10")
    print("rpc.mytftp_set_ip() -> " + str(result))
    
    result = rpc.mytftp_get_ip()
    print("rpc.mytftp_get_ip() -> " + str(result))

    # Use myaes methods
    result = rpc.myaes_config(1234, 555)
    print("rpc.myaes_config() -> " + str(result))

    result = rpc.myaes_encrypt("pt", "ct")
    print("rpc.myaes_encrypt() -> " + str(result))
