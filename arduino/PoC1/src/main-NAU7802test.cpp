#include <Adafruit_NAU7802.h>
// #include <Wire.h>

Adafruit_NAU7802 nau7802;

// Calibration factor
float calibrationFactor =
    1.0; // Will be calculated based on the average of slopes

float getAverageReading(int numReadings) {
  float sum = 0;
  for (int i = 0; i < numReadings; i++) {
    while (!nau7802.available()) {
      delay(10);
    }
    sum += nau7802.read();
    delay(10); // Delay to allow the scale to settle
  }
  return sum / numReadings;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10); // wait for serial monitor to open
  }

  if (!nau7802.begin()) {
    Serial.println("Failed to find NAU7802 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("NAU7802 found!");

  nau7802.setLDO(NAU7802_3V0);         // Set LDO to 3.3V
  nau7802.setGain(NAU7802_GAIN_128);   // Set gain
  nau7802.setRate(NAU7802_RATE_80SPS); // Set samples per second
  
  // Take 10 readings to flush out readings
  for (int i = 0; i < 10; i++) {
    while (!nau7802.available()) delay(1);
    Serial.println(nau7802.read());
  }

  while (!nau7802.calibrate(NAU7802_CALMOD_INTERNAL)) {
    Serial.println("Failed to calibrate internal offset, retrying!");
    delay(1000);
  }

  while (!nau7802.calibrate(NAU7802_CALMOD_OFFSET)) {
    Serial.println("Failed to calibrate system offset, retrying!");
    delay(1000);
  }

  Serial.println("Calibrated everything");

 for (uint8_t i=0; i<10; i++) {
    while (! nau7802.available()) delay(1);
    Serial.println(nau7802.read());
  }

  float sum_slopes = 0;

  for (int i = 0; i < 3; i++) {
    Serial.print("Place known weight ");
    Serial.print(i + 1);
    Serial.println(
        " on the scale. Then type the weight (in grams) and press 'y'...");

    while (!Serial.available()) {
      delay(100);
    }

    float known_weight = Serial.parseFloat();

    float raw_reading = getAverageReading(50);
    float slope = raw_reading / known_weight;
    sum_slopes += slope;

    Serial.print("Known weight: ");
    Serial.println(known_weight);
    Serial.print("Raw reading: ");
    Serial.println(raw_reading);
    Serial.print("Slope: ");
    Serial.println(slope, 10);
    Serial.print("Sum of slopes: ");
    Serial.println(sum_slopes, 10);
  }

  // Calculate the average of the slopes
  calibrationFactor = sum_slopes / 3.0;
  Serial.print("Average calibration factor: ");
  Serial.println(calibrationFactor, 5);

  delay(3000);
}

void loop() {
  float weightReading = getAverageReading(10);
  Serial.println(weightReading);
  float weightInGrams = weightReading / calibrationFactor;
  Serial.print("Measured weight: ");
  Serial.print(weightInGrams, 1);
  Serial.println(" grams");
  delay(500);  // Read every second
}