import socket
import threading
import time
import json
from typing import Optional

class DeviceAnnouncer:
    def __init__(self, multicast_group: str = "239.255.255.250", port: int = 1900):
        self.multicast_group = multicast_group
        self.port = port
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
    def get_local_ip(self) -> str:
        """Obtém o IP real da interface de rede"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def get_device_info(self) -> dict:
        """Retorna informações do dispositivo para anúncio"""
        return {
            "hostname": socket.gethostname(),
            "ip": self.get_local_ip(),
            "service": "file_transfer",
            "port": 5555  # Porta padrão para transferência de arquivos
        }

    def start_announcing(self) -> None:
        """Inicia o anúncio periódico do dispositivo"""
        if self.running:
            return
            
        self.running = True
        def announce():
            while self.running:
                try:
                    device_info = self.get_device_info()
                    self.sock.sendto(
                        json.dumps(device_info).encode(),
                        (self.multicast_group, self.port)
                    )
                except Exception as e:
                    print(f"Erro no anúncio: {e}")
                time.sleep(3)

        self.thread = threading.Thread(target=announce, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Para o anúncio do dispositivo"""
        self.running = False
        self.sock.close()