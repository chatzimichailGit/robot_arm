#include <AccelStepper.h>
#include <MultiStepper.h>

// Define stepper motors and the pins they are connected to
AccelStepper stepper1(1, 2, 5); // First stepper motor (Driver type: with 2 pins, STEP, DIR)
AccelStepper stepper2(1, 4, 7); // Second stepper motor (Driver type: with 2 pins, STEP, DIR)
const int enablePin = 8; // Enable pin for both stepper motors

MultiStepper steppersControl;  // Create instance of MultiStepper
long gotoposition[2]; // An array to store the target positions for each stepper motor

void setup() {
  pinMode(enablePin, OUTPUT); // Set the enable pin as output
  digitalWrite(enablePin, HIGH); // Disable the motors

  stepper1.setMaxSpeed(1000); // Set maximum speed value for the first stepper
  stepper2.setMaxSpeed(1000); // Set maximum speed value for the second stepper

  // Adding the 2 steppers to the steppersControl instance for multi-stepper control
  steppersControl.addStepper(stepper1);
  steppersControl.addStepper(stepper2);

  Serial.begin(9600); // Start serial communication
  Serial.println("Enter positions for both steppers (format: position1 position2):");
}

void loop() {
  if (Serial.available() > 0) {
    String commandString = Serial.readStringUntil('\n');
    parseAndExecuteCommand(commandString);
    digitalWrite(enablePin, LOW); // Enable the motors
  }

  steppersControl.moveTo(gotoposition); // Calculates the required speed for all motors
  steppersControl.runSpeedToPosition(); // Blocks until all steppers are in position
}

void parseAndExecuteCommand(String command) {
  int firstSpaceIndex = command.indexOf(' ');
  if(firstSpaceIndex != -1) {
    long position1 = command.substring(0, firstSpaceIndex).toInt();
    long position2 = command.substring(firstSpaceIndex + 1).toInt();

    gotoposition[0] = position1;
    gotoposition[1] = position2;

    Serial.print("Stepper 1 moving to position ");
    Serial.println(position1);
    Serial.print("Stepper 2 moving to position ");
    Serial.println(position2);
  } else {
    Serial.println("Invalid command format");
  }
}