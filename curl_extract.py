from bs4 import BeautifulSoup
import json
import re

# Load the HTML content from the file
with open("bitbucket_permission_management.html", "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, 'html.parser')

# Extract curl commands and query parameters
curl_commands_with_params = []

# Find all <code> elements that contain curl commands
for code_tag in soup.find_all('code'):
    code_text = code_tag.get_text()
    if 'curl' in code_text:
        # Clean the curl command
        curl_command = code_text.replace('\n', ' ').replace('\\', '').strip()
        
        # Replace http with https
        curl_command = curl_command.replace('http://', 'https://')
        
        # Remove any spaces after colon
        curl_command = re.sub(r':\s+', ':', curl_command)
        
        # Remove 'none' from the URL
        curl_command = re.sub(r'none', '', curl_command)

        # Extract and remove --data sections
        data_sections = {}

        def extract_data(match):
            key = '--data'
            value = match.group(1).strip('"\'')
            data_sections[key] = f'"{value}"'  # Enclose the value in double quotes
            return ''  # Remove the --data part from the curl command
        
        # Adjust regex to match --data and its value (with or without quotes)
        curl_command = re.sub(r'--data\s+(".*?"|\'.*?\'|\S+)', extract_data, curl_command)
        
        
        # Extract query parameters from the curl command if available
        query_params = {}

        if '?' in curl_command:
            params_str = curl_command.split('?', 1)[1]
            params_str = params_str.split(' ', 1)[0]
            param_pairs = params_str.split('&')
            for pair in param_pairs:
                if '=' in pair:
                    key, value = pair.split('=')
                    query_params[key] = value
        
        # Create a dictionary for the curl command
        curl_command_entry = {
            'curl_command': curl_command
        }

        # Add --data sections if they exist
        if data_sections:
            curl_command_entry['data_sections'] = data_sections

        # Add query parameters if they exist
        if query_params:
            curl_command_entry['query_parameters'] = query_params

        # Append the dictionary to the list
        curl_commands_with_params.append(curl_command_entry)

# Output the extracted details
print(json.dumps(curl_commands_with_params, indent=4))
