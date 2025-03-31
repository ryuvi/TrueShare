import zmq
import os
from typing import Optional

class FileTransfer:
    def __init__(self, port: int = 5555):
        self.port = port
        self.context = zmq.Context()
        
    def send_file(self, file_path: str, destination_ip: str) -> str:
        """Envia um arquivo para o dispositivo de destino"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        socket = self.context.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)  # Não manter conexão após close
        socket.connect(f"tcp://{destination_ip}:{self.port}")

        try:
            # Enviar metadados
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            metadata = {
                "file_name": file_name,
                "file_size": file_size
            }
            socket.send_json(metadata)
            
            # Aguardar confirmação
            response = socket.recv_string()
            if response != "READY":
                raise Exception("Destino não está pronto para receber o arquivo")

            # Enviar arquivo em chunks
            with open(file_path, "rb") as file:
                total_sent = 0
                while total_sent < file_size:
                    chunk = file.read(4096)
                    socket.send(chunk, zmq.SNDMORE if (total_sent + len(chunk)) < file_size else 0)
                    total_sent += len(chunk)

            # Receber confirmação final
            return socket.recv_string()
        except Exception as e:
            raise Exception(f"Falha no envio do arquivo: {str(e)}")
        finally:
            socket.close()

    def close(self) -> None:
        """Libera recursos"""
        self.context.term()