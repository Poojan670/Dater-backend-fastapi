from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from os.path import dirname, join
from dotenv import load_dotenv

load_dotenv()

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
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_template.html")


async def send_confirm_email(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="success_template.html")


async def forgot_password_mail(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="forgot_password.html")


async def reset_password_success(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_reset_confirm.html")


def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype='html',
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message, template_name='send_otp_mail.html')
    print("Done!")
