import tkinter as tk
from tkinter import ttk
import asyncio
import aiohttp
import json
from datetime import datetime

class ComputerNodeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("vAIn Computer Node")
        
        # Main frame
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status display
        self.status_var = tk.StringVar(value="Status: Idle")
        ttk.Label(self.frame, textvariable=self.status_var).grid(row=0, column=0, pady=5)
        
        # Control buttons
        ttk.Button(self.frame, text="Start Training", command=self.start_training).grid(row=1, column=0, pady=5)
        ttk.Button(self.frame, text="Stop", command=self.stop_training).grid(row=2, column=0, pady=5)
        
        # Log display
        self.log_text = tk.Text(self.frame, height=10, width=50)
        self.log_text.grid(row=3, column=0, pady=5)
        
        self.is_running = False

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def start_training(self):
        if not self.is_running:
            self.is_running = True
            self.status_var.set("Status: Training")
            self.log("Started training process")
            asyncio.run(self.training_loop())

    def stop_training(self):
        if self.is_running:
            self.is_running = False
            self.status_var.set("Status: Stopped")
            self.log("Stopped training process")

    async def training_loop(self):
        async with aiohttp.ClientSession() as session:
            while self.is_running:
                try:
                    async with session.get('http://localhost:8000/federated/global_model') as response:
                        if response.status == 200:
                            self.log("Successfully retrieved global model")
                except Exception as e:
                    self.log(f"Error: {str(e)}")
                await asyncio.sleep(10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComputerNodeGUI(root)
    root.mainloop()
