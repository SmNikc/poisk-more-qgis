import smtplib
from email.mime.text import MIMEText
class EmailManager:
def send(self, to, subject, body):
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = "sender@example.com"
msg['To'] = to
with smtplib.SMTP('smtp.example.com') as server:
server.login("user", "pass")
server.sendmail(msg['From'], [to], msg.as_string())