# network/file_transfer.py
import zmq
import os

class FileTransfer:
    def __init__(self, port=5555):
        self.port = port
        self.context = zmq.Context()

    def send_file(self, file_path, destination_ip):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        file_name = os.path.basename(file_path)
        socket = self.context.socket(zmq.REQ)
        socket.connect(f"tcp://{destination_ip}:{self.port}")  # Conecta ao IP do destino

        try:
            # Enviar metadados
            socket.send_json({"file_name": file_name})
            response = socket.recv_string()

            if response != "ACK":
                raise Exception("Erro ao enviar metadados do arquivo")

            # Enviar o arquivo
            with open(file_path, "rb") as file:
                file_data = file.read()
            
            socket.send(file_data)

            # Receber confirmação final
            response = socket.recv_string()
            return response

        finally:
            socket.close()

    def close(self):
        self.context.term()
