from email_extraction.gmail_imap import main_export
from email_redis_store.redis_store import main_export_redis_store

def main():
    main_export()
    main_export_redis_store()


if __name__ == "__main__":
    main()