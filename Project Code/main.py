import os
import cv2
import numpy as np
import importlib.util
import time
from datetime import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import lcddriver
from datetime import date
import csv
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import pandas as pd
from unimail import umail as um
from casmail import cmail as cm


today = date.today()
dt_string = today.strftime("%d-%m-%Y")

Image_folder = "Images" + dt_string
file = os.path.exists(Image_folder)
if file:
    print("Image already created")
else:
    os.mkdir(Image_folder)

csv='Attendance' + dt_string+'.csv'
csvfile=os.path.isfile(csv)
if csvfile:
    print("Csv already created")
else:
    data = {'Name': [], 'Rollnumber': [], 'Email': [],
            'Dress': [], 'Time': []}
    pandas = pd.DataFrame(data)
    pandas.to_csv(csv, mode='a', index=False, header=True)

   
GPIO.setwarnings(False)

MODEL_NAME = "tflite"
GRAPH_NAME = "detect.tflite"
LABELMAP_NAME = "labelmap.txt"
min_conf_threshold = float(0.8)

pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

CWD_PATH = os.getcwd()
# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, MODEL_NAME, LABELMAP_NAME)
# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

if labels[0] == '???':
    del (labels[0])

else:
    interpreter = Interpreter(model_path="tflite/detect.tflite")
interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width=640
cap.set(4, 480)  # height=480

GPIO.setmode(GPIO.BOARD)
buzzer=37
redled=33
greenled=35

GPIO.setup(buzzer,GPIO.OUT)
GPIO.setup(greenled,GPIO.OUT)
GPIO.setup(redled,GPIO.OUT)
lcd = lcddriver.lcd()
reader = SimpleMFRC522()

def rfidread():
    id, text = reader.read()
    if len(text) !=48:
        lcd.lcd_clear()
        lcd.lcd_display_string("Place Your Rfid Again",2)
        lcd.lcd_display_string("        Again       ",3)
        return rfidread()
    else:
        return text
