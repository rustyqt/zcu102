#!/usr/bin/python

import socket
import tcp

from jsonrpc import JSONRPCResponseManager, dispatcher     

class myclass():
    def __init__(self, value):
        self.value = value

    def set_val(self, value):
        self.value = value

    def get_val(self):
        return self.value


@dispatcher.add_method
def set_val(value):
    global c
    c.set_val(value)

@dispatcher.add_method
def get_val():
    global c
    return c.get_val()

@dispatcher.add_method
def echo(message):
    return message

@dispatcher.add_method
def mult(a, b):
    return a*b


# RPC Handler
def handle(request):

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

    #Init
    c = myclass(5)

    while True:
        # Accept connections
        conn, addr = s.accept()

        t = tcp.tcp(conn)

        print("Accept new connection from " + str(addr[0]))
        
        # Receive data
        while True:
    
            data = t.recv()

            if not data:
                break

            # Call JSON RPC Handler
            response = handle(data)

            # Transmit Response to Client
            t.send(response.encode('utf-8'))

        t.close()
        print("Close connection.")
    