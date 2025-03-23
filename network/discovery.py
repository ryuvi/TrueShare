# network/discovery.py
import zmq
import threading
import time
import random

class DeviceDiscovery:
    def __init__(self, discovery_port=None):
        self.discovery_port = discovery_port or random.randint(5000,6000)
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind(f"tcp://0.0.0.0:{self.discovery_port}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        self.devices = set()
        self.running = True

    def listen_for_devices(self):
        while self.running:
            try:
                message = self.subscriber.recv_string(flags=zmq.NOBLOCK)
                if message not in self.devices:
                    self.devices.add(message)
                    print(f"Novo dispositivo encontrado: {message}")
            except zmq.Again:
                time.sleep(1)  # Aguarda mensagens

    def start_listening(self):
        thread = threading.Thread(target=self.listen_for_devices, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        self.subscriber.close()
