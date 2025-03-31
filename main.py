# main.py
import sys
from PySide6.QtWidgets import QApplication, QComboBox, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Signal, QObject
from gui.main_window import MainWindow
from network.file_transfer import FileTransfer
from network.server import FileReceiver
from network.discovery import DeviceDiscovery
from network.announcer import DeviceAnnouncer
import pika  # RabbitMQ client library
import json
from threading import Thread

class MessageHandler(QObject):
    message_received = Signal(str, str)  # sender, message

class FileTransferApp(MainWindow):
    def __init__(self):
        super().__init__()
        # Initialize file transfer components
        self.file_transfer = FileTransfer()
        self.file_receiver = FileReceiver()
        self.file_receiver.start_in_thread()

        # Device discovery setup
        self.device_discovery = DeviceDiscovery()
        self.device_discovery.start_listening()

        self.device_announcer = DeviceAnnouncer()
        self.device_announcer.start_announcing()

        # Messaging setup
        self.message_handler = MessageHandler()
        self.message_handler.message_received.connect(self.display_message)
        self.setup_messaging()

        # UI enhancements for messaging
        self.setup_messaging_ui()

        # Device selector
        self.device_selector = QComboBox()
        self.centralWidget().layout().insertWidget(2, self.device_selector)

        # Message input and send button would be added in setup_messaging_ui

        # Update device list every 3 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start(3000)

    def setup_messaging_ui(self):
        layout = self.centralWidget().layout()
        
        # Add messaging components
        self.message_label = QLabel("Messages:")
        layout.addWidget(self.message_label)
        
        self.message_display = QLabel()
        self.message_display.setWordWrap(True)
        layout.addWidget(self.message_display)
        
        # You would add message input and send button here
        # For simplicity, I'm showing the structure

    def setup_messaging(self):
        """Initialize connection to message broker"""
        try:
            # Connect to RabbitMQ (replace with your broker details)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            
            # Declare an exchange (you might use direct or topic exchange)
            self.channel.exchange_declare(exchange='file_transfer', 
                                         exchange_type='topic')
            
            # Create a queue for this client
            result = self.channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            # Bind to the exchange with a routing key pattern
            self.channel.queue_bind(exchange='file_transfer',
                                  queue=queue_name,
                                  routing_key='message.*')
            
            # Start consuming messages in a separate thread
            self.consumer_thread = Thread(target=self.start_consuming, 
                                        args=(queue_name,))
            self.consumer_thread.daemon = True
            self.consumer_thread.start()
            
        except Exception as e:
            print(f"Failed to connect to message broker: {e}")

    def start_consuming(self, queue_name):
        """Start consuming messages from the queue"""
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.on_message_received,
            auto_ack=True)
        self.channel.start_consuming()

    def on_message_received(self, ch, method, properties, body):
        """Callback when a message is received"""
        try:
            message = json.loads(body)
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            
            # Emit signal to update UI from main thread
            self.message_handler.message_received.emit(sender, content)
        except Exception as e:
            print(f"Error processing message: {e}")

    def display_message(self, sender, message):
        """Display received message in UI"""
        current = self.message_display.text()
        new_message = f"{sender}: {message}\n{current}"
        self.message_display.setText(new_message[:500])  # Limit message length

    def send_message(self, message):
        """Send a message to selected device"""
        selected_device = self.device_selector.currentText()
        if not selected_device or not message:
            return
            
        try:
            # Extract IP from device name
            ip = selected_device.split("(")[-1].strip(")")
            
            # Create message payload
            payload = {
                'sender': self.device_announcer.device_name,
                'recipient': ip,
                'content': message
            }
            
            # Publish message to exchange
            self.channel.basic_publish(
                exchange='file_transfer',
                routing_key=f'message.{ip}',
                body=json.dumps(payload))
            
        except Exception as e:
            print(f"Error sending message: {e}")

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
                
                # Optionally send a notification message
                self.send_message(f"File {file_path.split('/')[-1]} sent successfully")
            except Exception as e:
                self.status_label.setText(f"Status: Erro - {str(e)}")
                self.send_message(f"Error sending file: {str(e)}")
        else:
            self.status_label.setText("Status: Nenhum arquivo selecionado.")

    def closeEvent(self, event):
        """Clean up resources when closing"""
        try:
            if hasattr(self, 'connection') and self.connection.is_open:
                self.connection.close()
        except Exception as e:
            print(f"Error closing message broker connection: {e}")
        
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTransferApp()
    window.show()
    sys.exit(app.exec())