#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Servo.h>

// Define stepper motors and the pins they are connected to
AccelStepper stepper1(1, 2, 5); // Driver type: 1, STEP pin: 2, DIR pin: 5
AccelStepper stepper2(1, 4, 7); // Driver type: 1, STEP pin: 4, DIR pin: 7

MultiStepper steppersControl; // Create instance of MultiStepper


//init servos
Servo servo1; // Create first servo object
Servo servo2; // Create second servo object

const int servoPin1 = A7; // The pin where the first servo motor is attached
const int servoPin2 = A8; // The pin where the second servo motor is attached

unsigned long previousMillis1 = 0; // Will store the last time servo1 was updated
unsigned long previousMillis2 = 0; // Will store the last time servo2 was updated

long moveDuration1 = 3000; // Duration of servo1 movement in milliseconds
long moveDuration2 = 3000; // Duration of servo2 movement in milliseconds

int startAngle1 = 90; // Starting angle for first servo
int startAngle2 = 90; // Starting angle for second servo

int endAngle1 = 90; // Ending angle for first servo
int endAngle2 = 90; // Ending angle for second servo


long gotoposition[2]; // Array to store the target positions for each stepper motor
int temp1, temp2, temp3;
int maxSpeed1 = 500, maxSpeed2 = 1000;
int acceleration1 = 500, acceleration2 = 1000;
float stepAngle = 1.8;
int targetPosition1, targetPosition2; // Variables to store target positions
int stepsPerRevolution = 200; // Example value, adjust to your stepper's spec

void setup() {
    pinMode(8, OUTPUT); // Set the enable pin as output
    
    stepper1.setMaxSpeed(maxSpeed1); // Set maximum speed for the first stepper
    stepper2.setMaxSpeed(maxSpeed2); // Set maximum speed for the second stepper

    stepper1.setAcceleration(acceleration1);
    stepper2.setAcceleration(acceleration2);

    stepper1.setCurrentPosition(0);
    stepper2.setCurrentPosition(0);

    // Adding the steppers to the steppersControl instance
    steppersControl.addStepper(stepper1);
    steppersControl.addStepper(stepper2);

    // Attaching servos to pins
    servo1.attach(servoPin1); // Attaches the first servo on its pin
    servo2.attach(servoPin2); // Attaches the second servo on its pin


    Serial.begin(9600); // Start serial communication
    Serial.println("Arduino is ready");

    digitalWrite(8, LOW); // Enable the motors
}

void loop() {
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');

        int commaIndex1 = data.indexOf(',');
        temp1 = data.substring(0, commaIndex1).toInt();

        int commaIndex2 = data.indexOf(',', commaIndex1 + 1);
        temp2 = data.substring(commaIndex1 + 1, commaIndex2).toInt();

        temp3 = data.substring(commaIndex2 + 1).toInt();

        targetPosition1 = (temp1 * stepsPerRevolution) / 360; // Convert degrees to steps
        targetPosition2 = (temp2 * stepsPerRevolution) / 360;

        gotoposition[0] = targetPosition1;
        gotoposition[1] = targetPosition2;

        steppersControl.moveTo(gotoposition);
        steppersControl.runSpeedToPosition(); // Block until all steppers reach their target position

        moveServo(servo1, startAngle1, endAngle1, previousMillis1, moveDuration1);
        moveServo(servo2, startAngle2, endAngle2, previousMillis2, moveDuration2);

        //digitalWrite(8, HIGH); // Disable the motors

        Serial.println("Moved to position: " + String(temp1) + ", " + String(temp2));
    }
}


void moveServo(Servo &servo, int &startAngle, int &endAngle, unsigned long &previousMillis, long moveDuration) {
    unsigned long currentMillis = millis();

    if (startAngle != endAngle && currentMillis - previousMillis <= moveDuration) {
        float proportion = (float)(currentMillis - previousMillis) / (float)moveDuration;
        int currentAngle = startAngle + (int)(proportion * (endAngle - startAngle));
        servo.write(currentAngle);
    } else if (currentMillis - previousMillis > moveDuration) {
        startAngle = endAngle; // Update the start angle after movement is complete
        previousMillis = currentMillis;
    }
}
