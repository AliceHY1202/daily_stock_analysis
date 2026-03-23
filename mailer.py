import os
import smtplib
from email.message import EmailMessage


def send_email(subject: str, body: str):
    sender = os.environ["MAIL_SENDER"]
    password = os.environ["MAIL_PASSWORD"]
    recipient = os.environ["MAIL_RECIPIENT"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
