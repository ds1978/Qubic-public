import os
import json
import smtplib, ssl
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
scriptversion = "1.2.2"
scriptdate="20230220"
basepath = "/opt/qiner/mailreport"
hostname = socket.gethostname()

with open(basepath +"/config.json") as config:
    data = json.load(config)

logfilename = data['other']['logfilename'] 
logfilepath = logfilename
lastsolutionfilename = basepath + "/lastsolution.json"
lastsolutionfilepath = lastsolutionfilename

emailport = data['email']['emailport']  # For SSL
emailusername = data['email']['emailusername'] 
emailpassword = data['email']['emailpassword'] 
emailserver = data['email']['emailserver'] 
emailfromname = data['email']['emailfromname'] 
emailsender = data['email']['emailsender'] 
emailreceiver = data['email']['emailreceiver'] 

with open(logfilepath, 'r') as f:
    try:  # catch OSError in case of a one line file 
        lines = f.readlines()
        second_last_line = lines[-2]    
    except OSError:
        print('error')
    
    last_line = second_last_line
    last_line_split = last_line.split('|')
    if "solutions" in last_line_split[3]:
        with open(lastsolutionfilepath, 'r') as openfile:
            # Reading from json file
            json_object_in = json.load(openfile)
            solutionsfound_in = json_object_in.get('solutionsfound') 
        solutionsfounddate_new = last_line_split[1].strip(' ')
        solutionsfoundcount_new = last_line_split[3].strip(' ').strip(' solutions')
        its_speed = last_line_split[2].strip(' ')
        dictionary = {
            "date": last_line_split[1].strip(' '),
            "solutionsfound": solutionsfoundcount_new
        }

        if int(solutionsfoundcount_new) > int(solutionsfound_in):
            # Serializing json
            json_object = json.dumps(dictionary, indent=4)
            # Writing to sample.json
            with open(lastsolutionfilepath, "w") as outfile:
                outfile.write(json_object)
                outfile.close()
            # Create a secure SSL context
            emailmessage = MIMEMultipart("alternative")
            emailmessage["Subject"] = "qbic solution found:" + hostname
            emailmessage["From"] = emailsender
            emailmessage["To"] = emailreceiver
            emailmessagetxt = 'Scriptversion: ' + scriptversion + '\nHost: ' + hostname + '\nDate (utc): ' + str(solutionsfounddate_new) + "\nCount: " + str(solutionsfoundcount_new)+  "\nit/s: " + str(its_speed) 
            
            part1 = MIMEText(emailmessagetxt, "plain")
            #part2 = MIMEText(emailmessagetxt, "html")

            emailmessage.attach(part1)


            context = ssl.create_default_context()
            with smtplib.SMTP(emailserver, emailport) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(emailusername, emailpassword)
                server.sendmail(emailsender, emailreceiver, emailmessage.as_string())

