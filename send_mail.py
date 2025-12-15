import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
load_dotenv()

#from linebot import LineBotApi, WebhookHandler
#from linebot.exceptions import InvalidSignatureError
#from linebot.models import MessageEvent, TextMessage, TextSendMessage
def send_email(image_path):
    # read address in env file
    fromaddr = os.getenv('FROMADDR')
    toaddr = os.getenv('TOADDR')
    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Motion Detected!"

    body = "Someone feel sad fear or angry.See the attached image."
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(image_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(image_path))

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "cxqg xdrw ryhn ltle")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

    print("motion detected!")

def send_line():
    pass