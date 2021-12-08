## Python JSON-RPC Server and Client

### Folder Structure

    -> client
      -> jsonrpc_client.py
      -> gen_jsonrpc_client.sh
    -> common
      -> spec.json
    -> examples
      -> server.py
      -> client.py
    -> server 
      -> jsonrpc_server.py
      -> tcp.py

### Description

The jsonrpc\_server class exposes all public methods of a given class object to the JSON RPC interface. TCP is used as transport layer for the JSON RPC.

The jsonrpc\_server also creates the spec.json file which contains the RPC interface defintion. It is consumed by the gen\_jsonrpc\_client.sh script to generate the jsonrpc\_client.py.

An example application demonstrating the usage of the JSON RPC server and client is provided in the examples directory.


### Start Server
    cd examples/
    ./server.py


### Start Client
    cd examples/
    ./client.py 
