import zmq
import threading
import os
from typing import Optional

class FileReceiver:
    def __init__(self, host: str = "0.0.0.0", port: int = 5555):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://{self.host}:{self.port}")
        self.running = False

    def start(self) -> None:
        """Inicia o servidor para receber arquivos"""
        self.running = True
        print(f"Servidor de arquivos ouvindo em {self.host}:{self.port}...")
        
        while self.running:
            try:
                # Receber metadados
                metadata = self.socket.recv_json()
                file_name = metadata["file_name"]
                file_size = metadata["file_size"]
                
                # Confirmar recebimento dos metadados
                self.socket.send_string("READY")
                
                # Preparar para receber o arquivo
                save_dir = "received_files"
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, file_name)
                
                # Receber arquivo em chunks
                with open(save_path, "wb") as file:
                    received = 0
                    while received < file_size:
                        chunk = self.socket.recv()
                        file.write(chunk)
                        received += len(chunk)
                
                # Confirmar recebimento
                self.socket.send_string(f"Arquivo {file_name} recebido com sucesso!")
                print(f"Arquivo recebido: {save_path}")
                
            except zmq.ZMQError as e:
                if self.running:
                    print(f"Erro no servidor: {e}")
            except Exception as e:
                print(f"Erro ao processar arquivo: {e}")
                self.socket.send_string(f"Erro: {str(e)}")

    def start_in_thread(self) -> None:
        """Inicia o servidor em uma thread separada"""
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Para o servidor"""
        self.running = False
        self.socket.close()
        self.context.term()