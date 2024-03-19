//
//    FILE: MAX6675_test.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: demo
//    DATE: 2022-01-12
//     URL: https://github.com/RobTillaart/MAX6675


#include "MAX6675.h"

const int dataPin   = 19;
const int clockPin  = 18;
const int selectPin = 5;


MAX6675 thermoCouple(selectPin, dataPin, clockPin);

uint32_t start, stop;


void setup()
{
  Serial.begin(115200);
  Serial.println(__FILE__);
  Serial.print("MAX6675_LIB_VERSION: ");
  Serial.println(MAX6675_LIB_VERSION);
  Serial.println();
  delay(250);

  SPI.begin();

  thermoCouple.begin();
  thermoCouple.setSPIspeed(4000000);
  thermoCouple.setOffset(-7.0);
}

void loop()
{
  delay(100);
  start = micros();
  int status = thermoCouple.read();
  stop = micros();
  float temp = thermoCouple.getTemperature();

  Serial.print(millis());
  Serial.print("\tstatus: ");
  Serial.print(status);
  Serial.print("\ttemp: ");
  Serial.print(temp);
  Serial.print("\tus: ");
  Serial.println(stop - start);

  delay(400);
}
//  -- END OF FILE --