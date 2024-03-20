#ifndef ExtractionProfile_h
#define ExtractionProfile_h

#include "StructsEnums.h"
#include <Arduino.h>

class ExtractionProfile {
private:
  TargetType type;
  unsigned long extractionDuration;
  unsigned long startTime = 0;
  bool extractionFinished = false;
  Parameters params;
  bool _isReady = false;

public:
  ExtractionProfile(TargetType t, unsigned long duration);

  void start(unsigned long currentTime);
  bool isFinished(unsigned long currentTime);
  float getTarget(unsigned long currentTime);
  void reset();

  void setSineParameters(float amplitude, float frequency, float offset);
  void setRampingParameters(float maxPressure, unsigned long rampDuration,
                            unsigned long holdDuration);
  void setStaticPressure(float setpoint);

  String getParams();
  void setReady(bool ready);
  bool isReady();
};

#endif