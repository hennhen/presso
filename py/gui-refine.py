import sys
import typing
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QRadioButton, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QEvent, QTimer, QThread, pyqtSignal

import sys
import json

from serial_comms import GraphLauncher, PlotWindow
from arduino_comms import SerialCommunicator
from arduino_commands import Command

class SerialWorker(QThread):
    data_received = pyqtSignal(object, object)  # Custom signal to emit command and value

    def __init__(self, arduino_serial):
        super().__init__()
        self.arduino_serial = arduino_serial
        self.running = True

    def run(self):
        while self.running:
            command, value = self.arduino_serial.receive_response()
            if command is not None:
                self.data_received.emit(command, value)  # Emit the signal with the received data

    def stop(self):
        self.running = False

class ControlPanel(QWidget):
    def __init__(self, arduino_serial):
        super().__init__()

        self.arduino_serial = arduino_serial
        self.p = 1
        self.i = 1
        self.d = 1
        self.plot_windows = []

        # Create main layout
        main_layout = QVBoxLayout()

        # PID input section
        pid_layout = QFormLayout()
        self.p_input = QLineEdit()
        self.p_input.setText("100")  # Set default value for P
        self.i_input = QLineEdit()
        self.i_input.setText("2")    # Set default value for I
        self.d_input = QLineEdit()
        self.d_input.setText("0")    # Set default value for D
        self.duration_input = QLineEdit()
        self.duration_input.setText("3000")    # Set default value for D
        pid_layout.addRow("P:", self.p_input)
        pid_layout.addRow("I:", self.i_input)
        pid_layout.addRow("D:", self.d_input)
        pid_layout.addRow("Duration (ms):", self.duration_input)

        # Button to start plotting
        self.start_button = QPushButton("Start + Plot")
        pid_layout.addWidget(self.start_button)

        # Profile selection section (horizontal radio buttons)
        profile_group = QGroupBox("Select a Profile:")
        profiles_layout = QHBoxLayout()  # Use QHBoxLayout for horizontal radio buttons
        self.sine_radio = QRadioButton("Sine")
        self.static_radio = QRadioButton("Static")
        self.ramp_radio = QRadioButton("Ramp")
        self.static_radio.setChecked(True)  # Set Static as the default option
        profiles_layout.addWidget(self.sine_radio)
        profiles_layout.addWidget(self.static_radio)
        profiles_layout.addWidget(self.ramp_radio)
        profile_group.setLayout(profiles_layout)

        # Text box for manual movement
        manual_movement_text = QLabel("Use left & right keys to manually move", alignment=Qt.AlignCenter)
        
        # Create a horizontal layout for profile parameters
        profile_params_layout = QHBoxLayout()

        # Sine Profile parameters
        sine_group = QGroupBox("Sine Profile:")
        sine_layout = QFormLayout()
        self.amplitude_input = QLineEdit()
        self.amplitude_input.setText("1")  # Set default value for Amplitude
        self.offset_input = QLineEdit()
        self.offset_input.setText("7")  # Set default value for Offset
        self.frequency_input = QLineEdit()
        self.frequency_input.setText("0.5")  # Set default value for Frequency
        sine_layout.addRow("Amplitude:", self.amplitude_input)
        sine_layout.addRow("Offset:", self.offset_input)
        sine_layout.addRow("Frequency:", self.frequency_input)
        sine_group.setLayout(sine_layout)

        # Static Profile parameters
        static_group = QGroupBox("Static Profile:")
        static_layout = QFormLayout()
        self.static_setpoint_input = QLineEdit()
        self.static_setpoint_input.setText("8")  # Set default value for Setpoint
        static_layout.addRow("Setpoint:", self.static_setpoint_input)
        static_group.setLayout(static_layout)

        # Ramp Profile parameters
        ramp_group = QGroupBox("Ramp Profile:")
        ramp_layout = QFormLayout()
        self.ramp_max_pressure_input = QLineEdit()
        self.ramp_max_pressure_input.setText("8")  # Set default value for Max Pressure
        self.ramp_duration_input = QLineEdit()
        self.ramp_duration_input.setText("2")  # Set default value for Ramp Duration
        self.hold_pressure_input = QLineEdit()
        self.hold_pressure_input.setText("8")  # Set default value for Hold Pressure
        self.hold_duration_input = QLineEdit()
        self.hold_duration_input.setText("3")  # Set default value for Hold Duration
        ramp_layout.addRow("Max Pressure:", self.ramp_max_pressure_input)
        ramp_layout.addRow("Ramp Duration (s):", self.ramp_duration_input)
        ramp_layout.addRow("Hold Pressure (bar):", self.hold_pressure_input)
        ramp_layout.addRow("Hold Duration (s):", self.hold_duration_input)
        ramp_group.setLayout(ramp_layout)

        # Add profile groups to the horizontal layout
        profile_params_layout.addWidget(sine_group)
        profile_params_layout.addWidget(static_group)
        profile_params_layout.addWidget(ramp_group)

        # Add sections to the main layout
        main_layout.addLayout(pid_layout)
        main_layout.addWidget(profile_group)
        main_layout.addLayout(profile_params_layout)
        main_layout.addWidget(manual_movement_text)

        # Load preset values from JSON file or set defaults
        self.load_preset_values()

        # Set the layout for the main window
        self.setLayout(main_layout)

        # Connect button clicks to functions
        self.start_button.clicked.connect(self.on_start_button_click)

        # Set focus policy for manual movement
        self.setFocusPolicy(Qt.StrongFocus)

        # Set up key event filters for manual movement
        self.installEventFilter(self)

        # Initialize the serial worker and move it to a separate thread
        # self.serial_worker = SerialWorker(arduino_serial)
        # self.serial_worker.data_received.connect(self.handle_received_data)
        # self.serial_worker.start()

    def handle_received_data(self, command, value):
        # Handle the received data in the main thread
        if command == Command.EXTRACTION_STOPPED.value:
            print("Extraction Stopped.")
        elif command == Command.PRESSURE_READING.value:
            print(f"Pressure Reading: {value}")
        elif command == Command.WEIGHT_READING.value:
            print(f"Weight Reading: {value}")
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Left:
                print("Left arrow key pressed")
                self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 126)
            elif event.key() == Qt.Key_Right:
                print("Right arrow key pressed")
                self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, -126)
        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
                print("Arrow key released")
                self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)
        elif event.type() == QEvent.Close:
            print("Closing window. Saving preset values.")
            self.save_preset_values()
            # Stop the serial worker thread before closing the application
            self.serial_worker.stop()
            self.serial_worker.wait()  # Wait for the thread to finish
            super(ControlPanel, self).closeEvent(event)
        return super(ControlPanel, self).eventFilter(obj, event)

    # Function to load preset values from a JSON file
    def load_preset_values(self):
        try:
            with open('./py/preset_values.json', 'r') as file:
                data = json.load(file)
                print(data)
                try:
                    self.p = float(data.get('p', 1))
                    self.i = float(data.get('i', 1))
                    self.d = float(data.get('d', 1))
                    self.duration = int(data.get('duration', 3000))

                    # Set the text box values using the provided syntax
                    self.p_input.setText(str(self.p))
                    self.i_input.setText(str(self.i))
                    self.d_input.setText(str(self.d))
                    self.duration_input.setText(str(self.duration))

                    # Set other text box values here
                    self.amplitude_input.setText(str(data.get('amplitude', 1)))
                    self.offset_input.setText(str(data.get('offset', 7)))
                    self.frequency_input.setText(str(data.get('frequency', 0.5)))
                    self.static_setpoint_input.setText(str(data.get('setpoint', 8)))
                    self.ramp_max_pressure_input.setText(str(data.get('max_pressure', 8)))
                    self.ramp_duration_input.setText(str(data.get('ramp_duration', 2)))
                    self.hold_pressure_input.setText(str(data.get('hold_pressure', 8)))
                    self.hold_duration_input.setText(str(data.get('hold_duration', 3)))

                except ValueError as e:
                    # Invalid values found. Just open up as normal
                    print(f"Error loading preset values: {e}")
                    pass

        except FileNotFoundError:
            # File doesn't exist, use default values
            pass

    def save_preset_values(self):
        data = {
            'p': self.p_input.text(),
            'i': self.i_input.text(),
            'd': self.d_input.text(),
            'duration': self.duration_input.text(),
            'amplitude': self.amplitude_input.text(),
            'offset': self.offset_input.text(),
            'frequency': self.frequency_input.text(),
            'static_setpoint': self.static_setpoint_input.text(),
            'ramp_max_pressure': self.ramp_max_pressure_input.text(),
            'ramp_duration': self.ramp_duration_input.text(),
            'hold_pressure': self.hold_pressure_input.text(),
            'hold_duration': self.hold_duration_input.text()
        }
        with open('./py/preset_values.json', 'w') as file:
            json.dump(data, file)

    def create_new_plot(self):
        # Create a new PlotWindow instance
        arduino_serial.send_command(Command.SET_PID_VALUES, self.p, self.i, self.d)
        # arduino_serial.flush()
        arduino_serial.send_command(Command.START_PARTIAL_EXTRACTION)
        self.plot_windows.append(PlotWindow(self.arduino_serial, self.p, self.i, self.d))
        self.plot_windows[-1].show()

    def on_start_button_click(self):
        # Get P, I, D values from text boxes
        self.p = float(self.p_input.text())
        self.i = float(self.i_input.text())
        self.d = float(self.d_input.text())

        # Get profile type
        if self.sine_radio.isChecked():
            profile = {
                'type': 'sine',
                'amplitude': float(self.amplitude_input.text()),
                'frequency': float(self.frequency_input.text()),
                'offset': float(self.offset_input.text()),
                'duration': int(self.duration_input.text())
            }
        elif self.static_radio.isChecked():
            profile = {
                'type': 'static',
                'setpoint': float(self.static_setpoint_input.text()),
                'duration': int(self.duration_input.text())
            }
            
        arduino_serial.send_command(Command.PROFILE_SELECTION, profile)
        # Create a new plot with the updated PID values
        self.create_new_plot()
        
    def mousePressEvent(self, event):
        # Set focus to the main window, which removes focus from the text boxes
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            print("Left arrow key pressed")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 126)
        elif event.key() == Qt.Key_Right:
            print("Right arrow key pressed")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, -126)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Left:
            print("Left arrow key released")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)
        elif event.key() == Qt.Key_Right:
            print("Right arrow key released")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)

if __name__ == '__main__':
    # Connect to the Arduino
    arduino_serial = SerialCommunicator(baudrate=460800)

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
    window = ControlPanel(arduino_serial)
    window.setWindowTitle("Control Panel")
    window.show()
    sys.exit(app.exec_())