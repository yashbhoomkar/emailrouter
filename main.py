import time
from email_extraction.gmail_imap import main_export
from email_redis_store.redis_store import main_export_redis_store

def main():
    while True:
        print("Starting email extraction...")
        start_time = time.time()
        main_export()
        main_export_redis_store()
        end_time = time.time()

        # Calculate processing time and adjust sleep interval
        processing_time = end_time - start_time
        sleep_time = max(5, processing_time)  # Ensure at least 5 seconds between runs
        print(f"Waiting for {sleep_time} seconds before the next run...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()