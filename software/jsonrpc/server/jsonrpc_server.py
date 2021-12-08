#!/usr/bin/python

import inspect

import socket
import tcp

import json
from jsonrpc import JSONRPCResponseManager, dispatcher

class jsonrpc_server:
    def __init__(self, exposed_object):

        # Expose all public methods of provided object
        dispatcher.build_method_map(exposed_object)

        # Create spec.json for exposed methods
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


    # RPC Handler
    def _handle(self, request):

        # JSON RPC Request Handler
        response = JSONRPCResponseManager.handle(request, dispatcher)

        # Print Request and Response
        print("--> " + str(request.decode()))
        print("<-- " + str(response.json) + "\n")

        return response.json

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
