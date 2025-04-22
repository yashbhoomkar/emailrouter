import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        list: A list of email objects with the specified status.
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
                    if email_json.get("STATUS") == status:  # Match the correct "STATUS" key
                        emails.append(email_json)  # Add the raw Redis object to the list
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for key {key}: {str(e)}")
        return emails
    except Exception as e:
        print(f"Error retrieving emails from Redis: {str(e)}")
        return []


def main_export_rfr():
    """
    Main function to retrieve and return emails with "NOT_ROUTED" status.
    """
    print("Connecting to Redis...")
    redis_client = connect_to_redis()

    if not redis_client:
        print("Failed to connect to Redis. Exiting...")
        return []

    print("Retrieving emails with status 'NOT_ROUTED'...")
    not_routed_emails = get_emails_with_status(redis_client, status="NOT_ROUTED")

    if not_routed_emails:
        print(f"Found {len(not_routed_emails)} email(s) with status 'NOT_ROUTED'.")
        return not_routed_emails
    else:
        print("No emails with status 'NOT_ROUTED' found.")
        return []


# if __name__ == "__main__":
#     emails = main_export_rfr()
#     print("Emails with 'NOT_ROUTED' status:")
#     print(json.dumps(emails, indent=4))