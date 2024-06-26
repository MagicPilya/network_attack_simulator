import tkinter as tk
from tkinter import ttk
from attack import NetworkAttackSimulator
from logger import setup_logger
import os

LOG_DIR = 'logs/'
LOG_NAME = 'network_attack.log'
CONFIG_FILE = 'config.txt'

class AttackSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Attack Simulator")
        
        self.logger = setup_logger(LOG_DIR, LOG_NAME)
        
        self.attack_type_label = tk.Label(root, text="Select Attack Type:")
        self.attack_type_label.pack()
        
        self.attack_type = tk.StringVar()
        self.attack_type_combobox = ttk.Combobox(root, textvariable=self.attack_type)
        self.attack_type_combobox['values'] = ('SYN Flood', 'ICMP Flood', 'HTTP Flood')
        self.attack_type_combobox.current(0)
        self.attack_type_combobox.pack()

        self.target_label = tk.Label(root, text="Target IP or URL:")
        self.target_label.pack()
        
        self.target_entry = tk.Entry(root)
        self.target_entry.pack()

        self.intensity_label = tk.Label(root, text="Intensity (requests per second):")
        self.intensity_label.pack()
        
        self.intensity_scale = tk.Scale(root, from_=1, to=1000, orient='horizontal')
        self.intensity_scale.pack()

        self.start_button = tk.Button(root, text="Start Attack", command=self.start_attack)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Attack", command=self.stop_attack, state=tk.DISABLED)
        self.stop_button.pack()

        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack()

        self.packet_count_label = tk.Label(root, text="Packets Sent: 0")
        self.packet_count_label.pack()

        self.last_target_ip = self.load_last_target_ip()
        self.target_entry.insert(0, self.last_target_ip)

        self.simulator = None
        self.attack_threads = []

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.update_packet_count()

    def start_attack(self):
        attack_type = self.attack_type.get()
        target = self.target_entry.get()
        intensity = self.intensity_scale.get()

        if not target:
            self.logger.error("Target IP or URL is empty")
            return

        if target != self.last_target_ip:
            self.last_target_ip = target
            self.save_last_target_ip(target)

        self.simulator = NetworkAttackSimulator(target, self.logger)

        threads = None  # Initialize threads variable
        if attack_type == 'SYN Flood':
            threads = self.simulator.perform_syn_flood(intensity)
        elif attack_type == 'ICMP Flood':
            threads = self.simulator.perform_icmp_flood(intensity)
        elif attack_type == 'HTTP Flood':
            self.simulator.perform_http_flood_async(intensity)

        if threads or attack_type == 'HTTP Flood':
            self.status_label.config(text="Status: Attacking")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_attack(self):
        if self.simulator:
            self.simulator.stop_attack()
            self.status_label.config(text="Status: Idle")
            self.packet_count_label.config(text="Packets Sent: 0")
            self.attack_threads = []
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def load_last_target_ip(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def save_last_target_ip(self, ip):
        with open(CONFIG_FILE, 'w') as f:
            f.write(ip)

    def update_packet_count(self):
        if self.simulator and self.simulator.attacking:
            self.packet_count_label.config(text=f"Packets Sent: {self.simulator.packet_count}")
        self.root.after(1000, self.update_packet_count)

    def on_closing(self):
        log_file = os.path.join(LOG_DIR, LOG_NAME)
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.truncate(0)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AttackSimulatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
