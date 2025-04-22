import streamlit as st
import sqlite3
import os

# Set the title of the app
st.set_page_config(page_title="Email Router Dashboard", page_icon="📧")

# Sidebar Navigation with Dropdown Menu
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select a Page",  # Dropdown label
    ["Home", "Feedback", "People Metadata"]  # Options in the dropdown
)

# Home Page
if page == "Home":
    st.title("📧 Email Router Dashboard")
    st.subheader("Welcome to the Email Router Project! 🚀")
    st.write(
        """
        The **Email Router** is a backend system designed to:
        - 📤 Automatically process and forward emails based on predefined rules.
        - 🛠️ Integrate with Redis and SQLite for efficient email routing and metadata management.
        - 📊 Provide insights and logs for monitoring email activity.

        ### Features:
        - **Email Processing**: Automatically fetch, analyze, and forward emails.
        - **Redis Integration**: Store and manage email routing data efficiently.
        - **SQLite Database**: Track email metadata and maintain logs.
        - **Streamlit Dashboard**: Monitor and control the system in real-time.

        ---
        """
    )
    st.write("### Get Started:")
    st.write("Use the sidebar to navigate to **Feedback** or **People Metadata**.")
    st.image(
        "https://via.placeholder.com/800x400.png?text=Email+Router+Dashboard",
        caption="Email Router Dashboard Overview",
    )

# Feedback Page
elif page == "Feedback":
    st.title("📝 Add Feedback")
    st.write("Use this form to submit feedback to the system.")

    # Database path
    db_path = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/testing/feedback_data.db"

    # Check if the database exists
    if not os.path.exists(db_path):
        st.error("The feedback database does not exist. Please ensure the database is created.")
    else:
        # Feedback form
        with st.form("feedback_form"):
            email = st.text_input("Email Address", placeholder="Enter your email address")
            email_subject = st.text_input("Email Subject", placeholder="Enter the subject of the email")
            email_actual_text = st.text_area("Email Content", placeholder="Enter the content of the email")
            previous_response = st.text_area("Previous Response", placeholder="Enter the previous response (if any)")
            expected_response = st.text_area("Expected Response", placeholder="Enter the expected response")
            previous_response_cc = st.text_input("Previous Response CC", placeholder="Enter CC emails (comma-separated)")
            previous_response_bcc = st.text_input("Previous Response BCC", placeholder="Enter BCC emails (comma-separated)")
            expected_response_cc = st.text_input("Expected Response CC", placeholder="Enter CC emails (comma-separated)")
            expected_response_bcc = st.text_input("Expected Response BCC", placeholder="Enter BCC emails (comma-separated)")

            # Submit button
            submitted = st.form_submit_button("Submit Feedback")

            if submitted:
                # Validate inputs
                if not email or not email_subject or not email_actual_text:
                    st.error("Email, Subject, and Content are required fields.")
                else:
                    try:
                        # Connect to the database
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()

                        # Insert feedback into the database
                        cursor.execute("""
                            INSERT OR IGNORE INTO feedback_data (
                                EMAIL, EMAIL_SUBJECT, EMAIL_ACTUAL_TEXT, PREVIOUS_RESPONSE, EXPECTED_RESPONSE,
                                PREVIOUS_RESPONSE_CC, PREVIOUS_RESPONSE_BCC, EXPECTED_RESPONSE_CC, EXPECTED_RESPONSE_BCC
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            email,
                            email_subject,
                            email_actual_text,
                            previous_response,
                            expected_response,
                            previous_response_cc,
                            previous_response_bcc,
                            expected_response_cc,
                            expected_response_bcc
                        ))

                        # Commit changes and close the connection
                        conn.commit()
                        conn.close()

                        st.success("Feedback submitted successfully!")
                    except Exception as e:
                        st.error(f"An error occurred while submitting feedback: {str(e)}")

# People Metadata Page
elif page == "People Metadata":
    st.title("👥 Add People Metadata")
    st.write("Use this form to add metadata for people into the database.")

    # Database path
    db_path = "/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/testing/people_emails_metadata.db"

    # Check if the database exists
    if not os.path.exists(db_path):
        st.error("The people metadata database does not exist. Please ensure the database is created.")
    else:
        # Metadata form
        with st.form("metadata_form"):
            dept = st.text_input("Department", placeholder="Enter the department (e.g., FINANCE, HR, etc.)")
            name = st.text_input("Name", placeholder="Enter the person's name")
            email = st.text_input("Email Address", placeholder="Enter the person's email address")
            emails_forwarded = st.number_input("Emails Forwarded in Last 24 Days", min_value=0, step=1)
            seniority_level = st.selectbox("Seniority Level", ["LOW", "MEDIUM", "HIGH", "HIGHEST"])
            work = st.text_input("Work", placeholder="Enter the person's work description")

            # Submit button
            submitted = st.form_submit_button("Add Metadata")

            if submitted:
                # Validate inputs
                if not dept or not name or not email or not work:
                    st.error("Department, Name, Email, and Work are required fields.")
                else:
                    try:
                        # Connect to the database
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()

                        # Insert metadata into the database
                        cursor.execute("""
                            INSERT OR IGNORE INTO table_data (
                                DEPT, NAME, EMAIL, EMAILS_FORWARDED_IN_LAST_24_DAYS, SENIORITY_LEVEL, WORK
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            dept,
                            name,
                            email,
                            emails_forwarded,
                            seniority_level,
                            work
                        ))

                        # Commit changes and close the connection
                        conn.commit()
                        conn.close()

                        st.success("Metadata added successfully!")
                    except Exception as e:
                        st.error(f"An error occurred while adding metadata: {str(e)}")