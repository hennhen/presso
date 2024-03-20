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
  // GOTO_POSITION_MM = 23,
  SET_PID_VALUES = 2,
  GOTO_POSITION_MM = 3,
  STOP = 4,
  HEATER_SETPOINT = 13,
  TARE = 14,
  START_PARTIAL_EXTRACTION = 15,
  CUSTOM_PROFILE = 16,
  DO_HOMING_SEQUENCE = 22,

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
  TEMPERATURE = 18,
  MOTOR_CURRENT = 19,
  MOTOR_SPEED = 20,
  MOTOR_POSITION = 21
};

struct Datas {
  // Extraction Critical
  float pressure;
  float target;
  float weight;
  short dutyCycle;
  unsigned long extractionStartTime;

  // Temperature & Heater
  float temperature;
  bool heaterOn;

  // Diagnostic
  int speed;
  long position;
  float motorCurrent;
};

struct Flags {
  bool inExtraction;
  bool partialExtraction; // Extraction without preheat or retraction
  bool inPID;
  bool isHeating;
  bool tareRequested;
  bool homing;
};

enum TargetType { NO_PROFILE, SINE_WAVE, CUSTOM, STATIC };

struct TimePressurePoint {
    unsigned long time;   // Time in seconds
    float pressure; // Pressure at that time
};

// Union of all possible parameters for all target types
// Union is used to save memory, it only allocates enough memory for the largest
// member
union Parameters {
  struct {
    // Sine wave parameters
    float amplitude;
    float frequency;
    float offset;
  } sineWaveParams;

  struct {
    // Ramp up, hold, ramp down
    // Ramp up and down slope is the same and is calculated from the max
    // pressure and ramp duration
    float maxPressure;
    unsigned long rampDuration;
    unsigned long holdDuration;
  } rampingParams;

  struct {
    TimePressurePoint points[6]; // Maximum of 6 points for simplicity
    int pointCount;           // How many points are actually used

  } customParams;

  float staticSetpoint;
};

#endif // COMMON_H