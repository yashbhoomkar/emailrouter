import os
import email
import redis
import json
import logging

def ensure_folder_exists(folder_path):
    """Ensure that a folder exists; create it if it does not."""
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            logging.info("Created missing folder: %s", folder_path)
        except Exception as e:
            logging.error("Failed to create folder '%s': %s", folder_path, str(e))
            raise

# Configure logging
def setup_logging():
    """Set up logging and ensure the log file exists."""
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_redis_store.log")
    
    # Check if the log file exists; if not, create it
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write("")  # Create an empty log file

    # Configure logging
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging setup complete. Log file: %s", log_file_path)

def connect_to_redis(host="localhost", port=6379, decode_responses=True):
    """Connect to the Redis server."""
    try:
        redis_client = redis.StrictRedis(host=host, port=port, decode_responses=decode_responses)
        logging.info("Connected to Redis server at %s:%s", host, port)
        return redis_client
    except Exception as e:
        logging.error("Failed to connect to Redis: %s", str(e))
        raise

def store_email_in_redis(redis_client, key, email_data):
    """Store email data in Redis."""
    try:
        redis_client.set(key, json.dumps(email_data))
        logging.info("Email data stored in Redis with key '%s'", key)
    except Exception as e:
        logging.error("Failed to store email data in Redis for key '%s': %s", key, str(e))
        raise

def retrieve_email_from_redis(redis_client, key):
    """Retrieve email data from Redis."""
    try:
        email_data = redis_client.get(key)
        if email_data:
            logging.info("Retrieved email data from Redis for key '%s'", key)
            return json.loads(email_data)
        else:
            logging.warning("No data found in Redis for key '%s'", key)
            return None
    except Exception as e:
        logging.error("Failed to retrieve email data from Redis for key '%s': %s", key, str(e))
        raise

def parse_eml_file(eml_file_path):
    """Parse the .eml file and extract email details."""
    try:
        with open(eml_file_path, "r") as file:
            msg = email.message_from_file(file)

        email_from = msg.get("From")
        email_subject = msg.get("Subject")
        email_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" not in content_disposition:
                    try:
                        email_body = part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            email_body = msg.get_payload(decode=True).decode()

        logging.info("Parsed email file: %s", eml_file_path)
        return email_from, email_subject, email_body
    except Exception as e:
        logging.error("Failed to parse email file '%s': %s", eml_file_path, str(e))
        raise

def check_attachments_folder(attachments_folder, email_id):
    """Check if the attachments folder for the email ID exists and is not empty."""
    try:
        email_attachments_folder = os.path.join(attachments_folder, email_id)
        if os.path.exists(email_attachments_folder) and os.listdir(email_attachments_folder):
            attachment_paths = [
                os.path.join(email_attachments_folder, f)
                for f in os.listdir(email_attachments_folder)
                if os.path.isfile(os.path.join(email_attachments_folder, f))
            ]
            logging.info("Found attachments for email ID '%s': %s", email_id, attachment_paths)
            return attachment_paths
        logging.info("No attachments found for email ID '%s'", email_id)
        return []
    except Exception as e:
        logging.error("Failed to check attachments for email ID '%s': %s", email_id, str(e))
        raise

def prepare_email_data(email_id, email_from, email_subject, email_body, attachment_paths):
    """Prepare the email data dictionary."""
    email_data = {
        "email_id": email_id,
        "from": email_from,
        "subject": email_subject,
        "body": email_body,
        "attachments": attachment_paths,  # Store file paths for attachments
        "STATUS": "NOT_ROUTED"  # Add STATUS field with initial value
    }
    logging.info("Prepared email data for email ID '%s'", email_id)
    return email_data

def process_eml_file(eml_file, raw_emails_folder, attachments_folder, redis_client):
    """Process a single .eml file and store its data in Redis."""
    try:
        email_id = os.path.splitext(eml_file)[0]  # Extract email ID from file name
        eml_file_path = os.path.join(raw_emails_folder, eml_file)

        # Parse the .eml file
        email_from, email_subject, email_body = parse_eml_file(eml_file_path)

        # Check for attachments
        attachment_paths = check_attachments_folder(attachments_folder, email_id)

        # Prepare email data
        email_data = prepare_email_data(email_id, email_from, email_subject, email_body, attachment_paths)

        # Store email data in Redis
        redis_key = f"email:{email_id}"
        store_email_in_redis(redis_client, redis_key, email_data)

        # Log successful insertion
        logging.info("Successfully inserted email ID '%s' into Redis.", email_id)
    except Exception as e:
        logging.error("Failed to process email file '%s': %s", eml_file, str(e))
        raise

def process_and_store_emails(redis_client, raw_emails_folder, attachments_folder):
    """Process all emails in the raw_emails folder and store their data in Redis."""
    try:
        # Ensure the raw_emails folder exists
        ensure_folder_exists(raw_emails_folder)

        eml_files = [f for f in os.listdir(raw_emails_folder) if f.endswith(".eml")]
        if not eml_files:
            logging.warning("Folder '%s' is empty.", raw_emails_folder)
            return

        for eml_file in eml_files:
            process_eml_file(eml_file, raw_emails_folder, attachments_folder, redis_client)
    except Exception as e:
        logging.error("Failed to process and store emails: %s", str(e))
        raise

def define_paths():
    """Define and return the paths for raw emails and attachments."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_emails_folder = os.path.join(base_dir, "../email_extraction/raw_emails")
    attachments_folder = os.path.join(base_dir, "../email_extraction/attachments")

    # Ensure both folders exist
    ensure_folder_exists(raw_emails_folder)
    ensure_folder_exists(attachments_folder)

    return raw_emails_folder, attachments_folder

def main_export_redis_store():
    """Main function to process and store emails."""
    try:
        # Set up logging
        setup_logging()

        # Connect to Redis
        redis_client = connect_to_redis()

        # Define paths
        raw_emails_folder, attachments_folder = define_paths()

        # Process and store emails
        process_and_store_emails(redis_client, raw_emails_folder, attachments_folder)
    except Exception as e:
        logging.critical("Critical error in main function: %s", str(e))
        raise

if __name__ == "__main__":
    main_export_redis_store()