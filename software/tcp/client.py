#!/usr/bin/python

import socket
import json

def create_socket(HOST='localhost', PORT=4000):

    # Create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    s.connect((HOST, PORT))

    # Return socket
    return s

def send(socket, request):
    # JSON dump
    req = json.dumps(request)

    # Send data
    s.sendall(req.encode('utf-8'))

    # Receive data
    resp = s.recv(2048)

    # Return response
    return json.loads(resp)



if __name__ == '__main__':    

    # Create socket
    s = create_socket()

    # Create JSON request
    req = {
        "method": "echo",
        "params": ["Hello World!"],
        "id": 0
    }

    resp = send(s, req)

    print(req)
    print(resp)

    # Call echo method
    req = {
        "method": "mult",
        "params": [12, 4],
        "id": 1
    }

    resp = send(s, req)

    print(req)
    print(resp)