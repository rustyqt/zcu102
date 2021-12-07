#!/usr/bin/python

from jsonrpc_pyclient.connectors import socketclient
from clientstub import clientstub
    
if __name__ == '__main__':    

    # Create TCP Socket Client
    connector = socketclient.TcpSocketClient("127.0.0.1", 4000)
    
    # Create RPC client
    client = clientstub(connector)

    # Call echo()    
    result = client.echo("Hello RPC!")
    print(result)

    # Call mult()
    result = client.mult(4, 2)
    print(result)

    # Call add()
    result = client.add(2, 2)
    print(result)

    # Call set_val()
    result = client.set_val(2)
    print(result)

    # Call get_val()
    result = client.get_val()
    print(result)