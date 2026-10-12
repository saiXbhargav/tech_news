"""Stage 5: send the HTML email through Gmail SMTP (needs a Gmail App Password)."""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(subject: str, html_body: str) -> None:
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "")
    to = [a.strip() for a in os.getenv("EMAIL_TO", user).split(",") if a.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Morning Brief <{user}>"
    msg["To"] = ", ".join(to)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as server:
        server.login(user, password)
        server.sendmail(user, to, msg.as_string())
    print(f"  email sent to {', '.join(to)}")
