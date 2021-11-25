import json

from tcp import tcp

class rpc:
   
    def __init__(self, host='localhost', port=4000):
        self.t = tcp()
        self.t.connect(host, port)

    def call(self, request):
        # JSON dump
        req = json.dumps(request)

        # Send data
        self.t.send(req.encode('utf-8'))

        # Receive data
        resp = self.t.recv()

        # Return response
        return json.loads(resp)

    def close(self):
        self.t.close()

    def __exit__(self):
        self.t.close()