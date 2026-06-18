import os
import re
from celery import Celery
from flask_mail import Mail, Message
from flask import Flask

def make_celery():
    app = Flask(__name__) #Celery needs a Flask app context to use Flask-Mail.
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
    # broker — where Celery picks up tasks from (Redis). Think post box address.
    # backend — where Celery stores task results (also Redis).
    # So you can check if a task succeeded or failed later.

    mail = Mail(app)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # this ensures every Celery task runs inside that flask context automatically.

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
# @celery.task is what registers this function as a background task.
# Without that decorator it's just a regular function.