while 1:
    _, img = cap.read()    
    #cap = cv2.VideoCapture(0)
    #cap.set(3, 640)  # width=640
    #cap.set(4, 480)  # height=480
    #print('ba') 
    

    lcd.lcd_clear()
    lcd.lcd_display_string("Dress Code Detection", 1)
    lcd.lcd_display_string("Plus RFID", 2)
    lcd.lcd_display_string("Place Your RFID", 3)
    lcd.lcd_display_string(dt_string, 4)

    data=rfidread()

    name = data.split()[0]
    rollnumber = data.split()[1]
    email = data.split()[2]
    #print('a')

    lcd.lcd_clear()
    lcd.lcd_display_string("     Please Wait    ", 2)
    
    attendance=pd.read_csv(csv)
    if rollnumber in attendance.values:
        lcd.lcd_clear()
        lcd.lcd_display_string(rollnumber +" " +"Your", 1)
        lcd.lcd_display_string("Attendance", 2)
        lcd.lcd_display_string("is Already Marked", 3)
        lcd.lcd_display_string(":-)", 4)
        time.sleep(1)
        
    else:
        #if cap.isOpened():
            #_, frame = cap.read()
            #cap.release()  # releasing camera immediately after capturing picture
            #if _ and frame is not None:
        now = datetime.now()
        tm_string = now.strftime("%H:%M:%S")
        cv2.imwrite(Image_folder+'/'+rollnumber+'.jpg', img)
                              
        image = cv2.imread(Image_folder+'/'+rollnumber+'.jpg')  # imagesdtstringfolder/rollnumber.jpg
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]['index'])[0]  # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0]  # Confidence of detected objects
            # num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
        #print("c")

            # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                #print("pp")
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                #print("q")
                # Draw label
                object_name = labels[int(classes[i])]  # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i] * 100))  # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7,2)  # Get font size
                label_ymin = max(ymin, labelSize[1] + 10)  # Make sure not to draw label too close to top of window
                cv2.rectangle(image, (xmin, label_ymin - labelSize[1] - 10),(xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255),cv2.FILLED)  # Draw white box to put label text in
                cv2.putText(image, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0),2)  # Draw label text
                    # print("d")

                if object_name == "uniform" and int(scores[i] > 0.8):
                    lcd.lcd_clear()
                    lcd.lcd_display_string(name, 1)
                    lcd.lcd_display_string(rollnumber, 2)
                    lcd.lcd_display_string(email, 3)
                    lcd.lcd_display_string(object_name, 4)
                    GPIO.output(greenled,GPIO.HIGH)
                    
                    data = {'Name': [name], 'Rollnumber': [rollnumber], 'Email': [email],'Dress': [object_name],'Time': [tm_string]}
                    pandas = pd.DataFrame(data)
                    pandas.to_csv(csv, mode='a', index=False, header=False)

                    try:
                        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                        server.login("email", "password")
                        fromaddr = 'email'
                        toaddr = email
                        msg = MIMEMultipart("alternative")
                        msg['From'] = fromaddr
                        msg['To'] = toaddr
                        msg['Subject'] = 'This is the subject of my email'
                        body = 'This is the body of my email'
                        msg.attach(MIMEText(body))
                        files = ['Images' + dt_string + '/' + rollnumber + '.jpg']
                        html = um(name,rollnumber,tm_string,dt_string)
                        for filename in files:
                            attachment = open(filename, 'rb')
                            part = MIMEBase("application", "octet-stream")
                            part2 = MIMEText(html, "html")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
                            msg.attach(part)
                            msg.attach(part2)
                            msg = msg.as_string()
                            try:
                                server = smtplib.SMTP('smtp.gmail.com:587')
                                server.ehlo()
                                server.starttls()
                                server.login(fromaddr, 'password')
                                server.sendmail(fromaddr, toaddr, msg)
                                server.quit()
                                print('Email sent successfully')
                            except:
                                print("Email couldn't be sent")
                    except:
                        print("Internet not working")

                    #GPIO.output(greenled,GPIO.HIGH)
                    #GPIO.output(greenled,GPIO.HIGH)
                    #time.sleep(1)
                    GPIO.output(greenled,GPIO.LOW)
                    lcd.lcd_clear()
                else:
                    lcd.lcd_clear()
                    lcd.lcd_display_string(name, 1)
                    lcd.lcd_display_string(" " + rollnumber, 2)
                    lcd.lcd_display_string(email, 3)
                    lcd.lcd_display_string("Casual", 4)
                    GPIO.output(redled,GPIO.HIGH)
                    GPIO.output(buzzer,GPIO.HIGH)
                    data = {'Name': [name], 'Rollnumber': [rollnumber], 'Email': [email],
                                    'Dress': ["Casual"], 'Time': [tm_string]}
                    pandas = pd.DataFrame(data)
                    pandas.to_csv(csv, mode='a', index=False, header=False)

                    try:
                        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                        server.login("email", "password")
                        fromaddr = 'email'
                        toaddr = email
                        msg = MIMEMultipart("altervative")
                        msg['From'] = fromaddr
                        msg['To'] = toaddr
                        msg['Subject'] = 'This is the subject of my email'
                        body = 'This is the body of my email'
                        msg.attach(MIMEText(body))
                        files = ['Images' + dt_string + '/' + rollnumber + '.jpg']
                        html = cm(name,rollnumber,tm_string,dt_string)
                        for filename in files:
                            attachment = open(filename, 'rb')
                            part = MIMEBase("application", "octet-stream")
                            part2 = MIMEText(html, "html")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
                            msg.attach(part)
                            msg.attach(part2)
                            msg = msg.as_string()
                            try:
                                server = smtplib.SMTP('smtp.gmail.com:587')
                                server.ehlo()
                                server.starttls()
                                server.login(fromaddr, 'password')
                                server.sendmail(fromaddr, toaddr, msg)
                                server.quit()
                                print('Email sent successfully')
                            except:
                                print("Email couldn't be sent")
                    except:
                        print("Internet not working")


                    # turn on red light and buzzer for 2 seconds

                    #GPIO.output(redled,GPIO.HIGH)
                    #GPIO.output(buzzer,GPIO.HIGH)
                    #time.sleep(1)
                    lcd.lcd_clear()
                    GPIO.output(redled,GPIO.LOW)
                    GPIO.output(buzzer,GPIO.LOW)

            else:    
                lcd.lcd_clear()
                lcd.lcd_display_string(name, 1)
                lcd.lcd_display_string(" " + rollnumber, 2)
                lcd.lcd_display_string(email, 3)
                lcd.lcd_display_string("Casual", 4)
                GPIO.output(redled,GPIO.HIGH)
                GPIO.output(buzzer,GPIO.HIGH)
                data = {'Name': [name], 'Rollnumber': [rollnumber], 'Email': [email],
                                'Dress': ["Casual"], 'Time': [tm_string]}
                pandas = pd.DataFrame(data)
                pandas.to_csv(csv, mode='a', index=False, header=False)

                try:
        
                    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                    server.login("email", "password")
                    fromaddr = 'email'
                    toaddr = email
                    msg = MIMEMultipart("alternative")
                    msg['From'] = fromaddr
                    msg['To'] = toaddr
                    msg['Subject'] = 'This is the subject of my email'
                    body = 'This is the body of my email'
                    msg.attach(MIMEText(body))
                    files = ['Images' + dt_string + '/' + rollnumber + '.jpg']
                    html = cm(name,rollnumber,tm_string,dt_string)
                    for filename in files:
                        attachment = open(filename, 'rb')
                        part = MIMEBase("application", "octet-stream")
                        part2 = MIMEText(html, "html")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
                        msg.attach(part)
                        msg.attach(part2)
                        msg = msg.as_string()
                        try:
                            server = smtplib.SMTP('smtp.gmail.com:587')
                            server.ehlo()
                            server.starttls()
                            server.login(fromaddr, 'password')
                            server.sendmail(fromaddr, toaddr, msg)
                            server.quit()
                            print('Email sent successfully')
                        except:
                            print("Email couldn't be sent")
                except:
                    print("Internet not working")

                # turn on red light and buzzer for 2 seconds

                #GPIO.output(redled,GPIO.HIGH)
                #GPIO.output(buzzer,GPIO.HIGH)
                #time.sleep(1)
                lcd.lcd_clear()
                GPIO.output(redled,GPIO.LOW)
                GPIO.output(buzzer,GPIO.LOW)


            # All the results have been drawn on the image, now display the image
            cv2.imshow('Object detector', image)
            # Object detector window automatically will be closed in 1 sec
            if cv2.waitKey(1000):
                break

        # Clean up
        cv2.destroyAllWindows()

        # fnames = ['Name', 'Rollnumber', 'Email', 'Dress', 'Time']
        # writer = csv.DictWriter(f, fieldnames=fnames)
        # if not file_exists:
        # writer.writeheader()
        # writer.writerow({'Name': name, 'Rollnumber': rollnumber, 'Email': email, 'Dress': object_name,'Time': tm_string})
        
    #GPIO.output(buzzer,GPIO.LOW)
    #GPIO.output(redled,GPIO.LOW)
    #GPIO.output(greenled,GPIO.LOW)
    #print('aa')
        #buzzer=26
#redled=13
#greenled=19
#GPIO.setup(buzzer,GPIO.OUT)
#GPIO.setup(greenled,GPIO.OUT)
#GPIO.setup(redled,GPIO.OUT)
