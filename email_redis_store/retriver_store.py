import os
import email

def check_raw_emails_folder(folder_path):
    """Check if the raw_emails folder exists and is not empty."""
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return False
    eml_files = [f for f in os.listdir(folder_path) if f.endswith(".eml")]
    if not eml_files:
        print(f"Folder '{folder_path}' is empty.")
        return False
    return eml_files

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

def display_email_details(email_id, email_from, email_subject, email_body, attachment_paths):
    """Display the processed email details and attachment paths."""
    print(f"Email ID: {email_id}")
    print(f"From: {email_from}")
    print(f"Subject: {email_subject}")
    print(f"Body:\n{email_body[:500]}")  # Display the first 500 characters of the body
    if attachment_paths:
        print("Attachments:")
        for path in attachment_paths:
            print(f" - {path}")
    else:
        print("No attachments found.")
    print("-" * 50)

def process_emails():
    """Main function to process emails and display their details."""
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths relative to the script's location
    raw_emails_folder = os.path.join(base_dir, "../email_extraction/raw_emails")
    attachments_folder = os.path.join(base_dir, "../email_extraction/attachments")

    # Check if the raw_emails folder exists and is not empty
    eml_files = check_raw_emails_folder(raw_emails_folder)
    if not eml_files:
        return

    # Process each .eml file
    for eml_file in eml_files:
        email_id = os.path.splitext(eml_file)[0]  # Extract email ID from file name
        eml_file_path = os.path.join(raw_emails_folder, eml_file)

        # Parse the .eml file
        email_from, email_subject, email_body = parse_eml_file(eml_file_path)

        # Check for attachments
        attachment_paths = check_attachments_folder(attachments_folder, email_id)

        # Display the processed email and attachment paths
        display_email_details(email_id, email_from, email_subject, email_body, attachment_paths)

if __name__ == "__main__":
    process_emails()