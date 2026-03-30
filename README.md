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

## Project story
- Co-developed the robotic arm with my teammate `kpassias`, contributing to the mechanical design, the kinematic model, and the integration of the full system from software to hardware.
- Derived the forward and inverse kinematics for the arm to understand its motion and support the control design, even though the inverse model was not required in the final control path.
- Built and assembled the physical prototype using 3D-printed parts, stepper motors, belts, planetary gearing, and an Arduino CNC shield to drive the actuators.
- Worked across electronics, programming, mechanical integration, wiring, and final assembly, making this a multidisciplinary robotics project rather than only a software demo.

## What I learned
- Applied robotics fundamentals by moving from kinematic modeling into practical actuator control and hardware constraints.
- Gained hands-on experience with Arduino-based motion control, CNC shield motor driving, and the mechanical tradeoffs of belts and gearing in a real prototype.
- Learned how computer vision, embedded control, and physical assembly have to work together for a robotic system to behave reliably.

## License
MIT
