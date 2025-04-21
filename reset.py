import os
import shutil
import redis
import logging

def delete_folder(folder_path):
    """Delete a folder and its contents if it exists."""
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            logging.info(f"Deleted folder: {folder_path}")
        except Exception as e:
            logging.error(f"Failed to delete folder '{folder_path}': {str(e)}")

def delete_file(file_path):
    """Delete a file if it exists."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to delete file '{file_path}': {str(e)}")

def clear_redis_database():
    """Connect to Redis and delete all keys."""
    try:
        redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
        redis_client.flushdb()
        logging.info("Cleared all keys from Redis database.")
    except Exception as e:
        logging.error(f"Failed to clear Redis database: {str(e)}")

def reset_environment():
    """Reset the environment by deleting folders, files, and Redis data."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Paths to delete
    base_dir = os.path.dirname(os.path.abspath(__file__))
    email_extraction_folder = os.path.join(base_dir, "email_extraction")
    email_redis_store_folder = os.path.join(base_dir, "email_redis_store")

    # Folders to delete
    attachments_folder = os.path.join(email_extraction_folder, "attachments")
    logs_folder = os.path.join(email_extraction_folder, "logs")
    raw_emails_folder = os.path.join(email_extraction_folder, "raw_emails")

    # Files to delete
    emails_with_attachments_file = os.path.join(email_extraction_folder, "emails_with_attachments.txt")
    email_redis_store_log_file = os.path.join(email_redis_store_folder, "email_redis_store.log")

    # Delete folders
    delete_folder(attachments_folder)
    delete_folder(logs_folder)
    delete_folder(raw_emails_folder)

    # Delete files
    delete_file(emails_with_attachments_file)
    delete_file(email_redis_store_log_file)

    # Clear Redis database
    clear_redis_database()

if __name__ == "__main__":
    reset_environment()