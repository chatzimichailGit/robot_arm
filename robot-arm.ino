#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Servo.h>

AccelStepper stepper1(1, 2, 5);
AccelStepper stepper2(1, 4, 7);
MultiStepper steppersControl;

Servo servo1;
Servo servo2;

const int servoPin1 = A7;
const int servoPin2 = A8;

unsigned long previousMillis1 = 0;
unsigned long previousMillis2 = 0;

long moveDuration1 = 3000;
long moveDuration2 = 3000;

long gotoposition[2];
int temp1, temp2;
int maxSpeed1 = 500, maxSpeed2 = 1000;
int acceleration1 = 500, acceleration2 = 1000;
float stepAngle = 1.8;
int targetPosition1, targetPosition2;
int stepsPerRevolution = 200;

void setup() {
    pinMode(8, OUTPUT);
    
    stepper1.setMaxSpeed(maxSpeed1);
    stepper2.setMaxSpeed(maxSpeed2);

    stepper1.setAcceleration(acceleration1);
    stepper2.setAcceleration(acceleration2);

    stepper1.setCurrentPosition(0);
    stepper2.setCurrentPosition(0);

    steppersControl.addStepper(stepper1);
    steppersControl.addStepper(stepper2);

    servo1.attach(servoPin1);
    servo2.attach(servoPin2);

    Serial.begin(9600);
    Serial.println("Arduino is ready");

    digitalWrite(8, LOW);

    previousMillis1 = millis();
}

void loop() {
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');

        int commaIndex = data.indexOf(',');

        if (commaIndex != -1) {
            int temp1 = data.substring(0, commaIndex).toInt();
            int temp2 = data.substring(commaIndex + 1).toInt();

            targetPosition1 = (temp1 * stepsPerRevolution) / 360;
            targetPosition2 = (temp2 * stepsPerRevolution) / 360;

            gotoposition[0] = targetPosition1;
            gotoposition[1] = targetPosition2;

            steppersControl.moveTo(gotoposition);
            steppersControl.runSpeedToPosition();

            moveServo(servo1, temp1, moveDuration1);
            moveServo(servo2, temp2, moveDuration2);

            Serial.println("Moved to position: " + String(temp1) + ", " + String(temp2));
        } else {
            Serial.println("Invalid data received");
        }
    }
}

void moveServo(Servo &servo, int targetAngle, long moveDuration) {
    unsigned long currentMillis = millis();
    int currentAngle = servo.read();

    if (currentAngle != targetAngle) {
        float proportion = (float)(currentMillis - previousMillis1) / (float)moveDuration;
        int newAngle = currentAngle + (int)(proportion * (targetAngle - currentAngle));
        servo.write(newAngle);
    } else {
        previousMillis1 = currentMillis;
    }
}
