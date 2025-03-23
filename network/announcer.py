# network/announcer.py
import zmq
import threading
import time
import socket
import random

class DeviceAnnouncer:
    def __init__(self, discovery_port=None):
        self.discovery_port = discovery_port or random.randint(5000,6000)
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://0.0.0.0:{self.discovery_port}")  # Mudança de connect para bind

    def get_device_identity(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return f"{hostname} ({ip})"

    def start_announcing(self):
        def announce():
            while True:
                identity = self.get_device_identity()
                self.publisher.send_string(identity)
                time.sleep(3)

        thread = threading.Thread(target=announce, daemon=True)
        thread.start()

