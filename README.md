# Raspberry Pi Attendance System with Object Detection
## Project Abstract:
This project is helpful for the organizations that require less staff and prefer automated systems in their organizations This is an attendance system integrated with object detection model This project completely automates the work of attendance and dress-code detection for any organization.
It is a Raspberry Pi based project integrated with an RFID reader and deep learning algorithm using python programming language,namely **SSD** which uses deep neural network for object detection and also compatable with mobile edge devices.
1. It detects the dress code of the person scanning the RFID card. After scanning, an image of the person is captured via Pi camera.
2. The object detection is performed, and the decision is taken based on the taken image. 
If the dress code which is trained in the model is detected, a green light is shown and the timestamps of the entry are emailed as a record to the student along with the captured image, which also specifically mentions if the detected person was in proper uniform or in casual. 
3. If a person scans by in a casual dress, a buzzer will be sounded and a red light will be shown, also sending the email to the student, mentioning that the scanned person who walked by was in a 
casual dress with the picture attached as proof.
4. Each day after 5:00 PM, the record of all the students who passed by scanning the RFID cards are sent to the admin and are deleted from the system.

## Project Features:
- RFID
- Object Detection
- Alarm Generation
- Emailing
- Record Generation

## Hardware Requirements:
- Raspberry Pi 4
- Raspberry Pi 4 Case with Cooling Fan
- IP Camera with 32GB Memory Card
- Pi Camera
- LCD I2C 20x4
- Buzzer and RGB LED
- Jumper Wires
- Raspberry Pi Power Supply
- HDMI Cable
- Resistors
 

## System Architecture Diagram
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/sad.jpg)
## UML Sequence Diagram
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/uml.png)
## Implementation Methodology
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/sdm.png)
## Hardware Integration Diagram:
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/connection%20wiring.jpg)
## Project Implementation Guide and UseFull Links
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/Email.png)
1. [How to Install OS in RPI](https://www.instructables.com/HOW-TO-INSTALL-RASPBIAN-OS-IN-YOUR-RASPBERRY-PI/)
2. [LCD Integration](https://www.electroniclinic.com/raspberry-pi-16x2-lcd-i2c-interfacing-and-python-programming/)
3. [RFID Integration](https://pimylifeup.com/raspberry-pi-rfid-rc522/)

## Final Result
### Project Model
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/model%201.jpg)
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/model%202.jpg)
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/model%204.jpg)
### Captured Picture
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/uniform.jpg)
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/casual.jpg)
### Email Output 
![alt text](https://github.com/NOMANSAEEDSOOMRO/Attendance-System/blob/main/Images/Email.png)









