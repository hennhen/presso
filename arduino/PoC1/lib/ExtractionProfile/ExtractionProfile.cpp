#include "ExtractionProfile.h"
#include <Arduino.h>

ExtractionProfile::ExtractionProfile(TargetType t, unsigned long duration)
: type(t), extractionDuration(duration), extractionFinished(true) {
}

void ExtractionProfile::start(unsigned long currentTime) {
    startTime = currentTime;
    extractionFinished = false;
}

bool ExtractionProfile::isFinished() const {
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
            return params.sineWaveParams.amplitude * sin(2.0 * PI * params.sineWaveParams.frequency * timeInSeconds) + params.sineWaveParams.offset;
        }

        case RAMPING: {
            unsigned long elapsedTime = currentTime - startTime;
            if (elapsedTime < params.rampingParams.rampDuration) {
                // Ramping up
                return (params.rampingParams.maxPressure / params.rampingParams.rampDuration) * elapsedTime;
            } else if (elapsedTime < params.rampingParams.rampDuration + params.rampingParams.holdDuration) {
                // Holding
                return params.rampingParams.maxPressure;
            } else {
                // Ramping down
                return params.rampingParams.maxPressure - (params.rampingParams.maxPressure / params.rampingParams.rampDuration) * (elapsedTime - params.rampingParams.rampDuration - params.rampingParams.holdDuration);
            }
        }

        case STATIC: {
            return params.staticSetpoint;
        }
    }
    return 0; // Default return
}

void ExtractionProfile::setSineParameters(float amplitude, float frequency, float offset) {
    params.sineWaveParams.amplitude = amplitude;
    params.sineWaveParams.frequency = frequency;
    params.sineWaveParams.offset = offset;
}

void ExtractionProfile::setRampingParameters(float maxPressure, unsigned long rampDuration, unsigned long holdDuration) {
    params.rampingParams.maxPressure = maxPressure;
    params.rampingParams.rampDuration = rampDuration;
    params.rampingParams.holdDuration = holdDuration;
}

void ExtractionProfile::setStaticPressure(float setpoint) {
    params.staticSetpoint = setpoint;
}
