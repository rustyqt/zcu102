#!/usr/bin/python3

import requests
import json


def main():
    url = "http://localhost:4000/jsonrpc"

    # Call echo method
    payload = {
        "method": "echo",
        "params": ["Hello World!"],
        "id": 0
    }

    response = requests.post(url, json=payload).json()
    
    print("--> " + str(payload))
    print("<-- " + str(response))

    assert response["result"] == "Hello World!"
    assert response["id"] == 0


    # Call mult method
    payload = {
        "method": "mult",
        "params": [4096, 2],
        "id": 1
    }

    response = requests.post(url, json=payload).json()
    
    print("--> " + str(payload))
    print("<-- " + str(response))


if __name__ == "__main__":
    main()
