import tkinter as tk
from PIL import ImageTk, Image, ImageGrab
import socket
import struct
import io
import threading
import time
import pyautogui
import json

class RemoteScreenViewer:
    def __init__(self, relay_host, relay_port=5000):
        self.root = tk.Tk()
        self.root.title("Remote Screen Viewer (Controlled)")
        
        # Create canvas for displaying the screen
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize network settings
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((relay_host, relay_port))
        self.socket.send("STREAMER".encode())
        
        # Command handling thread
        self.command_thread = threading.Thread(target=self.handle_commands)
        self.command_thread.daemon = True
        self.command_thread.start()
        
        # Screen streaming thread
        self.running = True
        self.stream_thread = threading.Thread(target=self.stream_screen)
        self.stream_thread.daemon = True
        self.stream_thread.start()
        
    def handle_commands(self):
        while self.running:
            try:
                command_data = self.socket.recv(1024)
                if not command_data:
                    break
                    
                command = json.loads(command_data.decode())
                
                if command['type'] == 'MOUSE_MOVE':
                    pyautogui.moveTo(command['x'], command['y'])
                elif command['type'] == 'MOUSE_CLICK':
                    pyautogui.click(button=command['button'])
                elif command['type'] == 'KEY':
                    pyautogui.press(command['key'])
                elif command['type'] == 'TYPE':
                    pyautogui.write(command['text'])
                    
            except Exception as e:
                print(f"Error handling command: {e}")
                break
    
    def stream_screen(self):
        while self.running:
            try:
                screenshot = ImageGrab.grab()
                img_byte_arr = io.BytesIO()
                screenshot = screenshot.resize((1024, 768))
                screenshot.save(img_byte_arr, format='JPEG', quality=70)
                img_byte_arr = img_byte_arr.getvalue()
                
                size = len(img_byte_arr)
                self.socket.send(struct.pack('>I', size))
                self.socket.send(img_byte_arr)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error streaming: {e}")
                break
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.running = False
            self.socket.close()

if __name__ == "__main__":
    RELAY_SERVER = "your_relay_server_ip"
    viewer = RemoteScreenViewer(RELAY_SERVER)
    viewer.run()