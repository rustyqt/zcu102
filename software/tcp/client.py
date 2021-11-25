#!/usr/bin/python

from rpc import rpc

if __name__ == '__main__':    

    # Create socket
    r = rpc()

    # Create JSON request
    req = {
        "method": "echo",
        "params": ["Hello World!"],
        "id": 0
    }

    resp = r.call(req)

    print(req)
    print(resp)

    # Create JSON request
    req = {
        "method": "mult",
        "params": [12, 4],
        "id": 1
    }

    resp = r.call(req)

    print(req)
    print(resp)