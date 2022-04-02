from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from os.path import dirname, join
from dotenv import load_dotenv

load_dotenv()

# this will be the location of the current .py file
current_dir = dirname(__file__)
templates = join(current_dir, 'templates')

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=os.getenv("MAIL_PORT"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


html = """
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Otp Verification</title>
        </head>
        <body>
            <h1>Otp Verification</h1>
            <hr>
            <small>Hello</small>
            <small>Thank you for your registration, Please Use the following OTP for verification</small>

            <p>Your Otp is <span style="font-weight: bolder; font-size: larger; background-color: rgb(230, 233, 236); padding: 4px;">{{ otp }}</span></p>

            <p>This otp is valid for 5 minutes only..</p>
            <em>Thank you</em><br/>
            <em>Team <b>Code Asterisk</b></em>

        </body>
        </html>
        """


async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=str(body),
        subtype='html',
    )
    fm = FastMail(conf)
    await fm.send_message(message)


def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        # subtype='html',
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message, template_name='email.html')
    print("Done!")
