import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
import logging

def ensure_log_file_exists(log_dir, log_file):
    """Ensure the log file exists in the specified directory."""
    os.makedirs(log_dir, exist_ok=True)  # Create the directory if it doesn't exist
    log_file_path = os.path.join(log_dir, log_file)
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as f:
            f.write("")  # Create an empty log file
    return log_file_path

# Configure logging
def configure_logging():
    """Configure logging for the application."""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    log_file = "email_processing.log"
    log_file_path = ensure_log_file_exists(log_dir, log_file)
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def load_env_variables():
    """Load environment variables from the .env file."""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    email_address = os.getenv('EMAIL')  # Renamed from 'email' to 'email_address'
    app_password = os.getenv('APP_PASSWORD')
    if not email_address or not app_password:
        raise ValueError("EMAIL or APP_PASSWORD is not set in the .env file.")
    return email_address, app_password

def connect_to_imap(email_address, app_password):
    """Connect to the Gmail IMAP server and login."""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(email_address, app_password)
    logging.info("Connected to IMAP server.")
    return imap

def select_mailbox(imap, mailbox="inbox"):
    """Select the mailbox to use."""
    imap.select(mailbox)
    logging.info(f"Selected mailbox: {mailbox}")

def search_emails(imap, criteria="ALL"):
    """Search for emails based on the given criteria."""
    status, messages = imap.search(None, criteria)
    if status != "OK":
        raise Exception("Failed to search emails.")
    email_ids = messages[0].split()
    logging.info(f"Found {len(email_ids)} emails matching criteria: {criteria}")
    return email_ids

def fetch_email(imap, email_id):
    """Fetch a single email by its ID."""
    res, msg_data = imap.fetch(email_id, "(RFC822)")
    if res != "OK":
        raise Exception(f"Failed to fetch email with ID {email_id}.")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            return email.message_from_bytes(response_part[1])
    return None

def decode_subject(msg):
    """Decode the subject of an email."""
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    return subject

def process_email_body(msg):
    """Extract the body of an email."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                except:
                    pass
    else:
        body = msg.get_payload(decode=True).decode()
    return body

def save_attachments(msg, email_id, base_folder="email_extraction/attachments"):
    """Save attachments from an email to a subfolder named after the email ID."""
    # Create a base folder for attachments
    os.makedirs(base_folder, exist_ok=True)

    # Create a subfolder for the specific email ID
    email_folder = os.path.join(base_folder, email_id)
    os.makedirs(email_folder, exist_ok=True)

    attachments = []
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))
        if "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(email_folder, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                attachments.append(filepath)
                logging.info(f"Attachment saved: {filepath}")
    return attachments

def save_email_to_file(email_data, filename="email_extraction/emails_with_attachments.txt"):
    """Save email data to a file."""
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"\n📨 Email From: {email_data['from']}\n")
        file.write(f"📝 Subject: {email_data['subject']}\n")
        file.write(f"📄 Body:\n{email_data['body'][:500]}\n")
        for attachment in email_data['attachments']:
            file.write(f"📎 Attachment saved: {attachment}\n")
    logging.info(f"Email data saved to file: {filename}")

def save_raw_email(raw_email, email_id, base_folder="email_extraction/raw_emails"):
    """Save the raw email content to a file."""
    # Create a base folder for raw emails
    os.makedirs(base_folder, exist_ok=True)

    # Create a file for the specific email ID
    email_file = os.path.join(base_folder, f"{email_id}.eml")
    with open(email_file, "wb") as f:
        f.write(raw_email)
    logging.info(f"Raw email saved: {email_file}")
    return email_file

def main_export():
    """Main function to fetch and process emails."""
    # Configure logging
    configure_logging()

    # Load environment variables
    email_address, app_password = load_env_variables()  # Updated variable name

    # Connect to IMAP server
    imap = connect_to_imap(email_address, app_password)  # Updated variable name

    try:
        # Select mailbox
        select_mailbox(imap, "inbox")

        # Search for emails
        email_ids = search_emails(imap, "ALL")

        # Process the latest 5 emails
        for eid in email_ids[-5:]:
            email_id = eid.decode()  # Decode email ID for folder naming
            logging.info(f"Processing email ID: {email_id}")
            res, msg_data = imap.fetch(eid, "(RFC822)")
            if res != "OK":
                logging.error(f"Failed to fetch email with ID {email_id}.")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    msg = email.message_from_bytes(raw_email)

                    # Save the raw email
                    save_raw_email(raw_email, email_id)

                    # Process and save the email data
                    email_data = {
                        "from": msg.get("From"),
                        "subject": decode_subject(msg),
                        "body": process_email_body(msg),
                        "attachments": save_attachments(msg, email_id)  # Pass email ID to save_attachments
                    }
                    save_email_to_file(email_data)
                    logging.info(f"Processed email ID: {email_id} from: {email_data['from']}")
    finally:
        # Close the connection
        imap.logout()
        logging.info("Logged out from IMAP server.")