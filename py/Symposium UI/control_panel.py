from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QHBoxLayout, QRadioButton, QGroupBox
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QFont, QFontDatabase
from serial_worker import SerialWorker
from serial_communicator import SerialCommunicator
from commands_list import Command
from styles import GLOBAL_STYLESHEET
import sys

sys.path.insert(1, 'py/Symposium UI/widgets')
from live_plots import LivePlotWidget

class ControlPanel(QWidget):
    def __init__(self, arduino_serial: SerialCommunicator):
        super().__init__()
        self.arduino_serial = arduino_serial
        if self.arduino_serial is not None:
            self.init_ui()
            self.init_serial_worker()
            # self.connect_extraction_plot_signals()
            self.live_plot_widget.extraction_plot_signal.connect(self.extraction_end_signal_received)
        else:
            print("Arduino serial is None")

        # Set focus policy for manual movement
        self.setFocusPolicy(Qt.StrongFocus)

        # Set up key event filters for manual movement
        self.installEventFilter(self)
        self.setFocus()
#region Functional Stuff
    def connect_extraction_plot_signals(self):
        self.serial_worker.data_received.connect(self.live_plot_widget.update_plots)
    def extraction_end_signal_received(self):
        self.serial_worker.data_received.disconnect(self.live_plot_widget.update_plots)

    def init_serial_worker(self):
        # Initialize the SerialWorker thread
        self.serial_worker = SerialWorker(self.arduino_serial)

        # data_received is a signal that is emitted when the SerialWorker receives data
        # We connect this signal to the handle_received_data method
        self.serial_worker.data_received.connect(self.update_sensor_data_display)
        self.serial_worker.start()

    def update_sensor_data_display(self, command, value):
        # Handle the received data from the SerialWorker
        # print(f"handle_received_data: {command}, value: {value}")
        if command == Command.PRESSURE_READING.value:
            self.pressure_label.setText(f"Pressure: {value:.2f}")  # Assuming value is a float
        elif command == Command.WEIGHT_READING.value:
            self.weight_label.setText(f"Weight: {value:.1f}")  # Assuming value is a float
        elif command == Command.TEMPERATURE.value:
            self.current_temperature_label.setText(f"Current: {value:.1f}ºC")  # Assuming value is a float
        elif command == Command.MOTOR_CURRENT.value:
            self.motor_current_label.setText(f"Motor Current: {value:.2f}A")  # Assuming value is a float
        elif command == Command.MOTOR_SPEED.value:
            self.motor_speed_label.setText(f"Motor Speed: {value:.0f}")  # Assuming value is a float
        elif command == Command.MOTOR_POSITION.value:
            self.motor_position_label.setText(f"Motor Position: {value:.0f}")  # Assuming value is a float
        else:
            pass
    def set_temperature_clicked(self):
        # Set the target temperature. If 0, display off
        target_temperature = float(self.target_temperature_input.text())
        if target_temperature <= 0:
            self.target_temp_label.setText("OFF")
        else:
            self.target_temp_label.setText(f"Target: {target_temperature}ºC")
        self.arduino_serial.send_command(Command.TEMPERATURE, target_temperature)

    def start_extraction_clicked(self):
        # Start the extraction process
        print("Start extraction")
        p_value = float(self.p_input.text())
        i_value = float(self.i_input.text())
        d_value = float(self.d_input.text())
        sample_time_value = float(self.sample_time_input.text())
        duration_value = int(self.duration_input.text())

        # Extract profile parameters based on the selected radio button
        if self.sine_radio.isChecked():
            profile = {
                'type': 'sine',
                'amplitude': float(self.amplitude_input.text()),
                'frequency': float(self.frequency_input.text()),
                'offset': float(self.offset_input.text()),
                'duration': duration_value
            }
        elif self.static_radio.isChecked():
            profile = {
                'type': 'static',
                'setpoint': float(self.static_setpoint_input.text()),
                'duration': duration_value
            }
        
        # self.arduino_serial.send_command(Command.PROFILE_SELECTION, profile)
        self.arduino_serial.send_command(Command.SET_PID_VALUES, p_value, i_value, d_value, sample_time_value)
        # self.arduino_serial.send_command(Command.START_PARTIAL_EXTRACTION)
        
        self.live_plot_widget.clear_plots()
        self.connect_extraction_plot_signals()
        # self.arduino_serial.send_command(Command.START_EXTRACTION)
#endregion

    def init_ui(self):
        """ Initialize the UI components """ 
        main_layout = QHBoxLayout(self)
        control_panel_layout = QVBoxLayout()
        
        """ LIVE PLOT WIDGET """ 
        plot_widget_layout = QVBoxLayout()
        self.live_plot_widget = LivePlotWidget(self)
        plot_widget_layout.addWidget(self.live_plot_widget)

        """ TEMPORARY BUTTONS TO CONNECT & DISCONNECT SLOTS """
        # Massive Stop Button
        self.stop_button = QPushButton("STOP")
        self.stop_button.setObjectName("startButton")  # Set the object name to redButton
        self.stop_button.setFixedHeight(100)  # Making the button taller
        control_panel_layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.arduino_serial.send_stop_request)

        # TEMP BUTTONS TO CONNECT & DISCONNECT SLOTS
        # Connect and disconnect slots for temporary buttons
        connect_button = QPushButton("Connect")
        disconnect_button = QPushButton("Disconnect")
        connect_button.clicked.connect(self.connect_extraction_plot_signals)
        disconnect_button.clicked.connect(self.extraction_end_signal_received)
        control_panel_layout.addWidget(connect_button)
        control_panel_layout.addWidget(disconnect_button)

        # Homing Button
        self.homing_button = QPushButton("Homing")
        control_panel_layout.addWidget(self.homing_button)
        self.homing_button.clicked.connect(self.arduino_serial.send_homing_sequence)

        # Goto Extraction Position Button
        self.goto_extraction_position_button = QPushButton("Goto Extraction Position")
        control_panel_layout.addWidget(self.goto_extraction_position_button)
        self.goto_extraction_position_button.clicked.connect(self.arduino_serial.send_goto_extraction_position)

