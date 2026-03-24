import os
import re
from celery import Celery
from flask_mail import Mail, Message
from flask import Flask

def make_celery():
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    celery = Celery(
        app.import_name,
        broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    )

    mail = Mail(app)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery, mail, app

celery, mail, flask_app = make_celery()

@celery.task
def send_email_task(to_email, city, packing_text):
    with flask_app.app_context():
        msg = Message(
            subject=f"🧳 Your Packing List for {city}",
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[to_email],
            body=f"Hi!\n\nHere's your packing list for {city}:\n\n{packing_text}\n\n— Travel Assistant"
        )
        mail.send(msg)