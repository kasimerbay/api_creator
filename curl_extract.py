from bs4 import BeautifulSoup
import json
import re

def curl_filter(code_text):
    # Clean the curl command
    curl_command = code_text.replace('\n', ' ').replace('\\', '').strip()

    # Replace http with https
    curl_command = curl_command.replace('http://', 'https://')

    # Replace unnecessary spaces 
    curl_command = curl_command.replace("    ", " ")
    curl_command = curl_command.replace(": ", ":")
    curl_command = curl_command.replace("  ", "")
    curl_command = curl_command.replace("{ ", "{").replace(" }", "}")
    curl_command = curl_command.replace(", ", ",")
    curl_command = curl_command.replace(" ]", "]")

    # Replace unnecessary "\"
    curl_command = curl_command.replace("\"\\", "\\\"")
    # Remove 'none' from the URL
    curl_command = re.sub(r'none', '', curl_command)

    # Add "-n" as option
    curl_command = curl_command.replace("GET ", "GET -n ")
    curl_command = curl_command.replace("DELETE ", "DELETE -n ")
    curl_command = curl_command.replace("POST ", "POST -n ")
    curl_command = curl_command.replace("PUT ", "PUT -n ")

    return curl_command

with open(f"./htmls/bitbucket_permission_management.html", "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, 'html.parser')

# Extract curl commands and query parameters
curl_commands_with_params = []

# Find all <code> elements that contain curl commands
for code_tag in soup.find_all('code'):
    code_text = code_tag.get_text()

    if 'curl' in code_text:

        curl_command = curl_filter(code_text)

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

        # Add query parameters if they exist
        if query_params:
            curl_command_entry['query_parameters'] = query_params

        # Append the dictionary to the list
        curl_commands_with_params.append(curl_command_entry)

with open("curls.txt", "w") as f:
    print(json.dumps(curl_commands_with_params, indent=4), file=f)

