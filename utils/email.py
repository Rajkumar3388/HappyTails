from flask_mail import Message
from app import create_app, mail

def send_email(subject, recipients, body):
    app = create_app()
    with app.app_context():
        msg = Message(subject=subject, recipients=recipients)
        msg.body = body
        mail.send(msg)
