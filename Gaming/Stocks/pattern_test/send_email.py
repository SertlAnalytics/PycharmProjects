"""The first step is to create an SMTP object, each object is used for connection
with one server."""


import sertl_analytics.environment  # init some environment variables during load - for security reasons
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

fromaddr = "josef.sertl@web.de"
toaddr = "josef.sertl@gmx.ch"
password = os.environ['web.de_password']

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "SUBJECT OF THE EMAIL"

body = "TEXT YOU WANT TO SEND"

msg.attach(MIMEText(body, 'plain'))

filename = "trade_test.py"
attachment = open("trade_test.py", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename={}".format(filename))

msg.attach(part)

server = smtplib.SMTP('smtp.web.de', 587)
server.starttls()
server.login(fromaddr, password)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()