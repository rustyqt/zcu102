import socket

class tcp:
   
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host='localhost', port=4000):
        return self.sock.connect((host, port))
    
    def send(self, msg):
        # Send all and add termination character
        self.sock.sendall(msg + b'\n')

    def recv(self):
        msg = b''
        while True:
            # Receive chunk
            chunk = self.sock.recv(2048)
            if not chunk: 
                return b''

            # Concat chunks to message
            msg += chunk

            if msg[-1] == 10:    # Check for '\n' (=10)
                return msg[0:-1]

    def close(self):
        self.sock.close()

    def __exit__(self):
        self.sock.close()