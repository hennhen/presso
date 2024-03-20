#include "ExtractionProfile.h"
#include <Arduino.h>

ExtractionProfile::ExtractionProfile(TargetType t, unsigned long duration)
    : type(t), extractionDuration(duration), extractionFinished(true) {}

void ExtractionProfile::start(unsigned long currentTime) {
  startTime = currentTime;
  extractionFinished = false;
}

bool ExtractionProfile::isFinished(unsigned long timeNow) {
  // Serial1.printf("Time now: %lu, Start Time: %lu, Duration: %lu\n", timeNow,
  //                startTime, extractionDuration);
  if (timeNow - startTime >= extractionDuration) {
    extractionFinished = true; // No target after the extraction is finished
  }
  return extractionFinished;
}

float ExtractionProfile::getTarget(unsigned long currentTime) {
  // Check if the extraction is finished
  if (currentTime - startTime >= extractionDuration) {
    extractionFinished = true;
    return 0; // No target after the extraction is finished
  }
  switch (type) {
  case SINE_WAVE: {
    float timeInSeconds = (currentTime - startTime) / 1000.0;
    return params.sineWaveParams.amplitude *
               sin(2.0 * PI * params.sineWaveParams.frequency * timeInSeconds) +
           params.sineWaveParams.offset;
  }

  case STATIC: {
    return params.staticSetpoint;
  }
  case CUSTOM: {
    // Handle case where currentTime is before the first point
    currentTime -= startTime;
    if (currentTime <= params.customParams.points[0].time) {

      return params.customParams.points[0].pressure;
    }

    // Handle case where currentTime is after the last point
    int lastPointIndex = params.customParams.pointCount - 1;
    if (currentTime >=
        params.customParams.points[lastPointIndex].time) {
      return params.customParams.points[lastPointIndex].pressure;
    }

    // Find the two points between which currentTime falls
    for (int i = 0; i < lastPointIndex; i++) {
      if (currentTime >= params.customParams.points[i].time &&
          currentTime < params.customParams.points[i + 1].time) {
        // Perform linear interpolation
        float timeDelta = params.customParams.points[i + 1].time -
                          params.customParams.points[i].time;
        float pressureDelta = params.customParams.points[i + 1].pressure -
                              params.customParams.points[i].pressure;
        float fraction =
            (currentTime - params.customParams.points[i].time) /
            timeDelta;
        return params.customParams.points[i].pressure +
               fraction * pressureDelta;
      }
    }
  }
  case NO_PROFILE: {
    Serial1.println("No profile set");
    return 0;
  }
  }
  return 0; // Default return
}

void ExtractionProfile::setCustomParams(
    const std::vector<std::pair<float, float>> &points) {
  // Clear any existing points
  std::fill(std::begin(params.customParams.points),
            std::end(params.customParams.points), TimePressurePoint{0, 0});

  // Ensure we do not exceed the maximum number of points
  int count = points.size() > 6 ? 6 : points.size();
  params.customParams.pointCount = count;

  // Copy each point from the input vector to the params
  for (int i = 0; i < count; i++) {
    params.customParams.points[i].time =
        static_cast<unsigned long>(points[i].first * 1000);
    params.customParams.points[i].pressure = points[i].second;
  }
  Serial1.printf("Set %d custom points\n", count);
  // Print the points
  for (int i = 0; i < count; i++) {
    Serial1.printf("Time: %d, Pressure: %f\n",
                   params.customParams.points[i].time,
                   params.customParams.points[i].pressure);
  }
  extractionFinished = false;
}

void ExtractionProfile::setSineParameters(float amplitude, float frequency,
                                          float offset) {
  params.sineWaveParams.amplitude = amplitude;
  params.sineWaveParams.frequency = frequency;
  params.sineWaveParams.offset = offset;
  extractionFinished = false;
}

void ExtractionProfile::setRampingParameters(float maxPressure,
                                             unsigned long rampDuration,
                                             unsigned long holdDuration) {
  params.rampingParams.maxPressure = maxPressure;
  params.rampingParams.rampDuration = rampDuration;
  params.rampingParams.holdDuration = holdDuration;
}

void ExtractionProfile::setStaticPressure(float setpoint) {
  params.staticSetpoint = setpoint;
  extractionFinished = false;
}

void ExtractionProfile::setReady(bool ready) {
  extractionFinished = false;
  _isReady = ready;
}

void ExtractionProfile::reset() {
  _isReady = false;
  extractionFinished = true;
  startTime = 0;
  type = NO_PROFILE;
  extractionDuration = 0;
  params = {0};
}

bool ExtractionProfile::isReady() { return _isReady; }

String ExtractionProfile::getParams() {
  String params;
  params += "Type: ";
  params += type;
  params += "\n";
  params += "Duration: ";
  params += extractionDuration;
  params += "\n";
  return params;
}