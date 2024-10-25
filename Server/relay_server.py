import socket
import threading
import struct
import json

class RelayServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = {}
        print(f"Relay server started on port {port}")

    def handle_client(self, client_socket, addr):
        try:
            # First message identifies client type
            client_type = client_socket.recv(1024).decode()
            
            if client_type == "VIEWER":
                self.clients['viewer'] = client_socket
                print(f"Viewer connected from {addr}")
                
                # Handle control commands from viewer
                while True:
                    try:
                        command = client_socket.recv(1024)
                        if not command:
                            break
                        if 'streamer' in self.clients:
                            self.clients['streamer'].send(command)
                    except:
                        break
                
            elif client_type == "STREAMER":
                self.clients['streamer'] = client_socket
                print(f"Streamer connected from {addr}")
                
                # Forward streamer's screen data to viewer
                while True:
                    try:
                        size_data = client_socket.recv(4)
                        if not size_data:
                            break
                            
                        size = struct.unpack('>I', size_data)[0]
                        
                        if 'viewer' in self.clients:
                            self.clients['viewer'].send(size_data)
                            
                            remaining = size
                            while remaining > 0:
                                chunk = client_socket.recv(min(remaining, 8192))
                                if not chunk:
                                    break
                                self.clients['viewer'].send(chunk)
                                remaining -= len(chunk)
                                
                    except:
                        break
                        
        finally:
            for key in list(self.clients.keys()):
                if self.clients[key] == client_socket:
                    del self.clients[key]
            client_socket.close()

    def run(self):
        while True:
            client_socket, addr = self.server.accept()
            client_handler = threading.Thread(
                target=self.handle_client,
                args=(client_socket, addr)
            )
            client_handler.start()

if __name__ == "__main__":
    relay = RelayServer()
    relay.run()