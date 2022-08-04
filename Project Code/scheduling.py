import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import schedule
import shutil
from os.path import basename
from zipfile import ZipFile
import time

def zipfile():
    with ZipFile("Images" + dt_string + '.zip', 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk("Images" + dt_string):
            for filename in filenames:
                # create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filePath, basename(filePath))

def automatedattendancemail():
    fromaddr = 
    toaddr =###Admin Email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'This is the subject of my email'
    body = 'This is the body of my email'
    msg.attach(MIMEText(body))
    files = ['Attendance' + dt_string + '.csv',"Images" + dt_string + '.zip']
    for filename in files:
        attachment = open(filename, 'rb')
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",f"attachment; filename= {filename}")
        msg.attach(part)
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

def deletefolderandzip():
    shutil.rmtree("Images"+dt_string)
    os.remove("Images"+dt_string+".zip")


schedule.every().day.at("16:25").do(zipfile)
schedule.every().day.at("16:30").do(automatedattendancemail)
schedule.every().day.at("16:45").do(deletefolderandzip)
while 1:

    schedule.run_pending()
    time.sleep(1)
