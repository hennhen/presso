from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QGroupBox, QHBoxLayout, QLineEdit, QFormLayout, QGridLayout
)
from PyQt5.QtCore import Qt

class MotorStatus(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        main_layout = QVBoxLayout()

        # Horizontal layout for Motor Control and Position Slider
        control_and_position_layout = QHBoxLayout()

        # Motor Control Group
        motor_control_group = QGroupBox("Motor Control")
        motor_control_layout = QVBoxLayout()

        extraction_button = QPushButton("ready position")
        up_button = QPushButton("↑")
        down_button = QPushButton("↓")
        homing_button = QPushButton("homing")

        motor_control_layout.addWidget(extraction_button)
        motor_control_layout.addWidget(up_button)
        motor_control_layout.addWidget(down_button)
        motor_control_layout.addWidget(homing_button)

        motor_control_group.setLayout(motor_control_layout)
        control_and_position_layout.addWidget(motor_control_group)

        # Motor Position Slider Group
        motor_position_group = QGroupBox("Piston Position")
        motor_position_layout = QVBoxLayout()

        current_position_label = QLabel("34.4 mm")
        top_label = QLabel("Top")
        bottom_label = QLabel("Bottom")
        motor_slider = QSlider(Qt.Vertical)
        motor_slider.setRange(0, 200000)
        motor_slider.setMinimumHeight(150)
        motor_slider.setStyleSheet("""
        QSlider::groove:vertical {
            border: 2px solid;
            background: #12ABC6;
            }
        QSlider::handle:vertical {
            border: 1px solid;
            height: 10px;
            margin: -5px 0;
            }
        QSlider::sub-page:vertical {
            background: gray;  
            border: 2px solid;
        }
        """)

        # Centering the slider in the layout
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(current_position_label, 0, Qt.AlignCenter)
        slider_layout.addWidget(top_label, 0, Qt.AlignCenter)
        slider_layout.addWidget(motor_slider, 0, Qt.AlignCenter)
        slider_layout.addWidget(bottom_label, 0, Qt.AlignCenter)

        motor_position_layout.addLayout(slider_layout)

        motor_position_group.setLayout(motor_position_layout)
        control_and_position_layout.addWidget(motor_position_group)

        # Add the control and position layout to the main layout
        main_layout.addLayout(control_and_position_layout)

        # Status Indicators Group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()

        pressure_layout = QHBoxLayout()
        pressure_label = QLabel("Pressure:")
        pressure_value = QLineEdit("8.9")
        pressure_value.setAlignment(Qt.AlignCenter)
        pressure_value.setReadOnly(True)
        pressure_layout.addWidget(pressure_label)
        pressure_layout.addWidget(pressure_value)
        pressure_layout.addWidget(QLabel("bar"))

        current_layout = QHBoxLayout()
        current_label = QLabel("Current:")
        current_value = QLineEdit("12.2")
        current_value.setAlignment(Qt.AlignCenter)
        current_value.setReadOnly(True)
        current_layout.addWidget(current_label)
        current_layout.addWidget(current_value)
        current_layout.addWidget(QLabel("A"))

        rpm_layout = QHBoxLayout()
        rpm_label = QLabel("Speed:")
        rpm_value = QLineEdit("13.1")
        rpm_value.setAlignment(Qt.AlignCenter)
        rpm_value.setReadOnly(True)
        rpm_layout.addWidget(rpm_label)
        rpm_layout.addWidget(rpm_value)
        rpm_layout.addWidget(QLabel("mm/s"))

        # Add the status layouts to the status group layout
        status_layout.addLayout(pressure_layout)
        status_layout.addLayout(current_layout)
        status_layout.addLayout(rpm_layout)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # Set the main layout for the widget
        self.setLayout(main_layout)

# Test code to create a simple application window and display the MotorStatus widget
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    motor_status_widget = MotorStatus()
    motor_status_widget.show()
    sys.exit(app.exec_())