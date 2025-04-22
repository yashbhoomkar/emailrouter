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

def create_email(sender_email, recipient_email, subject, body, cc=None, bcc=None):
    """
    Create an email message.
    Args:
        sender_email (str): The sender's email address.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
        cc (list): List of CC recipients.
        bcc (list): List of BCC recipients.
    Returns:
        MIMEMultipart: The email message object.
    """
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        if cc:
            message["Cc"] = ", ".join(cc)
        message.attach(MIMEText(body, "plain"))
        return message
    except Exception as e:
        raise ValueError(f"Error creating email: {str(e)}")

def send_email(smtp_server, smtp_port, sender_email, app_password, recipient_email, message, cc=None, bcc=None):
    """
    Send an email using the Gmail SMTP server.
    Args:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        sender_email (str): The sender's email address.
        app_password (str): The app password for the sender's email.
        recipient_email (str): The recipient's email address.
        message (MIMEMultipart): The email message object.
        cc (list): List of CC recipients.
        bcc (list): List of BCC recipients.
    """
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, app_password)
            recipients = [recipient_email] + (cc or []) + (bcc or [])
            server.sendmail(sender_email, recipients, message.as_string())
            print(f"Email sent successfully to {recipient_email} (CC: {cc}, BCC: {bcc}).")
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Authentication failed. Check your email and app password.")
    except Exception as e:
        raise ValueError(f"Error sending email: {str(e)}")

def process_and_send_email(email_data):
    """
    Process the input JSON and send emails to the appropriate recipients.
    Args:
        email_data (dict): The email data in JSON format.
    """
    try:
        # Load environment variables
        credentials = load_env_variables()
        sender_email = credentials["email"]
        app_password = credentials["app_password"]

        # Extract email details from JSON
        email_id = email_data.get("EMAIL_ID", "Unknown")
        forward_to = email_data.get("FORWARD_TO", None)
        cc = clean_email_list(email_data.get("CC", []))
        bcc = clean_email_list(email_data.get("BCC", []))
        subject = f"Email ID {email_id} - Routed Email"
        body = f"Dear {forward_to},\n\nThis email has been routed to you based on the department and urgency.\n\nBest regards,\nAliceInTensorLand Team"

        # Create and send the email
        if forward_to:
            message = create_email(sender_email, forward_to, subject, body, cc, bcc)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            send_email(smtp_server, smtp_port, sender_email, app_password, forward_to, message, cc, bcc)
        else:
            print(f"Skipping email ID {email_id} as no 'FORWARD_TO' address is provided.")
    except Exception as e:
        print(f"An error occurred while processing email ID {email_data.get('EMAIL_ID', 'Unknown')}: {str(e)}")

def clean_email_list(email_list):
    """
    Clean the email list by removing 'empty' or handling empty lists.
    Args:
        email_list (list): The list of email addresses.
    Returns:
        list: A cleaned list of email addresses.
    """
    if not email_list or email_list == ["empty"]:
        return []
    return email_list

def main():
    """
    Main function to process and send emails from JSON input.
    """
    # Example JSON input
    email_json_1 = {
        "EMAIL_ID": "1",
        "DEPARTMENT": "FINANCE",
        "URGENCY": "HIGHEST",
        "FORWARD_TO": "bob.smith@aliceintensorland.com",
        "CC": ["empty"],
        "BCC": ["empty"]
    }

    email_json_2 = {
        "EMAIL_ID": 1,
        "DEPARTMENT": "FINANCE",
        "URGENCY": "MEDIUM",
        "FORWARD_TO": "alice.smith@aliceintensorland.com",
        "CC": ["bob.smith@aliceintensorland.com"],
        "BCC": []
    }

    # Process and send emails
    for email_json in [email_json_1, email_json_2]:
        print("\nProcessing new email...")
        process_and_send_email(email_json)

if __name__ == "__main__":
    main()