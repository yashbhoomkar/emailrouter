import requests
import json
import sqlite3

def fetch_feedback_data(db_path="/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/testing/feedback_data.db"):
    """
    Fetch the feedback data from the feedback_data database.

    Args:
        db_path (str): The path to the SQLite database file.

    Returns:
        str: The feedback data as a formatted string.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all rows from the feedback_data table
    query = "SELECT * FROM feedback_data"
    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    if rows:
        feedback_data = ""
        for row in rows:
            feedback_data += f"{row[0]:<20} {row[1]:<30} {row[2]:<50} {row[3]:<30} {row[4]:<30} {row[5]:<20} {row[6]:<20} {row[7]:<20} {row[8]:<20}\n"
        return feedback_data
    else:
        raise ValueError("No feedback data found in the feedback_data database.")

def analyze_email(email_content, feedback_data, model="llama3.2", base_url="http://localhost:11434"):
    """
    Analyze the email to determine its urgency and department.

    Args:
        email_content (str): The content of the email to analyze, including the EMAIL_ID.
        feedback_data (str): The feedback database to help improve responses.
        model (str): The name of the model to query (default is "llama3.2").
        base_url (str): The base URL of the Ollama API (default is "http://localhost:11434").

    Returns:
        dict: The JSON response with email ID, urgency, and department.
    """
    url = f"{base_url}/api/chat"
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"Analyze the following email and decide the urgency and department it belongs to.\n\n"
        f"Email:\n{email_content}\n\n"
        f"Here is the feedback database to help you improve your response:\n{feedback_data}\n\n"
        "Strictly select only one department"
        "Respond strictly in the following JSON format:\n"
        "{\n"
        "    \"EMAIL_ID\": \"email_id\",\n"
        "    \"DEPARTMENT\": \"HR or FINANCE or SOFTWARE or CYBERSECURITY\",\n"
        "    \"URGENCY\": \"HIGH or MEDIUM or LOW\"\n"
        "}\n"
        "Ensure the response is valid JSON and adheres to the specified format. Do not include any additional text or explanations."
    "\n FOLLOW THE RESPONSE FORMAT STRICTLY AND DONOT ADD ANYTHING ELSE . IF YOU DONOT ADHERE TO THE GIVEN FORMAT YOU WILL BE FINED\n"
    "Example:\n"
        "{\n"
        "    \"EMAIL_ID\": \"123\",\n"
        "    \"DEPARTMENT\": \"HR\",\n"
        "    \"URGENCY\": \"HIGH\"\n"
        "}\n"
        "Ensure the response is valid JSON and adheres to the specified format. Do not include any additional text or explanations."
    )
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        # Process the streamed response
        complete_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    message = chunk.get("message", {}).get("content", "")
                    complete_response += message
                except json.JSONDecodeError:
                    continue

        # Validate and correct the final response as JSON
        return correct_json(complete_response.strip())
    except requests.exceptions.RequestException as e:
        return {"error": f"Error querying Ollama API: {str(e)}"}

def retrieve_people_by_department(department, db_path="/Users/yashbhoomkar/Desktop/pythonCodes/emailRouter/vone/testing/people_emails_metadata.db"):
    """
    Retrieve all rows from the people_emails_metadata.db for the given department.

    Args:
        department (str): The department to filter by.
        db_path (str): The path to the SQLite database file.

    Returns:
        list: A list of dictionaries containing the rows for the given department.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT * FROM table_data WHERE DEPT = ?"
    cursor.execute(query, (department,))
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    people = [
        {
            "DEPT": row[0],
            "NAME": row[1],
            "EMAIL": row[2],
            "EMAILS_FORWARDED_IN_LAST_24_DAYS": row[3],
            "SENIORITY_LEVEL": row[4],
            "WORK": row[5]
        }
        for row in rows
    ]

    conn.close()
    return people

