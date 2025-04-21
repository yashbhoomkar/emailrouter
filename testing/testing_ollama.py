import requests
import json

def query_ollama(email_content, model="llama3.2", base_url="http://localhost:11434"):
    """
    Query the Ollama API with an email and ensure the response is in the desired JSON format.

    Args:
        email_content (str): The content of the email to analyze.
        model (str): The name of the model to query (default is "llama3.2").
        base_url (str): The base URL of the Ollama API (default is "http://localhost:11434").

    Returns:
        dict: The JSON response from the model.
    """
    url = f"{base_url}/api/chat"
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"Analyze the following email and respond with the urgency and department it should be forwarded to.\n\n"
        f"Email:\n{email_content}\n\n"
        "Respond only in the following JSON format:\n"
        "{\n"
        "    \"urgency\": \"HIGHEST | MEDIUM | LOW\",\n"
        "    \"department\": \"HR | FINANCE | SOFTWARE | CYBERSECURITY\"\n"
        "}\n"
        "Ensure the response is valid JSON."
    )
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        # Send the request with streaming enabled
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

        # Process the streamed response
        complete_response = ""
        for line in response.iter_lines():
            if line:  # Skip empty lines
                try:
                    chunk = json.loads(line)
                    message = chunk.get("message", {}).get("content", "")
                    complete_response += message
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON chunk: {line}")
        
        # Validate and correct the final response as JSON
        corrected_response = correct_json(complete_response.strip())
        return corrected_response
    except requests.exceptions.RequestException as e:
        return {"error": f"Error querying Ollama API: {str(e)}"}

def correct_json(raw_response):
    """
    Attempt to correct common JSON formatting issues in the response if present, else return the original input as output.

    Args:
        raw_response (str): The raw JSON string to validate and correct if needed.

    Returns:
        dict: The corrected JSON object, or an error message if correction fails.
    """
    try:
        # Try to parse the raw response as JSON
        return json.loads(raw_response)  # If valid, return as-is
    except json.JSONDecodeError:
        # Attempt to fix common issues (e.g., missing commas)
        try:
            import json5  # json5 allows more forgiving JSON parsing
            corrected_json = json5.loads(raw_response)
            print("JSON correction applied successfully.")
            return corrected_json
        except ImportError:
            return {
                "error": "Invalid JSON and json5 is not installed. Install it using 'pip install json5'.",
                "raw_response": raw_response
            }
        except Exception as e:
            return {
                "error": f"Failed to correct JSON: {str(e)}",
                "raw_response": raw_response
            }

if __name__ == "__main__":
    # Sample email content
    email_content = (
        "Subject: Urgent - Payroll Issue\n\n"
        "Dear HR Team,\n\n"
        "I have noticed a discrepancy in my salary for this month. The amount credited is lower than expected. "
        "Please look into this matter urgently and let me know if additional details are required.\n\n"
        "Best regards,\nJohn Doe"
    )

    print("Sending email content to Ollama Llama 3.2...")
    response = query_ollama(email_content)
    print("Response from Llama 3.2:")
    print(json.dumps(response, indent=4))  # Pretty-print the JSON response