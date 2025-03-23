# main.py
import sys
from PySide6.QtWidgets import QApplication, QComboBox
from PySide6.QtCore import QTimer
from gui.main_window import MainWindow
from network.file_transfer import FileTransfer
from network.server import FileReceiver
from network.discovery import DeviceDiscovery
from network.announcer import DeviceAnnouncer

class FileTransferApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.file_transfer = FileTransfer()
        self.file_receiver = FileReceiver()
        self.file_receiver.start_in_thread()

        self.device_discovery = DeviceDiscovery()
        self.device_discovery.start_listening()

        self.device_announcer = DeviceAnnouncer()
        self.device_announcer.start_announcing()

        self.device_selector = QComboBox()
        self.centralWidget().layout().insertWidget(2, self.device_selector)

        # Atualizar lista de dispositivos a cada 3 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start(3000)  # 3000 ms = 3 segundos

    def refresh_devices(self):
        self.device_selector.clear()
        for device in self.device_discovery.devices:
            self.device_selector.addItem(device)


    def send_file(self):
        selected_device = self.device_selector.currentText()
        if not selected_device:
            self.status_label.setText("Status: Nenhum dispositivo selecionado.")
            return

        file_path = self.file_path_input.text()
        if file_path:
            try:
                # Extraindo o IP do nome do dispositivo (exemplo: "PC1 (192.168.1.100)")
                ip = selected_device.split("(")[-1].strip(")")

                response = self.file_transfer.send_file(file_path, ip)
                self.status_label.setText(f"Status: {response}")
            except Exception as e:
                self.status_label.setText(f"Status: Erro - {str(e)}")
        else:
            self.status_label.setText("Status: Nenhum arquivo selecionado.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTransferApp()
    window.show()
    sys.exit(app.exec())
