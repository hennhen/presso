import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QRadioButton, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt

import sys
from serial_comms import GraphLauncher, PlotWindow
from arduino_comms import SerialCommunicator
from arduino_commands import Command

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
        pid_layout.addRow("P:", self.p_input)
        pid_layout.addRow("I:", self.i_input)
        pid_layout.addRow("D:", self.d_input)

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

        # Profile parameters
        profile_params_layout = QVBoxLayout()

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

        profile_params_layout.addWidget(sine_group)
        profile_params_layout.addWidget(static_group)
        profile_params_layout.addWidget(ramp_group)

        # Add sections to main layout
        main_layout.addLayout(pid_layout)
        main_layout.addWidget(profile_group)
        main_layout.addLayout(profile_params_layout)

        # Text box for manual movement
        manual_movement_text = QLabel("Click empty space and use left & right keys to manually move:")
        main_layout.addWidget(manual_movement_text)

        # Set the layout for the main window
        self.setLayout(main_layout)

        # Connect button clicks to functions
        self.start_button.clicked.connect(self.on_start_button_click)

    def create_new_plot(self):
        # Create a new PlotWindow instance
        self.plot_windows.append(PlotWindow(self.arduino_serial, self.p, self.i, self.d))
        self.plot_windows[-1].show()
        arduino_serial.send_command(Command.SET_PID_VALUES, self.p, self.i, self.d, 1, 0)
        
    def on_start_button_click(self):
        # Get P, I, D values from text boxes
        self.p = float(self.p_input.text())
        self.i = float(self.i_input.text())
        self.d = float(self.d_input.text())

        # Create a new plot with the updated PID values
        self.create_new_plot()

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
    window = ControlPanel(arduino_serial)
    window.setWindowTitle("Control Panel")
    window.show()
    sys.exit(app.exec_())
