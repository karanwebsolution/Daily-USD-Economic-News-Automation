import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from logger import logger
from config import config

class EmailSender:
    def __init__(self):
        self.smtp_email = config.SMTP_EMAIL
        self.smtp_password = config.SMTP_PASSWORD
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.recipient = config.RECIPIENT_EMAIL

    def send_report(self, html_content: str, subject: str) -> bool:
        """Send HTML email report via Gmail SMTP."""
        if not all([self.smtp_email, self.smtp_password, self.recipient]):
            logger.error("SMTP configuration incomplete.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_email
            msg["To"] = self.recipient

            # Attach HTML part
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}...")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {self.recipient}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Check Gmail App Password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False