#region control_panel_layout
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
        # Motor position label
        self.motor_position_label = QLabel("Motor Position: --")
        sensor_data_layout.addWidget(self.motor_position_label)
        # Motor current label
        self.motor_current_label = QLabel("Motor Current: --")
        sensor_data_layout.addWidget(self.motor_current_label)
        # Motor speed label
        self.motor_speed_label = QLabel("Motor Speed: --")
        sensor_data_layout.addWidget(self.motor_speed_label)
        # Weight Label
        self.weight_label = QLabel("Weight: --")
        sensor_data_layout.addWidget(self.weight_label)
        # Tare Button
        self.tare_button = QPushButton("Tare")
        sensor_data_layout.addWidget(self.tare_button)
        self.tare_button.clicked.connect(self.arduino_serial.send_tare_request)

        # Add them to the group
        sensor_data_group.setLayout(sensor_data_layout)
        top_layout.addWidget(sensor_data_group)

        # PID Input Section
        pid_group = QGroupBox("PID settings")
        pid_layout = QFormLayout()
        self.p_input = QLineEdit("100")  # Set default value for P
        self.i_input = QLineEdit("2")    # Set default value for I
        self.d_input = QLineEdit("0")    # Set default value for D
        self.sample_time_input = QLineEdit("0.1")  # Set default value for Sample Time
        self.duration_input = QLineEdit("60")  # Set default value for Duration in seconds
        pid_layout.addRow("P:", self.p_input)
        pid_layout.addRow("I:", self.i_input)
        pid_layout.addRow("D:", self.d_input)
        pid_layout.addRow("Sample Time:", self.sample_time_input)
        pid_layout.addRow("Duration:", self.duration_input)
        pid_group.setLayout(pid_layout)
        top_layout.addWidget(pid_group)

        # Temperature Control Section
        temperature_group = QGroupBox("Temperature Control")
        temperature_layout = QVBoxLayout()

        # Current Temperature Label
        self.current_temperature_label = QLabel("Current: --ºC")
        temperature_layout.addWidget(self.current_temperature_label)

        # Target Temperature Input
        self.target_temp_label = QLabel("Target: OFF")
        temperature_layout.addWidget(self.target_temp_label)
        self.target_temperature_input = QLineEdit("25")  # Set default value for Target Temperature
        self.target_temperature_input.setAlignment(Qt.AlignCenter)
        temperature_layout.addWidget(self.target_temperature_input)
        temperature_layout.addWidget(self.target_temperature_input)

        # Set Temperature Button with center alignment
        self.set_temperature_button = QPushButton("Set Temperature")
        temperature_layout.addWidget(self.set_temperature_button)
        self.set_temperature_button.clicked.connect(self.set_temperature_clicked)

        temperature_group.setLayout(temperature_layout)
        top_layout.addWidget(temperature_group)

        # Add the top layout to the main layout
        control_panel_layout.addLayout(top_layout)
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
        control_panel_layout.addWidget(profile_group)
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
        static_layout.addRow("Setpoint:", self.static_setpoint_input)
        static_group.setLayout(static_layout)
        profile_parameters_layout.addWidget(static_group)

        control_panel_layout.addLayout(profile_parameters_layout)
    #endregion
        
        # Start button
        self.start_button = QPushButton("Start", objectName="startButton")
        # self.start_button.setObjectName("startButton")  # Set the object name to redButton
        control_panel_layout.addWidget(self.start_button)
#endregion
        
        main_layout.addLayout(control_panel_layout)
        main_layout.addLayout(plot_widget_layout)
        # Set the main layout
        self.setLayout(main_layout)

        # Connect signals and slots
        self.start_button.clicked.connect(self.start_extraction_clicked)

#region Events: Mouse, keybaord, close
    def mousePressEvent(self, event):
        # Set focus to the main window, which removes focus from the text boxes
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            print("Up arrow key pressed")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 126)
        elif event.key() == Qt.Key_Down:
            print("Right arrow key pressed")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, -126)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Up:
            print("Left arrow key released")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)
        elif event.key() == Qt.Key_Down:
            print("Right arrow key released")
            self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0)    
        elif event.key() == Qt.Key_Space:
            self.arduino_serial.send_command(Command.STOP)

    def closeEvent(self, event):
        # Override the close event to properly shut down the SerialWorker thread
        self.serial_worker.running = False
        self.serial_worker.stop()
        self.serial_worker.wait()
        event.accept()
#endregion


if __name__ == '__main__':
    # This block is for testing purposes and should be in your main.py

    app = QApplication(sys.argv)
    # app.setStyleSheet(GLOBAL_STYLESHEET)
    arduino_serial = SerialCommunicator(baudrate=250000, timeout=0.5, simulate=False)  # Set the correct baudrate
    try:
        arduino_serial.connect_id(target_vid="1A86", target_pid="7523")
        if arduino_serial.serial.is_open:
            print("Connected to {0}.".format(arduino_serial.port))
        else:
            print("Could not connect to Arduino.")
            # sys.exit(1)
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        # sys.exit(1)

    window = ControlPanel(arduino_serial)
    window.show()
    sys.exit(app.exec_())