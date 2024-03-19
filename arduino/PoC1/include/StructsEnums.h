#ifndef STRUCTS_ENUMS_H
#define STRUCTS_ENUMS_H

enum Commands {
  /*
  Commands enumumeration
  Used to identify the command sent from the host computer
  Must match the commands in the host computer code
 */
  /* Incoming */
  SET_MOTOR_SPEED = 1,
  SET_PID_VALUES = 2,
  SET_PRESSURE = 3,
  STOP = 4,
  HEATER_SETPOINT = 13,
  TARE = 14,
  START_PARTIAL_EXTRACTION = 15,
  START_FULL_EXTRACTION = 16,

  /* Outgoing */
  DUTY_CYCLE = 5,
  TARGET_PRESSURE = 6,
  WEIGHT_READING = 7,
  EXTRACTION_STOPPED = 8,
  PRESSURE_READING = 9,
  PROFILE_SELECTION = 10,
  SINE_PROFILE = 11,
  STATIC_PROFILE = 12,
  EXTRACTION_STARTED = 17,
  TEMPERATURE = 18
};

struct Datas {
  // Extraction Critical
  float pressure;
  float target;
  float weight;
  float dutyCycle;
  unsigned long extractionStartTime;

  // Temperature & Heater
  float temperature;
  bool heaterOn;

  // Diagnostic
  float speed;
  float position;
  float motorCurrent;
};

struct Flags {
  bool inExtraction;
  bool partialExtraction; // Extraction without preheat or retraction
  bool inPID;
  bool isHeating;
  bool tareRequested;
};

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

#endif // COMMON_H