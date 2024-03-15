//
//    FILE: ADS_differential.ino
//  AUTHOR: Rob.Tillaart
// PURPOSE: read differential
//     URL: https://github.com/RobTillaart/ADS1X15

//  test 1
//  connect 2 potmeters in series
//
//  GND ---[   x   ]------[   y   ]---- 5V
//             |              |
//
//  measure at x and y  (connect to AIN0 and AIN1). 
//  x should be lower or equal to y

//  test 2
//  connect 2 potmeters parallel
//
//  GND ---[   x   ]------ 5V
//             |
//
//  GND ---[   y   ]------ 5V
//             |
//
//  measure at x and y  (connect to AIN0 and AIN1).
//  range from -VDD .. +VDD are possible

#include <ADS1X15.h>

ADS1115 ADS(0x48);

float voltageToBars(float voltage) {
    // Sensor outputs 0.5V at 0 bars and 4.5V at 17.24 bars
    const float minVoltage = 0.5; // Minimum voltage output at 0 bars
    const float maxVoltage = 4.5; // Maximum voltage output at 17.24 bars
    const float minPressure = 0.0; // Minimum pressure in bars
    const float maxPressure = 17.24; // Maximum pressure in bars

    // Direct conversion of voltage to pressure in bars without clamping
    float pressure = ((voltage - minVoltage) * (maxPressure - minPressure)) / (maxVoltage - minVoltage) + minPressure;
    return pressure;
}

void setup() 
{
  Serial.begin(250000);
  Serial.println(__FILE__);
  Serial.print("ADS1X15_LIB_VERSION: ");
  Serial.println(ADS1X15_LIB_VERSION);

  Wire.begin();

  ADS.begin();
  ADS.setGain(0);
  ADS.setDataRate(6); // 475 SPS
}


void loop() 
{
  unsigned long startTime = micros(); // Start time for loop execution
  ADS.requestADC_Differential_0_1();
  int16_t val_01 = ADS.getValue();
  float volts_01 = 5.0 + ADS.toVoltage(val_01); 

  // Serial.print("\t"); Serial.print(volts_01, 3); 
  Serial.print("\t"); Serial.println(voltageToBars(volts_01), 3);
  Serial.println();

  unsigned long endTime = micros(); // End time for loop execution
  Serial.println(endTime - startTime); 
  
  // delay(200); // Uncomment if delay is needed
}


//  -- END OF FILE --
