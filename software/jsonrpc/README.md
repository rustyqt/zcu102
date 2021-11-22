## JSON-RPC Response Handler

### Start Server

    ./server.py


### Start Client

    ./client.py 
    --> {'method': 'echo', 'params': ['Hello World!'], 'id': 0}
    <-- {'result': 'Hello World!', 'id': 0}
    --> {'method': 'mult', 'params': [4096, 2], 'id': 1}
    <-- {'result': 8192, 'id': 1}




