import smtplib
import os
import redis
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

def load_env_variables():
    """
    Load environment variables from the .env file.
    Returns:
        dict: A dictionary containing email credentials.
    """
    env_path = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/email_extraction/.env"
    load_dotenv(dotenv_path=env_path)
    
    email = os.getenv("EMAIL")
    app_password = os.getenv("APP_PASSWORD")
    if not email or not app_password:
        raise ValueError("EMAIL or APP_PASSWORD is missing in the .env file.")
    return {"email": email, "app_password": app_password}

def connect_to_redis(host="localhost", port=6379, decode_responses=True):
    """
    Connect to the Redis server.
    Returns:
        redis.StrictRedis: Redis client connection.
    """
    try:
        redis_client = redis.StrictRedis(host=host, port=port, decode_responses=decode_responses)
        return redis_client
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

def retrieve_email_from_redis(redis_client, email_id):
    """
    Retrieve email data from Redis.
    Args:
        redis_client (redis.StrictRedis): Redis client connection.
        email_id (str): The email ID to retrieve.
    Returns:
        dict: The email data or None if not found.
    """
    try:
        redis_key = f"email:{email_id}"
        email_data = redis_client.get(redis_key)
        if email_data:
            return json.loads(email_data)
        else:
            print(f"No email found in Redis for email ID '{email_id}'.")
            return None
    except Exception as e:
        raise ValueError(f"Failed to retrieve email data from Redis for email ID '{email_id}': {str(e)}")

def check_attachments(attachments_folder, attachment_paths):
    """
    Check and retrieve attachment files.
    Args:
        attachments_folder (str): The base folder for attachments.
        attachment_paths (list): List of attachment file paths.
    Returns:
        list: List of valid attachment file paths.
    """
    valid_attachments = []
    for attachment in attachment_paths:
        attachment_path = os.path.join(attachments_folder, attachment)
        if os.path.exists(attachment_path):
            valid_attachments.append(attachment_path)
        else:
            print(f"Attachment not found: {attachment_path}")
    return valid_attachments

def create_email(sender_email, recipient_email, subject, body, cc=None, bcc=None, attachments=None):
    """
    Create an email message with optional attachments.
    Args:
        sender_email (str): The sender's email address.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
        cc (list): List of CC recipients.
        bcc (list): List of BCC recipients.
        attachments (list): List of file paths for attachments.
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

        # Attach files
        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(file_path)}",
                )
                message.attach(part)

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
            server.starttls()
            server.login(sender_email, app_password)
            recipients = [recipient_email] + (cc or []) + (bcc or [])
            server.sendmail(sender_email, recipients, message.as_string())
            print(f"Email sent successfully to {recipient_email} (CC: {cc}, BCC: {bcc}).")
    except Exception as e:
        raise ValueError(f"Error sending email: {str(e)}")

def process_and_send_email(email_json, redis_client, attachments_folder):
    """
    Process the input JSON, fetch email content from Redis, and send the email with attachments.
    Args:
        email_json (dict): The email data in JSON format.
        redis_client (redis.StrictRedis): Redis client connection.
        attachments_folder (str): The base folder for attachments.
    """
    try:
        # Extract EMAIL_ID from the JSON
        email_id = email_json.get("EMAIL_ID")
        if not email_id:
            print("EMAIL_ID is missing in the input JSON.")
            return

        # Retrieve email content from Redis
        email_data = retrieve_email_from_redis(redis_client, email_id)
        if not email_data:
            print(f"Skipping email ID '{email_id}' as it is not found in Redis.")
            return

        # Extract email details
        forward_to = email_json.get("FORWARD_TO")
        cc = clean_email_list(email_json.get("CC", []))
        bcc = clean_email_list(email_json.get("BCC", []))
        subject = email_data.get("subject", "No Subject")
        body = email_data.get("body", "No Body")
        attachment_paths = email_data.get("attachments", [])

        # Check and retrieve valid attachments
        attachments = check_attachments(attachments_folder, attachment_paths)

        # Load environment variables
        credentials = load_env_variables()
        sender_email = credentials["email"]
        app_password = credentials["app_password"]

        # Create and send the email
        if forward_to:
            message = create_email(sender_email, forward_to, subject, body, cc, bcc, attachments)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            send_email(smtp_server, smtp_port, sender_email, app_password, forward_to, message, cc, bcc)
        else:
            print(f"Skipping email ID '{email_id}' as no 'FORWARD_TO' address is provided.")
    except Exception as e:
        print(f"An error occurred while processing email ID '{email_json.get('EMAIL_ID', 'Unknown')}': {str(e)}")

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
    Main function to process and send emails.
    """
    # Connect to Redis
    redis_client = connect_to_redis()

    # Define attachments folder
    attachments_folder = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/email_extraction/attachments"

    # Example JSON input
    email_json = {'EMAIL_ID': 6, 'DEPARTMENT': 'SOFTWARE', 'URGENCY': 'LOW', 'FORWARD_TO': 'ivy.lee@aliceintensorland.com', 'CC': ['hank.green@aliceintensorland.com'], 'BCC': []}

    # Process and send the email
    process_and_send_email(email_json, redis_client, attachments_folder)

if __name__ == "__main__":
    main()