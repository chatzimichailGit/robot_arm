# 3D Printed Robot Arm with OpenCV Finger Gesture Control

This repository contains the code and documentation for a 3D printed robot arm controlled through finger gesture recognition using OpenCV and MediaPipe.

## Features
- Hand tracking using MediaPipe
- Gesture/pose detection with OpenCV
- Inverse/forward kinematics (Python)
- Arduino control for robot servos
- Real-time control loop and user interface

## Structure
- `robot-arm.ino` - Arduino code for servo control
- `JACOBIAN.py` - Robot jacobian and inverse kinematics
- `movement.py` - Planned motion routines
- `finals/` - proof-of-concept hand tracking and control scripts
- `serialtest.py` - Serial communication helper script

## How to use
1. Set up the 3D printed arm hardware and servos.
2. Upload `robot-arm.ino` to the Arduino controller.
3. Run the Python tracking script to send angle commands over serial.
4. Open the webcam and perform gestures to move the arm.

## Goals
- Demonstrate hardware/software integration
- Showcase practical robotics with computer vision
- Provide a clean portfolio project for CV/LinkedIn

## License
MIT
