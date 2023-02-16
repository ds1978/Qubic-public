import os
import json
import smtplib, ssl
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

hostname = socket.gethostname()

with open("config.json") as config:
    data = json.load(config)

logfilename = data['other']['logfilename'] 
logfilepath = logfilename
lastsolutionfilename = "lastsolution.json"
lastsolutionfilepath = lastsolutionfilename

emailport = data['email']['emailport']  # For SSL
emailusername = data['email']['emailusername'] 
emailpassword = data['email']['emailpassword'] 
emailserver = data['email']['emailserver'] 
emailfromname = data['email']['emailfromname'] 
emailsender = data['email']['emailsender'] 
emailreceiver = data['email']['emailreceiver'] 

with open(logfilepath, 'rb') as f:
    try:  # catch OSError in case of a one line file 
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
    except OSError:
        f.seek(0)
    last_line = f.readline().decode()
    last_line_split = last_line.split('|')
    if "solutions" in last_line_split[3]:
        with open(lastsolutionfilepath, 'r') as openfile:
            # Reading from json file
            json_object_in = json.load(openfile)
            solutionsfound_in = json_object_in.get('solutionsfound') 
        solutionsfounddate_new = last_line_split[1].strip(' ')
        solutionsfoundcount_new = last_line_split[3].strip(' ').strip(' solutions')
        solutionsfoundcount_new = 98
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
            emailmessage["Subject"] = "qbic solution sound"
            emailmessage["From"] = emailsender
            emailmessage["To"] = emailreceiver
            emailmessagetxt = 'new solution found \nHost: ' + hostname + '/nDateDate: ' + str(solutionsfounddate_new) + "\nCount: " + str(solutionsfoundcount_new) 
            
            part1 = MIMEText(emailmessagetxt, "plain")
            #part2 = MIMEText(emailmessagetxt, "html")

            emailmessage.attach(part1)


            context = ssl.create_default_context()
            with smtplib.SMTP(emailserver, emailport) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(emailusername, emailpassword)
                server.sendmail(emailsender, emailreceiver, emailmessage.as_string())
