import os
import json
import smtplib, ssl
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from datetime import timedelta

scriptversion = "1.1.1"
scriptdate="20230223"
basepath = "/opt/qiner/mailreport"
timespan_minutes_max = 5

hostname = socket.gethostname()

with open(basepath +"/config.json") as config:
    data = json.load(config)

logfilenames = data['other']['logfilename'] 

emailport = data['email']['emailport']  # For SSL
emailusername = data['email']['emailusername'] 
emailpassword = data['email']['emailpassword'] 
emailserver = data['email']['emailserver'] 
emailfromname = data['email']['emailfromname'] 
emailsender = data['email']['emailsender'] 
emailreceiver = data['email']['emailreceiver'] 

for logfilename in logfilenames:

    with open(logfilename, 'r') as f:
        try:  # catch OSError in case of a one line file 
            lines = f.readlines()
            second_last_line = lines[-2]    
        except OSError:
            print('error')
    
    last_line = second_last_line
    last_line_split = last_line.split('|')
    if "solutions" in last_line_split[3]:
        dt= last_line_split[1].strip(' ')
        dateTimeLogline = datetime.strptime(dt,'%Y-%m-%d %H:%M:%S') 
        dateTimeNow = datetime.now()
        timedelta = dateTimeNow - dateTimeLogline
        timedeltaInMinutes = timedelta.total_seconds() / 60
        if timedeltaInMinutes > 5:
        # Create a secure SSL context
            emailmessage = MIMEMultipart("alternative")
            emailmessage["Subject"] = "qbic report Error:" + hostname
            emailmessage["From"] = emailfromname + " <" + emailsender +">"
            emailmessage["To"] = emailreceiver
            emailmessagetxt = 'Scriptversion: ' + scriptversion + '\nHost: ' + hostname + '\n' 
            emailmessagetxt += "LogfileName: " + logfilename + "\n"
            emailmessagetxt += "DateTimeLogline: " + str(dateTimeLogline) + "\n"
            emailmessagetxt += "timespan_minutes_max: " + str(timespan_minutes_max) + "\n"
            
            part1 = MIMEText(emailmessagetxt, "plain")
            #part2 = MIMEText(emailmessagetxt, "html")

            emailmessage.attach(part1)
            context = ssl.create_default_context()
            with smtplib.SMTP(emailserver, emailport) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(emailusername, emailpassword)
                server.sendmail(emailsender, emailreceiver, emailmessage.as_string())

