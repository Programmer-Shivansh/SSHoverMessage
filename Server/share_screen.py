import socket
import struct
import tkinter as tk
from PIL import ImageTk, Image
import io
import json
import threading

class RemoteScreenClient:
    def __init__(self, relay_host, relay_port=5000):
        self.root = tk.Tk()
        self.root.title("Remote Screen Client (Controller)")
        
        # Create canvas
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Connect to relay
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((relay_host, relay_port))
        self.socket.send("VIEWER".encode())
        
        # Bind mouse events
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        # Bind keyboard events
        self.root.bind("<Key>", self.on_key)
        
        # Track screen size
        self.screen_width = 1024
        self.screen_height = 768
        
    def send_command(self, command):
        try:
            self.socket.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Error sending command: {e}")
    
    def on_mouse_move(self, event):
        # Convert coordinates
        x = int((event.x / self.canvas.winfo_width()) * self.screen_width)
        y = int((event.y / self.canvas.winfo_height()) * self.screen_height)
        
        command = {
            'type': 'MOUSE_MOVE',
            'x': x,
            'y': y
        }
        self.send_command(command)
    
    def on_left_click(self, event):
        command = {
            'type': 'MOUSE_CLICK',
            'button': 'left'
        }
        self.send_command(command)
    
    def on_right_click(self, event):
        command = {
            'type': 'MOUSE_CLICK',
            'button': 'right'
        }
        self.send_command(command)
    
    def on_key(self, event):
        if len(event.char) > 0:
            command = {
                'type': 'TYPE',
                'text': event.char
            }
        else:
            command = {
                'type': 'KEY',
                'key': event.keysym
            }
        self.send_command(command)
    
    def receive_forever(self):
        try:
            while True:
                size_data = self.socket.recv(4)
                if not size_data:
                    break
                    
                size = struct.unpack('>I', size_data)[0]
                
                img_data = b''
                while len(img_data) < size:
                    chunk = self.socket.recv(min(8192, size - len(img_data)))
                    if not chunk:
                        raise ConnectionError("Connection lost")
                    img_data += chunk
                
                img = ImageTk.PhotoImage(Image.open(io.BytesIO(img_data)))
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                # self.canvas.image = img
                
                self.root.update()
                
        except Exception as e:
            print(f"Error receiving: {e}")
        finally:
            self.socket.close()
    
    def run(self):
        receive_thread = threading.Thread(target=self.receive_forever)
        receive_thread.daemon = True
        receive_thread.start()
        self.root.mainloop()

if __name__ == "__main__":
    RELAY_SERVER = "your_relay_server_ip"
    client = RemoteScreenClient(RELAY_SERVER)
    client.run()