def finalize_routing(email_id, people_list, feedback_data, department, urgency, model="llama3.2", base_url="http://localhost:11434"):
    """
    Pass the retrieved people list and feedback data to Llama 3.2 for the final routing decision.

    Args:
        email_id (str): The ID of the email being processed.
        people_list (list of dict): The list of people retrieved for the department.
        feedback_data (str): The feedback database to help improve responses.
        department (str): The department the email belongs to.
        urgency (str): The urgency level of the email.
        model (str): The name of the model to query (default is "llama3.2").
        base_url (str): The base URL of the Ollama API (default is "http://localhost:11434").

    Returns:
        dict: The final routing decision from Llama 3.2.
    """
    url = f"{base_url}/api/chat"
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"The email with ID {email_id} belongs to the {department} department and has an urgency level of {urgency}.\n\n"
        f"Here is the list of people in the department:\n{json.dumps(people_list, indent=4)}\n\n"
        f"Here is the feedback database to help you improve your response:\n{feedback_data}\n\n"
        "Decide who the email should be forwarded to, and who should be in CC and BCC. ADD PEOPLE'S email id in cc and bcc if and only if required\n"
        "\n IF NO CC OR BCC REQUIRED, THEN ADD 'EMPTY' AS THE VALUE OF CC OR BCC \n"
        "\n STRICTLY SELECT ONLY ONE DEPARTMENT AND FORWARD_TO SHALL NEVER BE EMPTY / NULL \n\n"

        "Respond strictly in the following JSON format:\n"
        "{\n"
        "    \"EMAIL_ID\": \"email_id\",\n"
        "    \"DEPARTMENT\": \"HR or FINANCE or SOFTWARE or CYBERSECURITY\",\n"
        "    \"URGENCY\": \"HIGH | MEDIUM | LOW\",\n"
        "    \"FORWARD_TO\": \"email_id\",\n"
        "    \"CC\": [\"email_id1\", \"email_id2\"],\n"
        "    \"BCC\": [\"email_id3\", \"email_id4\"]\n"
        "}\n"
        "Ensure the response is valid JSON and adheres to the specified format. Do not include any additional text or explanations."
    )
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        # Process the streamed response
        complete_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    message = chunk.get("message", {}).get("content", "")
                    complete_response += message
                except json.JSONDecodeError:
                    continue

        # Validate and correct the final response as JSON
        return correct_json(complete_response.strip())
    except requests.exceptions.RequestException as e:
        return {"error": f"Error querying Ollama API: {str(e)}"}

def correct_json(raw_response):
    """
    Attempt to correct common JSON formatting issues in the response if present.

    Args:
        raw_response (str): The raw JSON string to validate and correct.

    Returns:
        dict: The corrected JSON object, or an error message if correction fails.
    """
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response.", "raw_response": raw_response}

def main_export_ollama(email_content):
    """
    Main function to execute the email analysis and routing process.
    """
    
    # Fetch feedback data from the database
    feedback_data = fetch_feedback_data()

    #print("Step 1: Analyzing email...")
    analysis_response = analyze_email(email_content, feedback_data)
    #print("Analysis Response:", json.dumps(analysis_response, indent=4))

    # Validate the response
    if "EMAIL_ID" not in analysis_response or "DEPARTMENT" not in analysis_response or "URGENCY" not in analysis_response:
        raise KeyError("The analysis response is missing required keys: 'EMAIL_ID', 'DEPARTMENT', or 'URGENCY'.")

    email_id = analysis_response["EMAIL_ID"]
    department = analysis_response["DEPARTMENT"]
    urgency = analysis_response["URGENCY"]

    if "error" not in analysis_response:
        email_id = analysis_response["EMAIL_ID"]
        department = analysis_response["DEPARTMENT"]
        urgency = analysis_response["URGENCY"]

        #print(f"\nStep 2: Retrieving people for department '{department}'...")
        people_list = retrieve_people_by_department(department)
        #print("People List:", json.dumps(people_list, indent=4))

        #print(f"\nStep 3: Finalizing routing for email ID '{email_id}' in department '{department}' with urgency '{urgency}'...")
        routing_response = finalize_routing(email_id, people_list, feedback_data, department, urgency)
        #print("Routing Response:", json.dumps(routing_response, indent=4))
        return routing_response

# if __name__ == "__main__":
#     #Example email content to test
#    email_content = (
#       "EMAIL_ID: 210\n"
#      "Subject: General Feedback \n\n"
#        "Dear HR Team,\n\n"
#        "I would like to provide some feedback regarding the recent changes in our HR policies. "
#        "I believe there are areas that need improvement, especially in the onboarding process.\n\n"
#        "I have attached a document with my detailed feedback.\n\n"
#        "Please let me know if you need any further information.\n\n"
#        "Best regards,\nJohn Doe"
#    )
#    main_export_ollama(email_content)