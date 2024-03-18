from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtGui, QtCore
import sys
from serial_comms import GraphLauncher, PlotWindow
from arduino_comms import SerialCommunicator
from arduino_commands import Command

QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

class MyWindow(QWidget):
    def __init__(self, arduino_serial: SerialCommunicator):
        super().__init__()

        self.arduino_serial = arduino_serial
        self.p = 1
        self.i = 1
        self.d = 1
        self.plot_windows = []

        # Create widgets
        self.label_p = QLabel("P:")
        self.label_p.setStyleSheet("font-size: 30px")  # Increase font size
        self.textbox_p = QLineEdit()
        self.textbox_p.setStyleSheet("font-size: 30px")  # Increase font size
        self.textbox_p.setMinimumSize(200, 50)  # Increase text box size
        self.label_i = QLabel("I:")
        self.label_i.setStyleSheet("font-size: 30px")  # Increase font size
        self.textbox_i = QLineEdit()
        self.textbox_i.setStyleSheet("font-size: 30px")  # Increase font size
        self.textbox_i.setMinimumSize(200, 50)  # Increase text box size
        self.label_d = QLabel("D:")
        self.label_d.setStyleSheet("font-size: 30px")  # Increase font size
        self.textbox_d = QLineEdit()
        self.textbox_d.setStyleSheet("font-size: 30px")  # Increase font size
        self.textbox_d.setMinimumSize(200, 50)  # Increase text box size
        self.start_button = QPushButton("Start & Plot")
        self.start_button.setStyleSheet("font-size: 30px")  # Increase font size

        # Set up layout
        layout = QVBoxLayout()
        
        # Create horizontal layouts for P, I, D pairs
        layout_p = QHBoxLayout()
        layout_p.addWidget(self.label_p)
        layout_p.addWidget(self.textbox_p)
        
        layout_i = QHBoxLayout()
        layout_i.addWidget(self.label_i)
        layout_i.addWidget(self.textbox_i)
        
        layout_d = QHBoxLayout()
        layout_d.addWidget(self.label_d)
        layout_d.addWidget(self.textbox_d)
        
        # Add P, I, D pairs vertically
        layout.addLayout(layout_p)
        layout.addLayout(layout_i)
        layout.addLayout(layout_d)
        
        layout.addWidget(self.start_button)

        # Set the layout for the main window
        self.setLayout(layout)

        # Connect button clicks to functions
        self.start_button.clicked.connect(self.on_start_button_click)

    def create_new_plot(self):
        # Create a new PlotWindow instance
        self.plot_windows.append(PlotWindow(self.arduino_serial, self.p, self.i, self.d))
        self.plot_windows[-1].show()
        arduino_serial.send_command(Command.SET_PID_VALUES, self.p, self.i, self.d, 1, 0)

    def on_start_button_click(self):
        # Get P, I, D values from text boxes
        self.p = float(self.textbox_p.text())
        self.i = float(self.textbox_i.text())
        self.d = float(self.textbox_d.text())
        
        print(f"P: {self.p}, I: {self.i}, D: {self.d}")

        # Create a new plot with the updated PID values
        self.create_new_plot()

    def mousePressEvent(self, event):
        # Set focus to the main window, which removes focus from the text boxes
        self.setFocus()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            print("Left arrow key pressed")
            arduino_serial.send_command(Command.SET_MOTOR_SPEED, 126)
        elif event.key() == Qt.Key_Right:
            print("Right arrow key pressed")
            arduino_serial.send_command(Command.SET_MOTOR_SPEED, -126)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Left:
            print("Left arrow key released")
            arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)
        elif event.key() == Qt.Key_Right:
            print("Right arrow key released")
            arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)

if __name__ == '__main__':
    # Connect to the Arduino
    arduino_serial = SerialCommunicator(baudrate=250000)

    try:
        arduino_serial.connect_id(target_vid="1A86", target_pid="7523")
        if arduino_serial.serial.is_open:
            print("Connected to {0}.".format(arduino_serial.port))
        else:
            print("Could not connect to Arduino.")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MyWindow(arduino_serial)
    window.setWindowTitle("Qt5 Application")
    window.setGeometry(100, 100, 500, 500)
    window.show()
    sys.exit(app.exec_())
