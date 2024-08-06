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
    curl_command = curl_command.replace("-u username:password ", "")
    curl_command = curl_command.replace("curl ", "curl -n ")

    # Create class variables

    


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

def data_filter(curl_command:str) -> dict:
    data_params = {}

    data_match = re.search(r"--data\s+'(.*?)'", curl_command)
    if data_match:
        data_part = data_match.group(1)
        curl_command = curl_command.replace(data_match.group(0), '').strip()
            
        # Parse the data part into a dictionary
        data_params = json.loads(data_part)
    
    return data_params, curl_command

def read_html(path:str) -> BeautifulSoup:
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    return soup

def extract_curl(code_text:str, api:str) -> list:

    if 'curl' in code_text:

        # Filter curl
        curl_command = curl_filter(code_text)

        # Extract query parameters from the curl command if available
        query_params = param_filter(curl_command)

        # Extract the --data part if available
        data_params, curl_command = data_filter(curl_command)

        # Extract what curl needs as variable
        variables = []

        # Extract variables of the form /{variable}
        variables = re.findall(r'/{(.*?)}', curl_command)

        curl_command = curl_command.replace("baseurl", "self.baseurl")
        curl_command = curl_command.replace("projectKey", "self.projectKey")
        curl_command = curl_command.replace("repositorySlug", "self.repositorySlug")
        curl_command = curl_command.replace("userKey", "self.userKey")
        curl_command = curl_command.replace("hookKey", "self.hookKey")
        curl_command = curl_command.replace("pullRequestId", "self.pullRequestId")
        curl_command = curl_command.replace("commitId", "self.commitId")
        curl_command = curl_command.replace("branchName", "self.branchName")
        curl_command = curl_command.replace("issueId", "self.issueId")

        # Create a dictionary for the curl command
        curl_command_entry = {
            'type': api,
            'curl_command': curl_command,
            'variables': variables,
            'query_parameters':query_params,
            'data': data_params
        }

        # Append the dictionary to the list
        if curl_command_entry not in curl_commands_with_params and "-X " not in curl_command_entry["curl_command"]:
            curl_commands_with_params.append(curl_command_entry)

def write_curl(path:str, commands:list) -> None:
    with open(path, "w") as f:
        print(json.dumps(commands, indent=4), file=f)

def create_apis(apis:list) -> None:
    for api in apis:

        soup = read_html(path=f"../htmls/bitbucket_{api}_management.html")

        for code_tag in soup.find_all('code'):
            code_text = code_tag.get_text()
            extract_curl(code_text, api)

        for header in soup.find_all('h2'):
            text = header.get_text()
            if text != "Manage Preferences":
                h2_.append(text)

        for i in range(len(curl_commands_with_params)):
            curl_commands_with_params[i]["title"] = h2_[i]

    print(f"Total headers:{len(h2_)}")
    print(f"Total Commands:{len(curl_commands_with_params)}")
    write_curl("curls.txt", curl_commands_with_params)

def create_classes_and_methods():
    class_definitions = {}

    for command in curl_commands_with_params:
        class_name = command['type'].capitalize() + 'API'
        method_name = command['title'].replace(' ', '_').replace('-', '_').lower()
        method_name = re.sub(r'\W+', '', method_name)  # Remove any non-alphanumeric characters

        data = command.get('data', {})
        query_parameters = command.get('query_parameters', {})

        # Create the class definition if it doesn't exist
        if class_name not in class_definitions:
            class_definitions[class_name] = f"class {class_name}:\n"

        # Add the method definition
        method_definition = f"    def {method_name}(self"

        if query_parameters:
            for param in query_parameters.keys():
                method_definition += f", {param}=None"
        if data and type(data) == dict:
            for key in data.keys():
                method_definition += f", d_{key}=None"
        method_definition += "):\n"

        # Add the curl command
        curl_command = command['curl_command'].replace("'", "\"")
        method_definition += f"        curl_command = '''{curl_command}'''\n"

        # Print the curl command
        method_definition += f"        return(curl_command)\n"

        class_definitions[class_name] += method_definition + "\n"

    with open("classes.py", "w") as f:
        # Execute the class definitions
        for class_def in class_definitions.values():
            # exec(class_def)
            print(class_def, file=f)  # Optional: print the class definition



curl_commands_with_params = []
h2_ = []
apis = ["permission"]#, "project", "permission", "repository"]

create_apis(apis)
create_classes_and_methods()