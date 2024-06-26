#include "SerialCommunicator.h"
#include "StructsEnums.h"
#include <Arduino.h>

SerialCommunicator::SerialCommunicator(PacketSerial &packetSerial,
                                       PIDController &pid,
                                       ExtractionProfile &profile,
                                       RoboController &motor,
                                       HeaterController &heater)
    : pSerial(packetSerial), pidController(pid), extractionProfile(profile),
      motor(motor), heater(heater) {
  // Constructor implementation (if necessary)
}

void SerialCommunicator::setSendFrequency(uint8_t frequency) {
  _sendFrequency = frequency;
}

void SerialCommunicator::sendFloat(short command, float value) {
  uint8_t buffer[sizeof(short) + sizeof(float)];
  memcpy(buffer, &command, sizeof(short));
  memcpy(buffer + sizeof(short), &value, sizeof(float));
  pSerial.send(buffer, sizeof(buffer));
}

void SerialCommunicator::sendShort(short command, short value) {
  uint8_t buffer[sizeof(short) + sizeof(short)];
  memcpy(buffer, &command, sizeof(short));
  memcpy(buffer + sizeof(short), &value, sizeof(short));
  pSerial.send(buffer, sizeof(buffer));
}

void SerialCommunicator::sendData(const Datas &datas, bool pressure,
                                  bool target, bool weight, bool dutyCycle,
                                  bool temperature, bool heaterStatus,
                                  bool speed, bool position,
                                  bool motorCurrent) {
  if (millis() - _lastSendTime > _sendFrequency) {
    if (weight)
      sendFloat(WEIGHT_READING, datas.weight);
    if (pressure)
      sendFloat(PRESSURE_READING, datas.pressure);
    if (target) {
      sendFloat(TARGET_PRESSURE, datas.target);
    }
    if (temperature) {
      sendFloat(TEMPERATURE, datas.temperature);
    }
    if (motorCurrent) {
      sendFloat(MOTOR_CURRENT, datas.motorCurrent);
    }
    if (speed) {
      sendFloat(MOTOR_SPEED, datas.speed);
    }
    if (position) {
      sendFloat(MOTOR_POSITION, datas.position);
    }
    if (dutyCycle) {
      sendShort(DUTY_CYCLE, datas.dutyCycle);
    }

    _lastSendTime = millis();
  }
}

void SerialCommunicator::notifyHeaterStatus(bool on) {
  // Implementation of notifyHeaterStatus
  //   sendFloat(HEATER_STATUS, on ? 1.0f : 0.0f);
}

void SerialCommunicator::notifyExtractionStarted() {
  sendFloat(EXTRACTION_STARTED, 0.0f);
}

void SerialCommunicator::notifyExtractionStopped() {
  // Implementation of notifyExtractionStopped
  sendFloat(EXTRACTION_STOPPED, 0.0f);
}

