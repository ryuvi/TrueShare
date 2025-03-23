# gui/main_window.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget, QLabel, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Transfer App")
        self.setGeometry(100, 100, 400, 200)

        # Layout
        layout = QVBoxLayout()

        # Widgets
        self.label = QLabel("Selecione um arquivo para enviar")
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.select_file_button = QPushButton("Selecionar Arquivo")
        self.send_file_button = QPushButton("Enviar Arquivo")
        self.status_label = QLabel("Status: Aguardando...")

        # Conectar botões a funções
        self.select_file_button.clicked.connect(self.select_file)
        self.send_file_button.clicked.connect(self.send_file)

        # Adicionar widgets ao layout
        layout.addWidget(self.label)
        layout.addWidget(self.file_path_input)
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.send_file_button)
        layout.addWidget(self.status_label)

        # Definir layout central
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo")
        if file_path:
            self.file_path_input.setText(file_path)

    def send_file(self):
        file_path = self.file_path_input.text()
        if file_path:
            self.status_label.setText("Status: Enviando...")
            # Aqui você chamará a função de envio de arquivo via ZeroMQ
            print(f"Arquivo selecionado: {file_path}")
            self.status_label.setText("Status: Arquivo enviado!")
        else:
            self.status_label.setText("Status: Nenhum arquivo selecionado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())