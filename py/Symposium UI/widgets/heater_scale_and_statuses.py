from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QApplication, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class HeaterScale(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        main_layout = QVBoxLayout()

        # Top Heater Scale Group
        heater_scale_hbox_layout = QHBoxLayout()

        # Group for the scale
        scale_group = QGroupBox("Weight")
        scale_group.setMinimumWidth(110)
        scale_layout = QVBoxLayout()
        self.weight_label = QLabel("26.7g")
        self.weight_label.setFont(QFont(None, 24, QFont.Bold))
        self.weight_label.setAlignment(Qt.AlignCenter)
        scale_layout.addWidget(self.weight_label)
        self.tare_button = QPushButton("Tare")
        scale_layout.addWidget(self.tare_button, alignment=Qt.AlignCenter)
        scale_group.setLayout(scale_layout)

        # Group for the heater
        heater_group = QGroupBox("Temperature")
        self.heater_layout = QVBoxLayout()
        # heater_layout.addItem(QSpacerItem(1, 18, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Spacer
        self.current_temp_label = QLabel("78°C")
        self.current_temp_label.setFont(QFont(None, 24, QFont.Bold))
        self.current_temp_label.setAlignment(Qt.AlignCenter)
        self.heater_layout.addWidget(self.current_temp_label)

        # Smaller label for the target temperature
        self.target_temp_display_label = QLabel("93°C")
        self.target_temp_display_label.setFont(QFont(None, 12))  # Smaller font size than the current temperature
        self.target_temp_display_label.setAlignment(Qt.AlignCenter)
        self.heater_layout.addWidget(self.target_temp_display_label)


        # heater_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Spacer

        # Vertical layout for the target temperature input and button
        target_temp_layout = QVBoxLayout()
        self.set_temp_input_label = QLineEdit()
        self.set_temp_input_label.setAlignment(Qt.AlignCenter)
        self.set_temp_button = QPushButton("Set")

        target_temp_layout.addWidget(self.set_temp_input_label)
        target_temp_layout.addWidget(self.set_temp_button)
        self.heater_layout.addLayout(target_temp_layout)

        heater_group.setLayout(self.heater_layout)

        # Add the groups to the horizontal layout
        heater_scale_hbox_layout.addWidget(scale_group)
        heater_scale_hbox_layout.addWidget(heater_group)

        main_layout.addLayout(heater_scale_hbox_layout)

        # Status Indicators Group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()

        pressure_layout = QHBoxLayout()
        pressure_label = QLabel("Pressure:")
        self.pressure_value = QLineEdit("8.9")
        self.pressure_value.setAlignment(Qt.AlignCenter)
        self.pressure_value.setReadOnly(True)
        pressure_layout.addWidget(pressure_label)
        pressure_layout.addWidget(self.pressure_value)
        pressure_layout.addWidget(QLabel("bar"))

        current_layout = QHBoxLayout()
        current_label = QLabel("Current:")
        self.current_value = QLineEdit("12.2")
        self.current_value.setAlignment(Qt.AlignCenter)
        self.current_value.setReadOnly(True)
        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_value)
        current_layout.addWidget(QLabel("A"))

        rpm_layout = QHBoxLayout()
        rpm_label = QLabel("Speed:")
        self.speed_value = QLineEdit("13.1")
        self.speed_value.setAlignment(Qt.AlignCenter)
        self.speed_value.setReadOnly(True)
        rpm_layout.addWidget(rpm_label)
        rpm_layout.addWidget(self.speed_value)
        rpm_layout.addWidget(QLabel("mm/s"))

        # Add the status layouts to the status group layout
        status_layout.addLayout(pressure_layout)
        status_layout.addLayout(current_layout)
        status_layout.addLayout(rpm_layout)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        # Set the main layout for the widget
        self.setLayout(main_layout)

# Test code to create a simple application window and display the HeaterScale widget
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    heater_scale_widget = HeaterScale()
    heater_scale_widget.show()
    sys.exit(app.exec_())