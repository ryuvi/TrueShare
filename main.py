import sys
from PySide6.QtWidgets import (QApplication, QComboBox, QVBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QLineEdit)
from PySide6.QtCore import QTimer, Signal, QObject, Qt
from network.file_transfer import FileTransfer
from network.server import FileReceiver
from network.discovery import DeviceDiscovery
from network.announcer import DeviceAnnouncer
import socket

class FileTransferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Transfer App")
        self.setGeometry(100, 100, 600, 400)
        
        # Configuração de rede
        self.local_ip = self.get_local_ip()
        self.hostname = socket.gethostname()
        
        # Componentes de rede
        self.file_transfer = FileTransfer()
        self.file_receiver = FileReceiver()
        self.file_receiver.start_in_thread()
        
        self.device_discovery = DeviceDiscovery()
        self.device_discovery.start_listening()
        
        self.device_announcer = DeviceAnnouncer()
        self.device_announcer.start_announcing()
        
        # Configuração da UI
        self.init_ui()
        
        # Atualizar lista de dispositivos a cada 3 segundos
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_device_list)
        self.update_timer.start(3000)
        
    def get_local_ip(self) -> str:
        """Obtém o IP local da máquina"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def init_ui(self):
        """Configura a interface do usuário"""
        layout = QVBoxLayout()
        
        # Informações do dispositivo local
        self.device_info = QLabel(f"Você: {self.hostname} ({self.local_ip})")
        layout.addWidget(self.device_info)
        
        # Seletor de dispositivos
        self.device_label = QLabel("Dispositivos disponíveis:")
        self.device_selector = QComboBox()
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_selector)
        
        # Seleção de arquivo
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.select_file_btn = QPushButton("Selecionar Arquivo")
        self.select_file_btn.clicked.connect(self.select_file)
        layout.addWidget(self.file_path_input)
        layout.addWidget(self.select_file_btn)
        
        # Botão de envio
        self.send_btn = QPushButton("Enviar Arquivo")
        self.send_btn.clicked.connect(self.send_file)
        layout.addWidget(self.send_btn)
        
        # Área de status
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)
        
        # Configurar widget central
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def select_file(self):
        """Abre diálogo para seleção de arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo")
        if file_path:
            self.file_path_input.setText(file_path)
            self.log_status(f"Arquivo selecionado: {file_path}")
    
    def send_file(self):
        """Envia o arquivo para o dispositivo selecionado"""
        file_path = self.file_path_input.text()
        if not file_path:
            self.log_status("Erro: Nenhum arquivo selecionado")
            return
            
        selected_device = self.device_selector.currentText()
        if not selected_device:
            self.log_status("Erro: Nenhum dispositivo selecionado")
            return
            
        try:
            # Extrai o IP do dispositivo selecionado
            ip = selected_device.split("(")[-1].rstrip(")")
            
            self.log_status(f"Enviando arquivo para {selected_device}...")
            QApplication.processEvents()  # Atualiza a UI
            
            response = self.file_transfer.send_file(file_path, ip)
            self.log_status(f"Sucesso: {response}")
            
        except Exception as e:
            self.log_status(f"Erro ao enviar arquivo: {str(e)}")
    
    def update_device_list(self):
        """Atualiza a lista de dispositivos disponíveis"""
        current_selection = self.device_selector.currentText()
        self.device_selector.clear()
        
        for device in sorted(self.device_discovery.devices):
            self.device_selector.addItem(device)
            
            # Restaura a seleção anterior se ainda existir
            if device == current_selection:
                self.device_selector.setCurrentText(device)
    
    def log_status(self, message: str):
        """Adiciona uma mensagem ao log de status"""
        self.status_display.append(message)
        self.status_display.ensureCursorVisible()
    
    def closeEvent(self, event):
        """Garante que todos os recursos sejam liberados ao fechar"""
        self.device_announcer.stop()
        self.device_discovery.stop()
        self.file_receiver.stop()
        self.file_transfer.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTransferApp()
    window.show()
    sys.exit(app.exec())