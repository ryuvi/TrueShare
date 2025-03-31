import socket
import threading
import json
from typing import Set, Dict, Optional

class DeviceDiscovery:
    def __init__(self, multicast_group: str = "239.255.255.250", port: int = 1900):
        self.multicast_group = multicast_group
        self.port = port
        self.devices: Set[str] = set()
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        
        # Adiciona o socket ao grupo multicast
        mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def start_listening(self) -> None:
        """Inicia a escuta por dispositivos na rede"""
        if self.running:
            return
            
        self.running = True
        def listen():
            while self.running:
                try:
                    data, _ = self.sock.recvfrom(4096)
                    device_info = json.loads(data.decode())
                    
                    if device_info.get("service") == "file_transfer":
                        device_str = f"{device_info['hostname']} ({device_info['ip']})"
                        if device_str not in self.devices:
                            self.devices.add(device_str)
                            print(f"Dispositivo encontrado: {device_str}")
                except Exception as e:
                    print(f"Erro na descoberta: {e}")

        self.thread = threading.Thread(target=listen, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Para a escuta por dispositivos"""
        self.running = False
        self.sock.close()