# tests/test_file_transfer.py
import pytest
import os
from network.file_transfer import FileTransfer
from network.server import FileReceiver

@pytest.fixture
def setup_file_transfer():
    # Configurações antes do teste
    file_receiver = FileReceiver()
    file_receiver.start_in_thread()  # Inicia o servidor em um thread
    file_transfer = FileTransfer()
    return file_transfer, file_receiver

def test_send_and_receive_file(setup_file_transfer):
    # Usando o fixture para setup
    file_transfer, file_receiver = setup_file_transfer
    
    # Caminho de um arquivo de teste
    test_file = "test.txt"
    with open(test_file, "w") as f:
        f.write("Este é um arquivo de teste.")
    
    # Enviar o arquivo
    try:
        response = file_transfer.send_file(test_file)
        assert response == "Arquivo recebido com sucesso!"
    except Exception as e:
        pytest.fail(f"Erro ao enviar arquivo: {e}")

    # Verificar se o arquivo foi recebido
    received_file = os.path.join("received_files", "test.txt")
    assert os.path.exists(received_file), f"O arquivo {received_file} não foi recebido."

    # Limpar arquivos após o teste
    if os.path.exists(received_file):
        os.remove(received_file)
    if os.path.exists(test_file):
        os.remove(test_file)

