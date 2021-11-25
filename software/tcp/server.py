#!/usr/bin/python

import socket

from tcp import tcp
from jsonrpc import JSONRPCResponseManager, dispatcher


@dispatcher.add_method
def echo(message):
    return message

@dispatcher.add_method
def mult(a, b):
    return a*b

def jsonrpc_handler(request):

    # JSON RPC Request Handler
    response = JSONRPCResponseManager.handle(request, dispatcher)

    # Print Request and Response
    print("--> " + str(request.decode()))
    print("<-- " + str(response.json) + "\n")

    return response.json




if __name__ == '__main__':    
    HOST = ''    # socket.gethostname()
    PORT = 4000
    
    # Create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to a public host and port
    s.bind((HOST, PORT))
    
    # Start server socket
    s.listen(1)
    
    while True:
        # Accept connections
        conn, addr = s.accept()

        t = tcp(conn)

        print("Accept new connection from " + str(addr[0]))
        
        # Receive data
        while True:
    
            data = t.recv()

            if not data:
                break

            # Call JSON RPC Handler
            response = jsonrpc_handler(data)

            # Transmit Response to Client
            t.send(response.encode('utf-8'))

        t.close()
        print("Close connection.")
    