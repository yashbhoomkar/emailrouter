import redis

def store_file_in_redis(redis_client, key, file_path):
    """Store a file in Redis."""
    with open(file_path, "rb") as file:
        binary_data = file.read()
        redis_client.set(key, binary_data)
        print(f"File '{file_path}' stored in Redis with key '{key}'.")

def retrieve_file_from_redis(redis_client, key, output_path):
    """Retrieve a file from Redis and save it locally."""
    binary_data = redis_client.get(key)
    if binary_data:
        with open(output_path, "wb") as file:
            file.write(binary_data)
        print(f"File retrieved from Redis and saved to '{output_path}'.")
    else:
        print(f"No data found in Redis for key '{key}'.")

# Example usage
if __name__ == "__main__":
    # Connect to Redis
    redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=False)

    # File paths
    file_to_store = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/email_redis_store/../email_extraction/attachments/210/CapgeminiOfferLetter.pdf"  # Replace with your file path
    redis_key = "file:cagemini_offer_letter"  # Unique key for the file in Redis
    # Output path for the retrieved file
    output_file = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/email_redis_store/cagemini_offer_letter_retrived.pdf"  # Replace with your desired output path

    # Store and retrieve the file
    store_file_in_redis(redis_client, redis_key, file_to_store)
    retrieve_file_from_redis(redis_client, redis_key, output_file)