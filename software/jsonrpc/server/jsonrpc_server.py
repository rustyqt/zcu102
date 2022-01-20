#!/usr/bin/python

import inspect

import socket
import tcp

import json
from jsonrpc import JSONRPCResponseManager, dispatcher

class jsonrpc_server:
    def __init__(self, exposed_object=None, filename="../common/spec.json"):
        if exposed_object != None:
            self.add(exposed_object, filename)

    # RPC Handler
    def _handle(self, request):

        # JSON RPC Request Handler
        response = JSONRPCResponseManager.handle(request, dispatcher)
        
        # Print Request and Response
        print("--> " + request.decode())
        print("<-- " + response.json + "\n")

        return response.json

    def add(self, exposed_object, filename="../common/spec.json"):
        # Expose all public methods of provided object
        dispatcher.build_method_map(exposed_object, prefix=type(exposed_object).__name__ + "_")

        # Create spec for exposed methods
        self.spec = []
        for procedure in dispatcher:
            # Get Signature
            sig = inspect.signature(dispatcher[procedure])
            print(procedure + str(sig))
            
            # Get Parameters
            params = {}
            for param in sig.parameters.values():
                params[param.name] = param.annotation()
                
                is_int = params[param.name] == int()
                is_str = params[param.name] == str()
                is_bool = params[param.name] == bool()

                assert is_int or is_str or is_bool, "Param type hint not provided or invalid."

            # Get Return Annotation
            return_type = sig.return_annotation()
            
            is_int = return_type == int()
            is_str = return_type == str()
            is_bool = return_type == bool()

            assert is_int or is_str or is_bool, "Return type hint not provided or invalid."

            # Create Method
            method = {}
            method["name"] = procedure
            method["params"] = params
            method["returns"] = return_type
            
            print(method)
            # Append method to RPC spec
            self.spec.append(method)

        # Write spec to JSON file
        with open(filename, 'w') as f:
            json.dump(self.spec, f, indent=4)        



    def run(self):
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

            # Start socket for new connection
            print("Accept new connection from " + str(addr[0]))
            sock = tcp.tcp(conn)

            # Receive data
            while True:
        
                data = sock.recv()

                if not data:
                    break

                # Call JSON RPC Handler
                response = self._handle(data)

                # Transmit Response to Client
                sock.send(response.encode('utf-8'))

            sock.close()
            print("Close connection.")
