import google.generativeai as genai
import yaml
import json
import re

CONFIG_PATH = r"config.yaml"

with open(CONFIG_PATH) as file:
    config = yaml.safe_load(file)
    api_key = config.get('GEMINI_API_KEY')

genai.configure(api_key=api_key)

def split_full_name(full_name):
    """Splits full name into First, Middle, and Last Name."""
    name_parts = full_name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    return first_name, middle_name, last_name

def ats_extractor(resume_text):
    prompt = """
    Extract the following details from the resume in **valid JSON format only**:
    {
      "Full Name": "",
      "Email ID": "",
      "GitHub Portfolio": "",
      "LinkedIn ID": "",
      "Employment Details": [
        {
          "Designation": "",
          "Duration": "",
          "Organization": ""
        }
      ],
      "Technical Skills": ["Skill1", "Skill2", "Skill3"],
      "Soft Skills": ["Skill1", "Skill2", "Skill3"]
    }

    - **Return only valid JSON**.
    - **Do not include any explanations or markdown formatting**.
    """

    model = genai.GenerativeModel('models/gemini-1.5-pro')
    response = model.generate_content([prompt, resume_text])

    raw_text = response.text.strip()

    # Remove markdown formatting if present
    cleaned_json = re.sub(r"```json\n|\n```", "", raw_text).strip()

    try:
        parsed_data = json.loads(cleaned_json)  # Convert string to JSON

        # Ensure parsed_data is a dictionary
        if isinstance(parsed_data, str):
            parsed_data = json.loads(parsed_data)

        # Process full name
        first_name, middle_name, last_name = split_full_name(parsed_data.get("Full Name", "Not Provided"))

        # Convert Technical Skills list into a comma-separated string
        technical_skills = ", ".join(parsed_data.get("Technical Skills", []))

        # Format output
        formatted_output = {
            "First Name": first_name,
            "Middle Name": middle_name,
            "Last Name": last_name,
            "Email ID": parsed_data.get("Email ID", "Not Provided"),
            "GitHub Portfolio": parsed_data.get("GitHub Portfolio", "Not Provided"),
            "LinkedIn ID": parsed_data.get("LinkedIn ID", "Not Provided"),
            "Employment Details": parsed_data.get("Employment Details", []),
            "Technical Skills": technical_skills,  # Stored as a single string
            "Soft Skills": parsed_data.get("Soft Skills", [])
        }

        return formatted_output

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_response": raw_text}
