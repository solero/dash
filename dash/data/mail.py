from dash import app
from dash.data import db
from email.mime.text import MIMEText

from sendgrid import Mail, SendGridAPIClient
from smtplib import SMTP_SSL, SMTP

class PenguinPostcard(db.Model):
    __tablename__ = 'penguin_postcard'

    id = db.Column(db.Integer, primary_key=True,
                   server_default=db.text("nextval('\"penguin_postcard_id_seq\"'::regclass)"))
    penguin_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                           index=True)
    sender_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    postcard_id = db.Column(db.ForeignKey('postcard.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    send_date = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    details = db.Column(db.String(255), nullable=False, server_default=db.text("''::character varying"))
    has_read = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))

def sendEmail(to_emails, subject, html_content):
    if app.config.EMAIL_METHOD == 'SENDGRID':
        message = Mail(
            from_email=app.config.FROM_EMAIL,
            to_emails=to_emails,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(app.config.SENDGRID_API_KEY)
        sg.send(message)
        return

    if app.config.EMAIL_METHOD != 'SMTP':
        return

    msg = MIMEText(html_content, 'html')
    msg['Subject'] = subject
    msg['From'] = app.config.FROM_EMAIL

    smtp_class = SMTP_SSL if app.config.SMTP_SSL else SMTP

    with smtp_class(app.config.SMTP_HOST, app.config.SMTP_PORT) as conn:
        conn.set_debuglevel(False)
        conn.login(app.config.SMTP_USER, app.config.SMTP_PASS)
        conn.sendmail(app.config.FROM_EMAIL, to_emails, msg.as_string())
