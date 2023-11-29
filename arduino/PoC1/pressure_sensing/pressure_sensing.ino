//This code works well

//Pin Assignment
#define pressurePin A0
#define pwmPin 6
#define dirPin 7

// Define global variables used for pressure sensing
int sensorValue = 0;
float pressure = 0.0;

// Function map the sensor value to a pressure range
float mapfloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

//Define variables for pressure sensor low pass filter
double cutOffHz = 10;
double euler = 2.718281828;
double pi = 3.141592654;
double beta = pow(euler, -2 * pi * cutOffHz * 0.001);
float pressureFilt = 0;
float pressurePrev = 0;

//Define Global Time Parameters
unsigned long currT = 0;
long prevT = 0;
float deltaT = 0;

//Define motor control parameters
int dir = HIGH;
int pwm = 0;

//Define PID Parameters
float pSet = 4;  //bar setpoint
float eintegral = 0;
float ePrev = 0;
float ederivative = 0;
float e = 0;
float u = 0;
float kp = 500;
float ki = 5;
float kd = 1;

void setup() {
  Serial.begin(9600);
  Serial.println("10s till start");
  delay(5000);
}

void loop() {

  //Set PID loop runtime
  checkTime();

  //Get Pressure Reading
  getPressure();

  //Set up PID Controller
  setPID();

  //Set Linear Actuator to Perform In Response to PID Controller
  setLA(u);

  // Report pressure and set sampling frequency to 1 ms


  //Serial.print(e);
  //Serial.print(" ");
  //Serial.print(ederivative);
  //Serial.print(" ");
  //Serial.print(u);
  //Serial.print(" ");
  //Serial.print(pwm);
  //Serial.print(" ");
  Serial.println(pressureFilt);
  delay(1);
}

void getPressure() {
  // read the analog in value:
  sensorValue = analogRead(pressurePin);

  // map it to the pressure range:
  pressure = mapfloat(sensorValue, 102.3, 920.7, 0, 17.24);

  // if pressure is negative, set it to 0
  if (pressure < 0) {
    pressure = 0.0;
  }
  pressureFilt = beta * pressurePrev + (1 - beta) * pressure;
  pressurePrev = pressureFilt;
}

void setLA(float u) {
  dir = HIGH;
  if (u < 0) {
    dir = LOW;
  }
  pwm = (int)fabs(u);
  if (pwm > 255) {
    pwm = 255;
  }
  digitalWrite(dirPin, dir);
  analogWrite(pwmPin, pwm);
}

void checkTime() {
  currT = micros();
  deltaT = ((float)(currT - prevT)) / 1.0e6;
  prevT = currT;


  //Safety loop,  turn everything off after 20s of runtime (excludes 10s delay at start)
  if (currT > 30 * 1.0e6) {
    while (true) {
      digitalWrite(dirPin, HIGH);
      analogWrite(pwmPin, 0);
    }
  }
}

void setPID() {
  e = pSet - pressureFilt;
  eintegral = eintegral + e * (deltaT);
  ederivative = (e - ePrev) / deltaT;
  u = kp * e + ki * eintegral + kd * ederivative;
  ePrev = e;
}
