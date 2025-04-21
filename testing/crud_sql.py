import sqlite3

def create_people_emails_metadata_db(db_path="/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/testing/people_emails_metadata.db"):
    """
    Create and populate the SQLite database for table_data.

    Args:
        db_path (str): The path to the SQLite database file.
    """
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the table_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_data (
            DEPT TEXT,
            NAME TEXT,
            EMAIL TEXT PRIMARY KEY,
            EMAILS_FORWARDED_IN_LAST_24_DAYS INTEGER,
            SENIORITY_LEVEL TEXT,
            WORK TEXT
        )
    """)

    # Insert sample data into table_data
    table_data = [
    ("FINANCE", "Alice Johnson", "alice.johnson@financecorp.com", 45, "HIGHEST", "Payroll Management"),
    ("FINANCE", "Bob Smith", "bob.smith@financecorp.com", 30, "MEDIUM", "Tax Compliance"),
    ("FINANCE", "Charlie Brown", "charlie.brown@financecorp.com", 15, "LOW", "Budget Analysis"),
    ("HR", "Diana Prince", "diana.prince@hrsolutions.com", 120, "HIGHEST", "Employee Relations"),
    ("HR", "Eve Adams", "eve.adams@hrsolutions.com", 75, "MEDIUM", "Recruitment"),
    ("HR", "Frank White", "frank.white@hrsolutions.com", 50, "LOW", "Training and Development"),
    ("SOFTWARE", "Grace Hopper", "grace.hopper@techinnovators.com", 200, "HIGHEST", "Software Architecture"),
    ("SOFTWARE", "Hank Green", "hank.green@techinnovators.com", 100, "MEDIUM", "Backend Development"),
    ("SOFTWARE", "Ivy Lee", "ivy.lee@techinnovators.com", 60, "LOW", "Frontend Development"),
    ("CYBERSECURITY", "Jack Ryan", "jack.ryan@securecorp.com", 150, "HIGHEST", "Incident Response"),
    ("CYBERSECURITY", "Karen Black", "karen.black@securecorp.com", 90, "MEDIUM", "Vulnerability Assessment"),
    ("CYBERSECURITY", "Leo King", "leo.king@securecorp.com", 40, "LOW", "Access Control Management"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO table_data (DEPT, NAME, EMAIL, EMAILS_FORWARDED_IN_LAST_24_DAYS, SENIORITY_LEVEL, WORK)
        VALUES (?, ?, ?, ?, ?, ?)
    """, table_data)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"People Emails Metadata database created and populated at {db_path}")


def create_feedback_data_db(db_path="/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/testing/feedback_data.db"):
    """
    Create and populate the SQLite database for feedback_data.

    Args:
        db_path (str): The path to the SQLite database file.
    """
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the feedback_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback_data (
            EMAIL TEXT PRIMARY KEY,
            EMAIL_SUBJECT TEXT,
            EMAIL_ACTUAL_TEXT TEXT,
            PREVIOUS_RESPONSE TEXT,
            EXPECTED_RESPONSE TEXT,
            PREVIOUS_RESPONSE_CC TEXT,
            PREVIOUS_RESPONSE_BCC TEXT,
            EXPECTED_RESPONSE_CC TEXT,
            EXPECTED_RESPONSE_BCC TEXT
        )
    """)

    # Insert sample data into feedback_data
    feedback_data = [
    ("alice.johnson@financecorp.com", "Salary discrepancy issue", "The amount credited is lower than expected.",
     "{'urgency': 'MEDIUM'}", "{'urgency': 'HIGHEST'}", "[]", "[]", "[]", "[]"),
    ("bob.smith@financecorp.com", "Tax compliance feedback", "Feedback on the recent tax compliance process.",
     "{'department': 'HR'}", "{'department': 'FINANCE'}", "[]", "[]", "[]", "[]"),
    ("diana.prince@hrsolutions.com", "Recruitment improvement", "Suggestions to improve the recruitment process.",
     "{'forward_to': 'eve.adams@hrsolutions.com'}", "{'forward_to': 'diana.prince@hrsolutions.com'}",
     "['eve.adams@hrsolutions.com']", "[]", "['diana.prince@hrsolutions.com']", "[]"),
    ("grace.hopper@techinnovators.com", "Software architecture review", "Request for a review of the new architecture design.",
     "{'urgency': 'HIGH'}", "{'urgency': 'HIGHEST'}", "[]", "[]", "[]", "[]"),
    ("jack.ryan@securecorp.com", "Incident response feedback", "Feedback on the recent incident response process.",
     "{'department': 'CYBERSECURITY'}", "{'department': 'CYBERSECURITY'}", "[]", "[]", "[]", "[]"),
    ("ivy.lee@techinnovators.com", "Frontend development issue", "Issues with the current frontend implementation.",
     "{'urgency': 'LOW'}", "{'urgency': 'MEDIUM'}", "[]", "[]", "[]", "[]"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO feedback_data (EMAIL, EMAIL_SUBJECT, EMAIL_ACTUAL_TEXT, PREVIOUS_RESPONSE, EXPECTED_RESPONSE,
                                             PREVIOUS_RESPONSE_CC, PREVIOUS_RESPONSE_BCC, EXPECTED_RESPONSE_CC, EXPECTED_RESPONSE_BCC)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, feedback_data)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"Feedback Data database created and populated at {db_path}")


if __name__ == "__main__":
    # Create and populate the people_emails_metadata.db
    create_people_emails_metadata_db()

    # Create and populate the feedback_data.db
    create_feedback_data_db()