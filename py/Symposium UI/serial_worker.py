from PyQt5.QtCore import QThread, pyqtSignal
from serial_communicator import SerialCommunicator
from commands_list import Command

class SerialWorker(QThread):
    data_received = pyqtSignal(object, object)

    def __init__(self, arduino_serial: SerialCommunicator):
        super().__init__()
        self.arduino_serial = arduino_serial
        self.running = True

    def run(self):
        while self.running:
            command, value = self.arduino_serial.receive_response()
            if command is not None:
                # Emit the data_received signal with the command and value
                # print(f"Received command: {command}, value: {value}")
                self.data_received.emit(command, value)
            # self.msleep(50)  # Sleep a bit before the next read to prevent CPU hogging

    def stop(self):
        self.running = False
        self.wait()  # Wait for the thread to finish before exiting

if __name__ == "__main__":
    worker = SerialWorker()
