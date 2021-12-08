#!/usr/bin/python

import inspect

import socket
import tcp

import json
from jsonrpc import JSONRPCResponseManager, dispatcher     

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
    c = myclass()

    dispatcher.build_method_map(c)

    print("RPC Procedures:")
    spec = []
    for procedure in dispatcher:
        # Get Signature
        sig = inspect.signature(dispatcher[procedure])
        print(procedure + str(sig))
        
        # Get Parameters
        params = {}
        for param in sig.parameters.values():
            params[param.name] = param.annotation()

        # Get Return Annotation
        return_type = sig.return_annotation()

        # Create Method
        method = {}
        method["name"] = procedure
        method["params"] = params
        method["returns"] = return_type
        
        # Append method to RPC spec
        spec.append(method)

    # Write spec to JSON file
    with open('../common/spec.json', 'w') as f:
        json.dump(spec, f, indent=4)


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
    