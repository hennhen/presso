# main_ui.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QHBoxLayout, QRadioButton, QGroupBox
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QFont, QFontDatabase
from serial_worker import SerialWorker
from serial_communicator import SerialCommunicator
from commands_list import Command
from styles import GLOBAL_STYLESHEET

from widgets.motor_controls import MotorStatus
from widgets.heater_scale_and_statuses import HeaterScale
from widgets.pid_settings import ExtractionSettings as PIDSettings
from widgets.target_settings import ExtractionSettings as TargetSettings
from widgets.custom_profile import ProfileMakerWidget
from widgets.live_plots import LivePlotWidget

class MainUI(QMainWindow):
    def __init__(self, ard_serial: SerialCommunicator):
        super().__init__()
        self.arduino_serial = ard_serial
        self.init_ui()
        self.init_serial_worker()
        self.connect_buttons()

        self.setFocusPolicy(Qt.StrongFocus)
        self.installEventFilter(self)
        self.setFocus()
        self.connect_extraction_plot_signals()
        # Recieve extration end signal
        self.live_plots_widget.extraction_plot_signal.connect(self.extraction_end_signal_received)



    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)

        # First vertical column
        first_column = QVBoxLayout()
        self.motor_controls_widget = MotorStatus()
        self.heater_scale_live_status_widget = HeaterScale()
        self.pid_settings_widget = PIDSettings()
        first_column.addWidget(self.motor_controls_widget)
        first_column.addWidget(self.heater_scale_live_status_widget)
        first_column.addWidget(self.pid_settings_widget)

        # Second vertical column
        second_column = QVBoxLayout()
        self.custom_profile_widget = ProfileMakerWidget()
        self.target_settings_widget = TargetSettings()
        # Start and Stop bottom HGroup
        self.start_stop_hbox_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.start_button.setMinimumHeight(40)
        self.stop_button.setMinimumHeight(40)
        self.start_stop_hbox_layout.addWidget(self.start_button)
        self.start_stop_hbox_layout.addWidget(self.stop_button)
        second_column.addWidget(self.custom_profile_widget)
        second_column.addLayout(self.start_stop_hbox_layout)
        second_column.addWidget(self.target_settings_widget)
        second_column.addStretch(1)

        # Third vertical column
        third_column = QVBoxLayout()
        self.live_plots_widget = LivePlotWidget(None)  # Assuming no serial connection for this example
        third_column.addWidget(self.live_plots_widget)

        # Add columns to the main layout
        main_layout.addLayout(first_column)
        main_layout.addLayout(second_column)
        main_layout.addLayout(third_column)

        # Set window title and size
        self.setWindowTitle("Control Panel")
        self.resize(1200, 800)  # Adjust the size as needed

    def connect_extraction_plot_signals(self):
        self.serial_worker.data_received.connect(self.live_plots_widget.update_plots)
    def extraction_end_signal_received(self):
        self.serial_worker.data_received.disconnect(self.live_plots_widget.update_plots)

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
            self.heater_scale_live_status_widget.pressure_value.setText(f"{value:.2f}")  # Assuming value is a float
        elif command == Command.TEMPERATURE.value:
            self.heater_scale_live_status_widget.current_temp_label.setText(f"{value:.1f}")
        elif command == Command.MOTOR_CURRENT.value:
            self.heater_scale_live_status_widget.current_value.setText(f"{value:.2f}")  # Assuming value is a float
        elif command == Command.MOTOR_SPEED.value:
            speedmm_s = value / 3365.0
            self.heater_scale_live_status_widget.speed_value.setText(f"{speedmm_s:.2f}") 
        elif command == Command.MOTOR_POSITION.value:
            self.motor_controls_widget.set_current_position(value)
        elif command == Command.WEIGHT_READING.value:
            self.heater_scale_live_status_widget.weight_label.setText(f"{value:.1f}g")  # Assuming value is a float
        else:
            pass
    def start_button_clicked(self):
        # Start the extraction process
        p_value = float(self.pid_settings_widget.p_line_edit.text())
        i_value = float(self.pid_settings_widget.i_line_edit.text())
        d_value = float(self.pid_settings_widget.d_line_edit.text())
        sample_time_value = float(self.pid_settings_widget.sample_time_line_edit.text())
        duration_value = float(self.pid_settings_widget.duration_line_edit.text())

        print(f"Start extraction: p: {p_value}, i: {i_value}, d: {d_value}, sample time: {sample_time_value}, duration: {duration_value}")
        self.arduino_serial.send_command(Command.SET_PID_VALUES, p_value, i_value, d_value, sample_time_value)

        # Extract profile parameters based on the selected radio button
        if self.target_settings_widget.sine_radio.isChecked():
            profile = {
                'type': 'sine',
                'amplitude': float(self.target_settings_widget.amplitude_field.text()),
                'frequency': float(self.target_settings_widget.frequency_field.text()),
                'offset': float(self.target_settings_widget.offset_field.text()),
                'duration': duration_value
            }
        elif self.target_settings_widget.static_radio.isChecked():
            profile = {
                'type': 'static',
                'setpoint': float(self.target_settings_widget.static_field.text()),
                'duration': duration_value
            }
        elif self.target_settings_widget.custom_radio.isChecked():
            profile = {
                'type': 'custom',
                'points' : self.custom_profile_widget.getPoints(),
            }
        
        self.arduino_serial.send_command(Command.PROFILE_SELECTION, profile)
        
        self.live_plots_widget.clear_plots()
        
        self.arduino_serial.send_command(Command.START_PARTIAL_EXTRACTION)
        # self.arduino_serial.wait_for_extraction_start()
        self.connect_extraction_plot_signals()

    def connect_buttons(self):
        self.stop_button.clicked.connect(self.arduino_serial.send_stop_request)
        self.start_button.clicked.connect(self.start_button_clicked)

        #region Motor Controls
        self.motor_controls_widget.extraction_position_button.clicked.connect(lambda: self.arduino_serial.send_command(Command.GOTO_POSITION_MM, float(60)))
        self.motor_controls_widget.up_button.pressed.connect(lambda: self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 126))
        self.motor_controls_widget.up_button.released.connect(lambda: self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0))
        self.motor_controls_widget.down_button.pressed.connect(lambda: self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, -126))
        self.motor_controls_widget.down_button.released.connect(lambda: self.arduino_serial.send_command(Command.SET_MOTOR_SPEED, 0))
        self.motor_controls_widget.homing_button.clicked.connect(self.arduino_serial.send_homing_sequence)
        self.motor_controls_widget.heating_position.clicked.connect(lambda: self.arduino_serial.send_command(Command.GOTO_POSITION_MM, float(2)))
        #endregion

        #region Heater Scale
        self.heater_scale_live_status_widget.set_temp_button.clicked.connect(self.handle_set_temp_button_click)
        self.heater_scale_live_status_widget.tare_button.clicked.connect(self.arduino_serial.send_tare_request)
        #endregion

        #region plot control buttons
        self.live_plots_widget.start_plotting_button.clicked.connect(self.connect_extraction_plot_signals)
        self.live_plots_widget.stop_plotting_button.clicked.connect(self.extraction_end_signal_received)
        self.live_plots_widget.clear_plots_button.clicked.connect(self.live_plots_widget.clear_plots)
        #endregion

    def handle_set_temp_button_click(self):
        # Set the target temperature. If 0, display off
        target_temperature = float(self.heater_scale_live_status_widget.set_temp_input_label.text())
        if target_temperature <= 0:
            self.heater_scale_live_status_widget.target_temp_display_label.setText("OFF")
        else:
            self.heater_scale_live_status_widget.target_temp_display_label.setText(f"{target_temperature}ºC")
        self.arduino_serial.send_command(Command.TEMPERATURE, target_temperature)
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
    app = QApplication(sys.argv)

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
    main_window = MainUI(arduino_serial)
    main_window.show()
    sys.exit(app.exec_())

