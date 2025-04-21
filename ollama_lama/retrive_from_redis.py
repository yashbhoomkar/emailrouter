import redis
import json

def connect_to_redis(host="localhost", port=6379, db=0):
    """
    Connect to the Redis database.

    Args:
        host (str): Redis server hostname.
        port (int): Redis server port.
        db (int): Redis database number.

    Returns:
        redis.StrictRedis: Redis client connection.
    """
    try:
        redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        return redis_client
    except Exception as e:
        print(f"Error connecting to Redis: {str(e)}")
        return None

def get_emails_with_status(redis_client, status="NOT_ROUTED"):
    """
    Retrieve all emails from Redis with the specified status.

    Args:
        redis_client (redis.StrictRedis): Redis client connection.
        status (str): The status to filter emails by (default is "NOT_ROUTED").

    Returns:
        list: A list of processed emails with the specified status.
    """
    try:
        emails = []
        for key in redis_client.scan_iter("email:*"):  # Assuming keys are stored as "email:<id>"
            email_data = redis_client.get(key)
            if email_data:
                try:
                    email_json = json.loads(email_data)
                    # Debug: Log the raw email data
                    print(f"Processing key: {key}, Raw data: {email_json}")
                    if email_json.get("status") == status:  # Match the lowercase "status" key
                        # Extract relevant fields for the processed email
                        processed_email = {
                            "EMAIL_ID": email_json.get("email_id", "MISSING"),
                            "SUBJECT": email_json.get("subject", "MISSING"),
                            "BODY": email_json.get("body", "MISSING"),
                            "STATUS": email_json.get("status", "MISSING")
                        }
                        emails.append(processed_email)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for key {key}: {str(e)}")
        return emails
    except Exception as e:
        print(f"Error retrieving emails from Redis: {str(e)}")
        return []

def main():
    """
    Main function to retrieve and print processed emails with "NOT_ROUTED" status.
    """
    print("Connecting to Redis...")
    redis_client = connect_to_redis()

    if not redis_client:
        print("Failed to connect to Redis. Exiting...")
        return

    print("Retrieving emails with status 'NOT_ROUTED'...")
    not_routed_emails = get_emails_with_status(redis_client, status="NOT_ROUTED")

    if not_routed_emails:
        print(f"Found {len(not_routed_emails)} email(s) with status 'NOT_ROUTED':")
        for email in not_routed_emails:
            print(json.dumps(email, indent=4))  # Print the processed email
    else:
        print("No emails with status 'NOT_ROUTED' found.")

if __name__ == "__main__":
    main()