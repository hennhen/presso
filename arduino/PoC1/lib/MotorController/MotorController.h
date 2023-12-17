// MotorController.h
#ifndef MotorController_H
#define MotorController_H

class MotorController {
public:
    virtual void setSpeed(short value) = 0; // Pure virtual function
    virtual void stop() = 0; // Stop the motor
    virtual ~MotorController() {} // Virtual destructor
};

#endif
