import os
import email
import redis
import json

def store_email_in_redis(redis_client, key, email_data):
    """Store email data in Redis."""
    redis_client.set(key, json.dumps(email_data))
    print(f"Email data stored in Redis with key '{key}'.")

def retrieve_email_from_redis(redis_client, key):
    """Retrieve email data from Redis."""
    email_data = redis_client.get(key)
    if email_data:
        return json.loads(email_data)
    else:
        print(f"No data found in Redis for key '{key}'.")
        return None

def parse_eml_file(eml_file_path):
    """Parse the .eml file and extract email details."""
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

    return email_from, email_subject, email_body

def check_attachments_folder(attachments_folder, email_id):
    """Check if the attachments folder for the email ID exists and is not empty."""
    email_attachments_folder = os.path.join(attachments_folder, email_id)
    if os.path.exists(email_attachments_folder) and os.listdir(email_attachments_folder):
        attachment_paths = [
            os.path.join(email_attachments_folder, f)
            for f in os.listdir(email_attachments_folder)
            if os.path.isfile(os.path.join(email_attachments_folder, f))
        ]
        return attachment_paths
    return []

def process_and_store_emails(redis_client, raw_emails_folder, attachments_folder):
    """Process each email and store its data in Redis."""
    # Check if the raw_emails folder exists and is not empty
    if not os.path.exists(raw_emails_folder):
        print(f"Folder '{raw_emails_folder}' does not exist.")
        return

    eml_files = [f for f in os.listdir(raw_emails_folder) if f.endswith(".eml")]
    if not eml_files:
        print(f"Folder '{raw_emails_folder}' is empty.")
        return

    # Process each .eml file
    for eml_file in eml_files:
        email_id = os.path.splitext(eml_file)[0]  # Extract email ID from file name
        eml_file_path = os.path.join(raw_emails_folder, eml_file)

        # Parse the .eml file
        email_from, email_subject, email_body = parse_eml_file(eml_file_path)

        # Check for attachments
        attachment_paths = check_attachments_folder(attachments_folder, email_id)

        # Prepare email data
        email_data = {
            "email_id": email_id,
            "from": email_from,
            "subject": email_subject,
            "body": email_body,
            "attachments": attachment_paths
        }

        # Store email data in Redis
        redis_key = f"email:{email_id}"
        store_email_in_redis(redis_client, redis_key, email_data)

if __name__ == "__main__":
    # Connect to Redis
    redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_emails_folder = os.path.join(base_dir, "../email_extraction/raw_emails")
    attachments_folder = os.path.join(base_dir, "../email_extraction/attachments")

    # Process and store emails
    process_and_store_emails(redis_client, raw_emails_folder, attachments_folder)

    # Example: Retrieve an email from Redis
    email_id_to_retrieve = "207"  # Replace with the email ID you want to retrieve
    redis_key = f"email:{email_id_to_retrieve}"
    email_data = retrieve_email_from_redis(redis_client, redis_key)
    if email_data:
        print(f"Retrieved email data for key '{redis_key}':")
        print(json.dumps(email_data, indent=4))