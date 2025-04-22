import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def load_env_variables():
    """
    Load environment variables from the .env file.
    Returns:
        dict: A dictionary containing email credentials.
    """
    # Specify the path to the .env file
    env_path = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/email_extraction/.env"
    load_dotenv(dotenv_path=env_path)
    
    email = os.getenv("EMAIL")
    app_password = os.getenv("APP_PASSWORD")
    if not email or not app_password:
        raise ValueError("EMAIL or APP_PASSWORD is missing in the .env file.")
    return {"email": email, "app_password": app_password}

def create_email(sender_email, recipient_email, subject, body):
    """
    Create an email message.
    Args:
        sender_email (str): The sender's email address.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
    Returns:
        MIMEMultipart: The email message object.
    """
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        return message
    except Exception as e:
        raise ValueError(f"Error creating email: {str(e)}")

def send_email(smtp_server, smtp_port, sender_email, app_password, recipient_email, message):
    """
    Send an email using the Gmail SMTP server.
    Args:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        sender_email (str): The sender's email address.
        app_password (str): The app password for the sender's email.
        recipient_email (str): The recipient's email address.
        message (MIMEMultipart): The email message object.
    """
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"Email sent successfully to {recipient_email}.")
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Authentication failed. Check your email and app password.")
    except Exception as e:
        raise ValueError(f"Error sending email: {str(e)}")

def main():
    """
    Main function to send a test email.
    """
    try:
        # Load environment variables
        credentials = load_env_variables()
        sender_email = credentials["email"]
        app_password = credentials["app_password"]

        # Email details
        recipient_email = "yash31204testing@gmail.com"
        subject = "Test Email from AliceInTensorLand"
        body = "Hello,\n\nThis is a test email sent from the AliceInTensorLand email system.\n\nBest regards,\nAliceInTensorLand Team"

        # Create email
        message = create_email(sender_email, recipient_email, subject, body)

        # Send email
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        send_email(smtp_server, smtp_port, sender_email, app_password, recipient_email, message)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()