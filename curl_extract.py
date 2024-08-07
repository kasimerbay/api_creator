from bs4 import BeautifulSoup
from itertools import chain
from collections import defaultdict
import json, re, os

def read_html(path:str) -> BeautifulSoup:
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    return soup

def write_curl(path:str, commands:list) -> None:
    with open(path, "w") as f:
        print(json.dumps(commands, indent=4), file=f)

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

def variables_filter(curl_command:str) -> dict:
    # Extract what curl needs as variable
    variables = []

    # Extract variables of the form /{variable}
    variables = re.findall(r'/{(.*?)}', curl_command)

    return variables

def extract_curl(code_text:str, api:str) -> list:

    if 'curl' in code_text:

        # Filter curl
        curl_command = curl_filter(code_text)

        # Extract query parameters from the curl command if available
        query_params = param_filter(curl_command)

        # Extract the --data part if available
        data_params, curl_command = data_filter(curl_command)

        # Extract what curl needs as variable
        variables = variables_filter(curl_command)

        curl_command = curl_command.replace("{baseurl}", "{self.baseurl}")
        curl_command = curl_command.replace("{projectKey}", "{self.projectKey}")
        curl_command = curl_command.replace("{repositorySlug}", "{self.repositorySlug}")
        curl_command = curl_command.replace("{userKey}", "{self.userKey}")
        curl_command = curl_command.replace("{hookKey}", "{self.hookKey}")
        curl_command = curl_command.replace("{pullRequestId}", "{self.pullRequestId}")
        curl_command = curl_command.replace("{commitId}", "{self.commitId}")
        curl_command = curl_command.replace("{branchName}", "{self.branchName}")
        curl_command = curl_command.replace("{issueId}", "{self.issueId}")
        curl_command = curl_command.replace("{keyId}", "{self.keyId}")
        curl_command = curl_command.replace("{permission}", "{self.permission}")
        curl_command = curl_command.replace("{tokenId}", "{self.tokenId}")
        curl_command = curl_command.replace("{userSlug}", "{self.userSlug}")
        curl_command = curl_command.replace("{key}", "{self.key}")
        curl_command = curl_command.replace("{externalId}", "{self.externalId}")
        curl_command = curl_command.replace("{id}", "{self.id}")
        curl_command = curl_command.replace("{attachmentId}", "{self.attachmentId}")
        curl_command = curl_command.replace("{path}", "{self.path}")
        curl_command = curl_command.replace("{commentId}", "{self.commentId}")
        curl_command = curl_command.replace("{scriptId}", "{self.scriptId}")
        curl_command = curl_command.replace("{labelName}", "{self.labelName}")
        curl_command = curl_command.replace("{webhookId}", "{self.webhookId}")
        curl_command = curl_command.replace("{taskId}", "{self.taskId}")
        curl_command = curl_command.replace("{scmId}", "{self.scmId}")


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

def create_apis(paths:list) -> None:
    for path in paths:

        soup = read_html(path="../htmls/"+path)

        for code_tag in soup.find_all('code'):
            code_text = code_tag.get_text()
            extract_curl(code_text, path.split("_")[1])

        for header in soup.find_all('h2'):
            text = header.get_text()
            if text != "Manage Preferences":
                h2_.append(text)

        for i in range(len(curl_commands_with_params)):
            curl_commands_with_params[i]["title"] = h2_[i]

    print(f"Total headers:{len(h2_)}")
    print(f"Total Commands:{len(curl_commands_with_params)}")
    # write_curl("curls.txt", curl_commands_with_params)

def generate_class_name(variable_set):
    """Generate a class name based on a set of variables."""
    return 'API_' + '_'.join(sorted(variable_set))

def create_method_definition(command):
    """Generate method definition from a command dictionary."""
    method_name = command['title'].replace(' ', '_').replace('-', '_').lower()
    method_name = re.sub(r'\W+', '', method_name)  # Remove any non-alphanumeric characters

    data = command.get('data', {})
    query_parameters = command.get('query_parameters', {})

    method_definition = f"    def {method_name}(self"

    if data:
        method_definition += ", data=None"

    if query_parameters:
        for param in query_parameters.keys():
            method_definition += f", {param}=None"
    
    method_definition += "):\n"

    # Add the curl command with proper formatting
    curl_command = command['curl_command'].replace("'", "\"")
    if data:
        curl_command += " --data '''{data}''' "
    method_definition += f'        curl_command = f"""{curl_command} """ \n'

    # Print the curl command
    method_definition += f"        return curl_command\n"

    return method_definition

def create_init_method(variable_set):
    """Generate the __init__ method for the class based on the variable set."""
    init_method = "    def __init__(self"
    for var in variable_set:
        init_method += f", {var}=None"
    init_method += "):\n"

    for var in variable_set:
        init_method += f"        self.{var} = {var}\n"

    return init_method

def create_classes_and_methods():
    """Create Python classes and methods from curl_commands_with_params."""
    # Group commands by unique sets of variables
    variable_grouped_commands = defaultdict(list)

    for command in curl_commands_with_params:
        variable_set = frozenset(command['variables'])
        variable_grouped_commands[variable_set].append(command)
    
    class_definitions = {}

    for variable_set, commands in variable_grouped_commands.items():
        class_name = generate_class_name(variable_set)
        
        if class_name not in class_definitions:
            class_definitions[class_name] = f"class {class_name}:\n"
            class_definitions[class_name] += create_init_method(variable_set) + "\n"

        for command in commands:
            method_definition = create_method_definition(command)
            class_definitions[class_name] += method_definition + "\n"

    with open("classes.py", "w") as f:
        for class_def in class_definitions.values():
            print(class_def, file=f)  # Write the class definition to the file


curl_commands_with_params = []
h2_ = []
files = [f for f in os.listdir("../htmls/")]

create_apis(files)
create_classes_and_methods()