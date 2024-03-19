#include <Arduino.h>
#include <HeaterController.h>

// Define the pins used for the OneWire bus and the heater control
const uint8_t ONE_WIRE_BUS = 4; // Change to the actual pin connected to the temperature sensor
const uint8_t HEATER_PIN = 12;   // Change to the actual pin connected to the heater control

// Create an instance of the HeaterController
HeaterController heaterController(ONE_WIRE_BUS, HEATER_PIN);

void setup() {
  // Start the serial communication
  Serial.begin(250000);
  
  // Set a target temperature
  heaterController.setTarget(50); // Set your desired target temperature in degrees Celsius
}

void loop() {
  unsigned long loopStartTime = millis(); // Start time of loop execution

  // Update the heater controller
  heaterController.update();

  // Read the current temperature
  float currentTemperature = heaterController.read();

  // Print the current temperature and heater status to the serial monitor
  Serial.print(currentTemperature);
  Serial.println(" C");

  // Check if the heater is on or off
  bool isHeaterOn = digitalRead(HEATER_PIN);
  Serial.println(isHeaterOn ? "ON" : "OFF");

  // Print out loop time
  unsigned long loopEndTime = millis(); // End time of loop execution
  Serial.print(loopEndTime - loopStartTime);
  Serial.println(" ms");
  delay(100);
}