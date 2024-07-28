from bs4 import BeautifulSoup
import json
import re

def curl_filter(code_text:str) -> str:
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
    curl_command = curl_command.replace("curl ", "curl -n ")

    return curl_command

def param_filter(curl_command:str) -> dict:
    query_params = {}

    if '?' in curl_command:
        params_str = curl_command.split('?', 1)[1]
        params_str = params_str.split(' ', 1)[0]
        param_pairs = params_str.split('&')
        for pair in param_pairs:
            if '=' in pair:
                key, value = pair.split('=')
                query_params[key] = value
    
    return query_params

def read_html(path:str) -> BeautifulSoup:
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    return soup

def extract_curl(code_tag:str) -> list[str]:
    code_text = code_tag.get_text()

    if 'curl' in code_text:

        curl_command = curl_filter(code_text)

        # Extract query parameters from the curl command if available
        query_params = param_filter(curl_command)

        # Create a dictionary for the curl command
        curl_command_entry = {
            'curl_command': curl_command
        }

        # Add query parameters if they exist
        if query_params:
            curl_command_entry['query_parameters'] = query_params

        # Append the dictionary to the list
        if curl_command_entry not in curl_commands_with_params:
            curl_commands_with_params.append(curl_command_entry)

def write_curl(path:str, commands:list) -> None:
    with open(path, "w") as f:
        print(json.dumps(commands, indent=4), file=f)


curl_commands_with_params = []

soup = read_html(path=f"../htmls/bitbucket_permission_management.html")

for code_tag in soup.find_all('code'):
    command = extract_curl(code_tag)

print(len(curl_commands_with_params))
write_curl("curls.txt", curl_commands_with_params)
