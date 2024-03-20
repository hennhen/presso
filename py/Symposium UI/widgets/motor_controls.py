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

        self.extraction_position_button = QPushButton("ready position")
        self.up_button = QPushButton("↑")
        self.down_button = QPushButton("↓")
        self.homing_button = QPushButton("homing")
        self.heating_position = QPushButton("heating position")

        motor_control_layout.addWidget(self.extraction_position_button)
        motor_control_layout.addWidget(self.up_button)
        motor_control_layout.addWidget(self.down_button)
        motor_control_layout.addWidget(self.heating_position)
        motor_control_layout.addWidget(self.homing_button)

        motor_control_group.setLayout(motor_control_layout)
        control_and_position_layout.addWidget(motor_control_group)

        # Motor Position Slider Group
        motor_position_group = QGroupBox("Piston Position")
        motor_position_layout = QVBoxLayout()

        self.current_raw_position_label = QLabel("1234")
        self.current_position_label = QLabel("34.4 mm")
        self.motor_slider = QSlider(Qt.Vertical)
        self.motor_slider.setRange(0, 65000)
        self.motor_slider.setMinimumHeight(150)
        self.motor_slider.setStyleSheet("""
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
        slider_layout.addWidget(self.current_raw_position_label, 0, Qt.AlignCenter)
        slider_layout.addWidget(self.current_position_label, 0, Qt.AlignCenter)
        slider_layout.addWidget(self.motor_slider, 0, Qt.AlignCenter)

        motor_position_layout.addLayout(slider_layout)

        motor_position_group.setLayout(motor_position_layout)
        control_and_position_layout.addWidget(motor_position_group)

        # Add the control and position layout to the main layout
        main_layout.addLayout(control_and_position_layout)

        

        # Set the main layout for the widget
        self.setLayout(main_layout)

    def set_current_position(self, value):
            """
            Sets the current position of the motor slider and updates the display label.
            
            :param value: The new position value to set.
            """
            # Ensure the value is within the slider's range
            self.current_raw_position_label.setText(str(int(value)))
            mm = value / 3365
            self.current_position_label.setText(f"{mm:.1f} mm")
            if mm < 0:
                self.motor_slider.setValue(0)
            elif mm > 65:
                self.motor_slider.setValue(65)
            else:
                self.motor_slider.setValue(mm*1000)

# Test code to create a simple application window and display the MotorStatus widget
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    motor_status_widget = MotorStatus()
    motor_status_widget.show()
    sys.exit(app.exec_())