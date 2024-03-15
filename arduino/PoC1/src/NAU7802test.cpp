#include <Arduino.h>
#include <Wire.h>
#include "NAU7802.h"

// Define calibration factor (this should be determined through calibration)
const float calibrationFactor = 1030.71337; // Example calibration factor

// Create an instance of the NAU7802 class
NAU7802 scale(calibrationFactor);

void setup() {
  // Start the serial communication
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for Serial to be ready
  }
  Serial.println("Starting NAU7802 Test...");

  // Initialize the NAU7802
  if (!scale.init()) {
    Serial.println("Failed to initialize NAU7802!");
    while (1); // Halt if initialization failed
  } else {
    Serial.println("NAU7802 initialized successfully.");
    scale.tare();
  }
}

void loop() {
  // Check if data is available to read
  if (scale.available()) {
    float weight = scale.read(); // Read the weight
    Serial.print("Weight: ");
    Serial.print(weight, 2); // Print the weight with 2 decimal places
    Serial.println(" grams");
  } else {
    Serial.println("No data available.");
  }

  delay(100); // Wait for half a second before reading again
}