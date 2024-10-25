import tkinter as tk
from PIL import ImageTk, Image, ImageGrab
import socket
import struct
import io
import threading
import time

class ScreenViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Viewer")
        
        # Create canvas for displaying the screen
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize network settings
        self.server_socket = socket.socket()
        self.server_socket.bind(('localhost', 5003))
        self.server_socket.listen(1)
        
        # Start the server threa3
        self.running = True
        self.server_thread = threading.Thread(target=self.serve_forever)
        self.server_thread.start()
        
    def serve_forever(self):
        print("Waiting for connection...")
        conn, addr = self.server_socket.accept()
        print(f"Connected to {addr}")
        
        try:
            while self.running:
                # Capture screen
                screenshot = ImageGrab.grab()
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                screenshot = screenshot.resize((800, 600))  # Resize for performance
                screenshot.save(img_byte_arr, format='PNG', optimize=True)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Send size followed by data
                size = len(img_byte_arr)
                conn.send(struct.pack('>I', size))
                conn.send(img_byte_arr)
                
                # Update GUI
                img = ImageTk.PhotoImage(Image.open(io.BytesIO(img_byte_arr)))
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                # self.canvas.image = img
                
                time.sleep(0.1)  # Limit frame rate
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.running = False
            self.server_socket.close()

if __name__ == "__main__":
    viewer = ScreenViewer()
    viewer.run()