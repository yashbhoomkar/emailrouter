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
        ("FINANCE", "XYZ", "XYZ@gmail.com", 56, "HIGHEST", "Payroll Service"),
        ("FINANCE", "ABC", "ABC@gmail.com", 24, "MEDIUM", "Payroll Service"),
        ("FINANCE", "EFG", "EFG@gmail.com", 100, "LOW", "Budget Planning"),
        ("HR", "HIJ", "HIJ@gmail.com", 108, "HIGHEST", "Recruitment"),
        ("HR", "KLM", "KLM@gmail.com", 56, "MEDIUM", "Employee Relations"),
        ("HR", "PQR", "PQR@gmail.com", 96, "LOW", "Employee Benefits"),
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
        ("XYZ@gmail.com", "Salary discrepancy issue", "The amount credited is lower than expected",
         "{'urgency': 'MEDIUM'}", "{'urgency': 'HIGHEST'}", "[]", "[]", "[]", "[]"),
        ("ABC@gmail.com", "Payroll service feedback", "Feedback on payroll service",
         "{'department': 'HR'}", "{'department': 'FINANCE'}", "[]", "[]", "[]", "[]"),
        ("HIJ@gmail.com", "Recruitment improvement", "Improve recruitment process",
         "{'forward_to': 'PQR@gmail.com'}", "{'forward_to': 'HIJ@gmail.com'}",
         "['PQR@gmail.com']", "[]", "['HIJ@gmail.com']", "[]"),
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