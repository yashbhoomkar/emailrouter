import time
from email_extraction.gmail_imap import main_export
from email_redis_store.redis_store import main_export_redis_store
from testing.testing_ollama import main_export_ollama
from ollama_lama.retrive_from_redis import main_export_rfr
from ollama_lama.retrive_and_send_email import main_export_send_email
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

        emails_list  = main_export_rfr()
        for  email_object in emails_list:
            print(f"Processing email: {email_object}")
            response = main_export_ollama(email_object)
            print(f"Response: {response}")
            print("Sending email...")
            main_export_send_email(response)
            print("Email sent successfully.")
        
        print(f"Waiting for {sleep_time} seconds before the next run...")
        time.sleep(sleep_time)

def main_testing():
    """
    Main function to execute the email analysis and routing process.
    """
    # Example email content for testing
    email_content = (
       "EMAIL_ID: 210\n"
      "Subject: General Feedback \n\n"
        "Dear HR Team,\n\n"
       "I would like to provide some feedback regarding the recent changes in our HR policies. "
      "I believe there are areas that need improvement, especially in the onboarding process.\n\n"
       "I have attached a document with my detailed feedback.\n\n"
       "Please let me know if you need any further information.\n\n"
       "Best regards,\nJohn Doe"
   )
    main_export_ollama(email_content)


if __name__ == "__main__":
    main()