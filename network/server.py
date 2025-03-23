# network/server.py
import zmq
import threading
import os

class FileReceiver:
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://{self.host}:{self.port}")

    def start(self):
        print(f"Servidor ouvindo em {self.host}:{self.port}...")
        while True:
            try:
                # Receber metadados do arquivo
                metadata = self.socket.recv_json()
                file_name = metadata["file_name"]
                self.socket.send_string("ACK")  # Confirmação de metadados

                # Receber o arquivo
                file_data = self.socket.recv()
                save_path = os.path.join("received_files", file_name)
                os.makedirs("received_files", exist_ok=True)

                with open(save_path, "wb") as f:
                    f.write(file_data)

                print(f"Arquivo recebido: {save_path}")
                self.socket.send_string("Arquivo recebido com sucesso!")

            except Exception as e:
                print(f"Erro no servidor: {e}")

    def start_in_thread(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