// 0=fail, 1=sucess, 2 = start partial extraction, 3 = STOP, 4 = tare,
// 5 = heater off, 6 = heater on, 7 = do homing sequence
uint8_t SerialCommunicator::receiveCommands(const uint8_t *buffer,
                                            size_t size) {
  // Ensure the buffer has at least the size of a short (for the command)
  if (size < sizeof(short)) {
    // Handle error: not enough data to read a command
    return 0;
  }
  // Extract the command
  short command;
  memcpy(&command, buffer, sizeof(short));

  Serial1.printf("Received command: %d\n", command);

  // Switch on the command
  switch (command) {
  case SET_MOTOR_SPEED: {
    // Serial1.print("set motor speed: ");
    // Check if the size is correct (command + 1 float)
    if (size == sizeof(short) + sizeof(float)) {
      float speed;
      memcpy(&speed, buffer + sizeof(short), sizeof(float));
      short shortSpeed = (short)round(speed);
      // Serial1.println(shortSpeed);

      motor.setDutyCycle(speed);
      break;
    } else {
      // Invalid command
      return 0;
    }
    break;
  }
  case STOP:
    return 3;
    break;
  case HEATER_SETPOINT:
    // Handle heater setpoint command
    break;
  case TARE:
    return 4;
    break;
  case SET_PID_VALUES: {
    // Check if packet is 3 or 4 floats (4 is with sample time)
    if (size == sizeof(short) + 3 * sizeof(float)) {
      // Create variables to hold the PID values
      float p, i, d;

      // Extract the PID values
      memcpy(&p, buffer + sizeof(short), sizeof(float));
      memcpy(&i, buffer + sizeof(short) + sizeof(float), sizeof(float));
      memcpy(&d, buffer + sizeof(short) + 2 * sizeof(float), sizeof(float));

      pidController.setParameters(p, i, d);
      pidController.setReady(true);
      Serial1.printf("PID values set. P: %f, I: %f, D: %f\n", p, i, d);
      break;
    } else if (size == sizeof(short) + 4 * sizeof(float)) {
      // Sample time also set
      Serial1.println("Receiving PID values with sample time");
      float p, i, d, sampleTime;
      memcpy(&p, buffer + sizeof(short), sizeof(float));
      memcpy(&i, buffer + sizeof(short) + sizeof(float), sizeof(float));
      memcpy(&d, buffer + sizeof(short) + 2 * sizeof(float), sizeof(float));
      memcpy(&sampleTime, buffer + sizeof(short) + 3 * sizeof(float),
             sizeof(short));

      pidController.setParameters(p, i, d, (short)sampleTime);
      pidController.setReady(true);
      Serial1.printf("PID values set. P: %f, I: %f, D: %f, Sample Time: %d\n",
                     p, i, d, sampleTime);
      break;
    } else {
      pidController.setReady(false);
      return 0;
      break;
    }
    return 1;
  }

  case PROFILE_SELECTION: {
    // Check if the size is correct (command + 1 short)
    if (size >= sizeof(short)) {
      short profileType;
      memcpy(&profileType, buffer + sizeof(short), sizeof(short));

      // Determine the profile type and set the global profile object
      switch (profileType) {
      case SINE_PROFILE: {
        // Create and set a Sine Wave profile
        float amplitude, frequency, offset, duration;

        // Extract the parameters.
        // Buffer starts with command short, 3 floats,
        memcpy(&amplitude, buffer + 2 * sizeof(short), sizeof(float));
        memcpy(&frequency, buffer + 2 * sizeof(short) + sizeof(float),
               sizeof(float));
        memcpy(&offset, buffer + 2 * sizeof(short) + 2 * sizeof(float),
               sizeof(float));
        memcpy(&duration, buffer + 2 * sizeof(short) + 3 * sizeof(float),
               sizeof(float));

        Serial1.printf(
            "Sine parameters set: Amplitude: %f, Frequency: %f, Offset: %f, "
            "Duration: %f\n",
            amplitude, frequency, offset, duration);

        extractionProfile =
            ExtractionProfile(SINE_WAVE, static_cast<unsigned long>(duration));
        extractionProfile.setSineParameters(amplitude, frequency, offset);
        extractionProfile.setReady(true);
        break;
      }
        // case CUSTOM:
        //   // Create and set a Ramping profile
        //   extractionProfile = MyProfile(); // Replace with your profile class
        //   extractionProfile.setRampingParameters(9.0, 2000, 2000); // Set
        //   profile parameters break;

      case STATIC_PROFILE: {
        // Create and set a Static profile
        float pressure, duration;

        // buffer starts with command short, type short, 1 float, 1 short
        memcpy(&pressure, buffer + 2 * sizeof(short), sizeof(float));
        memcpy(&duration, buffer + 2 * sizeof(short) + sizeof(float),
               sizeof(float));
        Serial1.printf("Static parameters set: Pressure: %f, Duration: %f\n",
                       pressure, duration);

        extractionProfile = ExtractionProfile(
            STATIC, static_cast<unsigned long>(
                        duration)); // Replace with your profile class
        extractionProfile.setStaticPressure(pressure); // Set profile parameters
        extractionProfile.setReady(true);
        break;
      }

      case CUSTOM_PROFILE: {
        Serial1.println("Custom profile selected");
        // Extract the number of point pairs
        float numPointsFloat;
        memcpy(&numPointsFloat, buffer + 2 * sizeof(short), sizeof(float));
        int numPoints = static_cast<int>(numPointsFloat);
        Serial1.printf("Number of points: %d\n", numPoints);

        // Check if the buffer has enough data for all points
        if (size <
            sizeof(short) + sizeof(float) + numPoints * 2 * sizeof(float)) {
          Serial1.println("Not enough data for all points");
          return 0; // Not enough data for all points
        }
        // Extract the points
        std::vector<std::pair<float, float>> points;
        for (int i = 0; i < numPoints; ++i) {
          float x, y;
          memcpy(&x,
                 buffer + 2 * sizeof(short) + sizeof(float) +
                     i * 2 * sizeof(float),
                 sizeof(float));
          memcpy(&y,
                 buffer + 2 * sizeof(short) + sizeof(float) +
                     (i * 2 + 1) * sizeof(float),
                 sizeof(float));
          points.push_back(std::make_pair(x, y));
        }

        // for (const auto &point : points) {
        //   Serial1.printf("X: %f, Y: %f\n", point.first, point.second);
        // }

        // Duration is the last x value
        float duration = 1000 * points[numPoints - 1].first;

        // Cast to unsigned long
        unsigned long custom_duration = static_cast<unsigned long>(duration);
        Serial1.printf("Custom profile duration: %lu\n", custom_duration);
        extractionProfile = ExtractionProfile(CUSTOM, custom_duration);
        extractionProfile.setCustomParams(points);
        extractionProfile.setReady(true);
        // Assuming successful handling of the custom profile
        break;
      }
      default:
        Serial1.println("Invalid Profile Type");
        return 0;
        break;
      }
      return 1;
    }
    break;
  }
  case TEMPERATURE: {
    float temp;
    memcpy(&temp, buffer + sizeof(short), sizeof(float));
    Serial1.println(temp);
    heater.setTarget(temp);
    if (temp > 0) {
      return 6;
    } else {
      return 5;
    }
    break;
  }
  case DO_HOMING_SEQUENCE: {
    return 7;
    break;
  }
  case GOTO_POSITION_MM: {
    float position;
    memcpy(&position, buffer + sizeof(short), sizeof(float));
    Serial1.println(position);
    motor.moveToAbsMmPosition(position);
    return 1;
    break;
  }
  case START_PARTIAL_EXTRACTION:
    return 2;
    break;

  case CUSTOM_PROFILE:
    break;
  default:
    // Handle unknown command
    return 0;
    break;
  }
  // Broken out, success
  return 1;
}

// PIDController SerialCommunicator::createPIDObject(const std::vector<float>&
// data) {
//     // Implementation of createPIDObject
//     // Construct and return a PIDController object using the provided data
// }

// ExtractionProfile SerialCommunicator::createExtractionProfile(const
// std::vector<float>& data) {
//     // Implementation of createExtractionProfile
//     // Construct and return an ExtractionProfile object using the provided
//     data
// }