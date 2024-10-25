import socket
import struct
import tkinter as tk
from PIL import ImageTk, Image
import io

class ScreenClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Client")
        
        # Create canvas for displaying the screen
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Connect to server
        self.client_socket = socket.socket()
        self.client_socket.connect(('localhost', 5003))
        
    def receive_forever(self):
        try:
            while True:
                # Receive size of incoming image
                size_data = self.client_socket.recv(4)
                size = struct.unpack('>I', size_data)[0]
                
                # Receive image data
                img_data = b''
                while len(img_data) < size:
                    chunk = self.client_socket.recv(size - len(img_data))
                    if not chunk:
                        raise ConnectionError("Connection lost")
                    img_data += chunk
                
                # Display image
                img = ImageTk.PhotoImage(Image.open(io.BytesIO(img_data)))
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                # self.canvas.image = img
                
                self.root.update()
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()
    
    def run(self):
        self.receive_forever()

if __name__ == "__main__":
    client = ScreenClient()
    client.run()