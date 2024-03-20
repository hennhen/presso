# extraction_settings.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLineEdit, QLabel, QRadioButton, QButtonGroup, QFormLayout, QApplication
)

class ExtractionSettings(QWidget):
    def __init__(self):
        super().__init__()

        # Main vertical layout
        main_layout = QVBoxLayout()

        # Make a group for the target settings
        target_group = QGroupBox("Target Settings")
        target_layout = QVBoxLayout()

        # Create a button group for radio buttons
        self.radio_group = QButtonGroup(self)

        # Static Target
        static_group = QGroupBox()
        static_layout = QVBoxLayout()
        self.static_radio = QRadioButton("Static Target")
        self.radio_group.addButton(self.static_radio)  # Add the radio button to the group
        static_layout.addWidget(self.static_radio)
        static_settings_layout = QFormLayout()
        self.static_field = QLineEdit("100")  # Default value set to 100
        static_settings_layout.addRow("Setpoint: ", self.static_field)
        static_layout.addLayout(static_settings_layout)
        static_group.setLayout(static_layout)
        target_layout.addWidget(static_group)

        # Sine Target
        sine_group = QGroupBox()
        sine_layout = QVBoxLayout()
        self.sine_radio = QRadioButton("Sine Target")
        self.radio_group.addButton(self.sine_radio)  # Add the radio button to the group
        sine_layout.addWidget(self.sine_radio)
        sine_settings_layout = QFormLayout()

        self.amplitude_field = QLineEdit("100")  # Default value set to 100
        sine_settings_layout.addRow("Amplitude: ", self.amplitude_field)
        
        self.frequency_field = QLineEdit("100")  # Default value set to 100
        sine_settings_layout.addRow("Frequency: ", self.frequency_field)
        
        self.offset_field = QLineEdit("100")  # Default value set to 100
        sine_settings_layout.addRow("Offset: ", self.offset_field)
        
        sine_layout.addLayout(sine_settings_layout)
        sine_group.setLayout(sine_layout)
        target_layout.addWidget(sine_group)

        # Custom Target
        custom_group = QGroupBox()
        custom_layout = QVBoxLayout()
        self.custom_radio = QRadioButton("Custom Profile")
        self.radio_group.addButton(self.custom_radio)  # Add the radio button to the group
        custom_layout.addWidget(self.custom_radio)
        custom_group.setLayout(custom_layout)
        target_layout.addWidget(custom_group)

        # Add the target group to the main layout
        target_group.setLayout(target_layout)
        main_layout.addWidget(target_group)

        # Set the main layout for the widget
        self.setLayout(main_layout)
        main_layout.addStretch(1)



# Test code to create a simple application window and display the ExtractionSettings widget
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    extraction_settings_widget = ExtractionSettings()
    extraction_settings_widget.show()
    sys.exit(app.exec_())