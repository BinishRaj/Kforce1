import pysftp
import time
import os.path
import datetime as dt
import paramiko
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders

#Kforce SFTP server details
Hostname = "ftp.kforce.com"
Username = "workllama-prod"
Password = "RxX=01D8Bw2Q"

#The mail addresses and password
sender_address = 'kforce.workllama@gmail.com'
sender_pass = 'P@5sw0rd'
receiver_address = 'braj@workllama.com,jjose@workllama.com'

#Setup the MIME
message = MIMEMultipart()
message['From'] = sender_address
message['To'] = receiver_address

# Mail content
mail_content = '''Hello Team,
Please find the attached Kforce Referral Payment sheet for this week.
Thank You
'''
# The subject line
message['Subject'] = 'Kforce referral payment. It has an attachment.?'
# The body and the attachments for the mail
message.attach(MIMEText(mail_content, 'plain'))


ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=Hostname, username=Username, password=Password,allow_agent=False)
sftp_client = ssh_client.open_sftp()

print("Connection successfully established ... ")

# Switch to a remote directory
sftp_client.chdir('/download/PROD/Payments/')

# Obtain structure of the remote directory '/download/PROD/Payments/'
directory_structure = sftp_client.listdir_attr()

# Print data
for attr in directory_structure:
    print(attr.filename, attr)

for f in sorted(directory_structure, key=lambda k: k.st_mtime, reverse=True):
    sftp_client.get(f.filename, f.filename)
    modified = time.ctime(os.path.getmtime(f.filename))
    print("Last modified: %s" % modified)
    time_delta = time.time() - os.path.getmtime(f.filename)
    time_delta_days = time_delta / (60 * 60 * 24)
    print(time_delta_days)
    print(os.path.getmtime(f.filename))
    if time_delta_days < 5:
        print("The File copied is : %s" % f.filename)
        attach_file_name = f.filename
        with open(attach_file_name, 'rb') as file:
            message.attach(MIMEApplication(file.read(), Name=attach_file_name))
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

    break
sftp_client.close()
ssh_client.close()
