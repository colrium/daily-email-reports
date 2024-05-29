import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def send_email():
    # Email account credentials
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL")
    cc_emails = os.getenv("CC_EMAILS").split(",")

    # Prompt for the day's tasks
    tasks = input("Enter today's tasks: ")

    # Capture the current date and format it
    current_date = datetime.now().strftime("%d-%b-%Y")

    # Prompt for the subject with a default value
    default_subject = f"Tasks for {current_date} - Mutugi (WFH)"
    subject = (
        input(f"Enter the email subject (default: '{default_subject}'): ")
        or default_subject
    )

    # Email content
    body = f"Today's tasks:\n{tasks}"

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Cc"] = ", ".join(cc_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Get all recipients (to + cc)
    recipients = [to_email] + cc_emails

    # Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, recipients, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Schedule the email to be sent every day at a specific time
schedule.every().day.at("09:00").do(send_email)

print("Scheduler started. Waiting to send the email...")
while True:
    schedule.run_pending()
    time.sleep(1)
