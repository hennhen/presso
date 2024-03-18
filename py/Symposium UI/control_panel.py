from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QHBoxLayout, QRadioButton, QGroupBox
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from serial_worker import SerialWorker
from plot_window import PlotWindow
from serial_communicator import SerialCommunicator
from commands_list import Command

class ControlPanel(QWidget):
    # what is this
    update_sensor_data = pyqtSignal(object)

    def __init__(self, arduino_serial: SerialCommunicator):
        super().__init__()
        self.arduino_serial = arduino_serial
        self.init_ui()
        self.init_serial_worker()

    def init_ui(self):
        # Initialize the UI components
        main_layout = QVBoxLayout(self)

    #region SENSOR DATAS AND PID INPUTS
        # create a horizontal layout first to contain the pressure and weight labels
           # Create a horizontal layout to contain the sensor data and PID input sections
        top_layout = QHBoxLayout()

        # Sensor Data Group
        sensor_data_group = QGroupBox("Sensor data")
        sensor_data_layout = QVBoxLayout()
        # Pressure Label
        self.pressure_label = QLabel("Pressure: --")
        sensor_data_layout.addWidget(self.pressure_label)
        # Weight Label
        self.weight_label = QLabel("Weight: --")
        sensor_data_layout.addWidget(self.weight_label)

        # Add them to the group
        sensor_data_group.setLayout(sensor_data_layout)
        top_layout.addWidget(sensor_data_group)

        # PID Input Section
        pid_group = QGroupBox("PID settings")
        pid_layout = QFormLayout()
        self.p_input = QLineEdit("100")  # Set default value for P
        self.i_input = QLineEdit("2")    # Set default value for I
        self.d_input = QLineEdit("0")    # Set default value for D
        pid_layout.addRow("P:", self.p_input)
        pid_layout.addRow("I:", self.i_input)
        pid_layout.addRow("D:", self.d_input)
        pid_group.setLayout(pid_layout)
        top_layout.addWidget(pid_group)

        # Temperature Control Section
        temperature_group = QGroupBox("Temperature Control")
        temperature_layout = QVBoxLayout()

        # Current Temperature Label
        self.current_temperature_label = QLabel("Current: --ºC")
        temperature_layout.addWidget(self.current_temperature_label)

        # Target Temperature Input
        target_label = QLabel("Target: OFF")
        temperature_layout.addWidget(target_label)
        self.target_temperature_input = QLineEdit("25")  # Set default value for Target Temperature
        self.target_temperature_input.setAlignment(Qt.AlignCenter)
        temperature_layout.addWidget(self.target_temperature_input)
        temperature_layout.addWidget(self.target_temperature_input)

        # Set Temperature Button with center alignment
        self.set_temperature_button = QPushButton("Set Temperature")
        temperature_layout.addWidget(self.set_temperature_button)

        temperature_group.setLayout(temperature_layout)
        top_layout.addWidget(temperature_group)

        # Add the top layout to the main layout
        main_layout.addLayout(top_layout)
    #endregion
        
    #region TARGET PARAMETERS
        # Profile selection section
        profile_group = QGroupBox("Select a Profile:")
        profiles_layout = QHBoxLayout()
        self.sine_radio = QRadioButton("Sine")
        self.static_radio = QRadioButton("Static")
        self.sine_radio.setChecked(True)  # Set sine as the default selection
        profiles_layout.addWidget(self.sine_radio)
        profiles_layout.addWidget(self.static_radio)
        profile_group.setLayout(profiles_layout)
        main_layout.addWidget(profile_group)
        #Horizontal layout box to contain the sine and static profile parameters
        profile_parameters_layout = QHBoxLayout()

        # Sine Profile parameters
        sine_group = QGroupBox("Sine Profile Parameters:")
        sine_layout = QFormLayout()
        self.amplitude_input = QLineEdit("1")  # Set default value for Amplitude
        self.frequency_input = QLineEdit("0.5")  # Set default value for Frequency
        self.offset_input = QLineEdit("0")  # Set default value for Offset
        sine_layout.addRow("Amplitude:", self.amplitude_input)
        sine_layout.addRow("Frequency:", self.frequency_input)
        sine_layout.addRow("Offset:", self.offset_input)
        sine_group.setLayout(sine_layout)
        profile_parameters_layout.addWidget(sine_group)

        # Static Profile parameters
        static_group = QGroupBox("Static Profile Parameters:")
        static_layout = QFormLayout()
        self.static_setpoint_input = QLineEdit("0")  # Set default value for Static Setpoint
        self.duration_input = QLineEdit("60")  # Set default value for Duration in seconds
        static_layout.addRow("Setpoint:", self.static_setpoint_input)
        static_layout.addRow("Duration:", self.duration_input)
        static_group.setLayout(static_layout)
        profile_parameters_layout.addWidget(static_group)

        main_layout.addLayout(profile_parameters_layout)
    #endregion
        
        # Start button
        self.start_button = QPushButton("Start")
        main_layout.addWidget(self.start_button)

        # Set the main layout
        self.setLayout(main_layout)

        # Connect signals and slots
        self.start_button.clicked.connect(self.start_extraction_clicked)

    def init_serial_worker(self):
        # Initialize the SerialWorker thread
        self.serial_worker = SerialWorker(self.arduino_serial)

        # data_received is a signal that is emitted when the SerialWorker receives data
        # We connect this signal to the handle_received_data method
        self.serial_worker.data_received.connect(self.handle_received_data)
        self.serial_worker.start()

    def handle_received_data(self, command, value):
        # Handle the received data from the SerialWorker
        # print(f"handle_received_data: {command}, value: {value}")
        if command == Command.PRESSURE_READING.value:
            self.pressure_label.setText(f"Pressure: {value:.2f}")  # Assuming value is a float
        elif command == Command.WEIGHT_READING.value:
            self.weight_label.setText(f"Weight: {value:.1f}")  # Assuming value is a float
        elif command == Command.TEMPERATURE.value:
            self.current_temperature_label.setText(f"Current: {value:.1f}ºC")  # Assuming value is a float
        else:
            self.update_sensor_data.emit(value)  # Emit signal with sensor data

    def start_extraction_clicked(self):
        # Start the extraction process
        print("Start extraction")
        p_value = float(self.p_input.text())
        i_value = float(self.i_input.text())
        d_value = float(self.d_input.text())

        # Extract profile parameters based on the selected radio button
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
        
        self.arduino_serial.send_command(Command.PROFILE_SELECTION, profile)
        self.arduino_serial.send_command(Command.SET_PID_VALUES, p_value, i_value, d_value)

        self.start_live_plotting()
        # self.arduino_serial.send_command(Command.START_EXTRACTION)

    def start_live_plotting(self):
        # Open the live plotting window
        self.plot_window = PlotWindow(self.arduino_serial)
        self.plot_window.show()
        # Connect the signal to the plot window's slot
        self.update_sensor_data.connect(self.plot_window.update_plot)

    def stop_live_plotting(self):
        # Close the live plotting window
        if self.plot_window:
            self.plot_window.close()

    def update_displays(self, sensor_data):
        # Update the main window's displays with the new sensor data
        self.sensor_label.setText(f"Sensor Data: {sensor_data}")

    def closeEvent(self, event):
        # Override the close event to properly shut down the SerialWorker thread
        self.serial_worker.running = False
        self.serial_worker.wait()
        event.accept()

if __name__ == '__main__':
    # This block is for testing purposes and should be in your main.py
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    arduino_serial = SerialCommunicator(baudrate=250000, simulate=False)  # Set the correct baudrate
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

    window = ControlPanel(arduino_serial)
    window.show()
    sys.exit(app.exec_())