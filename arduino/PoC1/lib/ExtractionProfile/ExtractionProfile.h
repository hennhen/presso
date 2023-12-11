#ifndef ExtractionProfile_h
#define ExtractionProfile_h
#endif

#include <Arduino.h>

enum TargetType {
    SINE_WAVE,
    RAMPING,
    STATIC
};

// Union of all possible parameters for all target types
// Union is used to save memory, it only allocates enough memory for the largest member
union Parameters {
    struct {
        // Sine wave parameters
        float amplitude;
        float frequency;
        float offset;
    } sineWaveParams;

    struct {
        // Ramp up, hold, ramp down
        // Ramp up and down slope is the same and is calculated from the max pressure and ramp duration
        float maxPressure;
        unsigned long rampDuration;
        unsigned long holdDuration;
    } rampingParams;

    float staticSetpoint;
};

class ExtractionProfile {
private:
    TargetType type;
    unsigned long extractionDuration;
    unsigned long startTime;
    bool extractionFinished;
    Parameters params;

public:
    ExtractionProfile(TargetType t, unsigned long duration);

    void start(unsigned long currentTime);
    bool isFinished() const;
    float getTarget(unsigned long currentTime);

    void setSineParameters(float amplitude, float frequency, float offset);
    void setRampingParameters(float maxPressure, unsigned long rampDuration, unsigned long holdDuration);
    void setStaticPressure(float setpoint);
};
