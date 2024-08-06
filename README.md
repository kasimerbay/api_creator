
# API Command Extractor and Class Generator

This project is designed to extract `curl` commands from HTML files, clean and format them, and then generate Python classes and methods based on the extracted commands. The classes are grouped by the kind of variables used in the `curl` commands.


## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Functions](#functions)
  - [curl_filter](#curl_filter)
  - [param_filter](#param_filter)
  - [data_filter](#data_filter)
  - [read_html](#read_html)
  - [extract_curl](#extract_curl)
  - [write_curl](#write_curl)
  - [create_apis](#create_apis)
  - [generate_class_name](#generate_class_name)
  - [create_method_definition](#create_method_definition)
  - [create_init_method](#create_init_method)
  - [create_classes_and_methods](#create_classes_and_methods)
- [Example](#example)
- [Contributing](#contributing)
- [License](#license)
## Prerequisites

- Python 3.x
- `BeautifulSoup` library
- `requests` library

You can install the required libraries using the following command:

```sh
python3 -m pip install beautifulsoup4 requests
```
## Installation

Clone the repository:
```sh
git clone https://github.com/yourusername/api-command-extractor.git
```

Navigate to the project directory:
```sh
cd api-command-extractor
```
    
## Usage

Prepare your HTML files containing curl commands. Place them in a directory (e.g., htmls/).
Update the apis list with the desired API types.
Run the script:

```sh
python curl_extract.py
```


## Functions

### `curl_filter`

Filters and cleans the `curl` command.

**Parameters:**
- `code_text` (str): The `curl` command as a string.

**Returns:**
- `str`: The cleaned `curl` command.

### `param_filter`

Extracts query parameters from the `curl` command.

**Parameters:**
- `curl_command` (str): The `curl` command.

**Returns:**
- `dict`: A dictionary of query parameters.

### `data_filter`

Extracts `--data` parameters from the `curl` command.

**Parameters:**
- `curl_command` (str): The `curl` command.

**Returns:**
- `dict`: A dictionary of data parameters.
- `str`: The cleaned `curl` command without `--data` part.

### `read_html`

Reads and parses an HTML file.

**Parameters:**
- `path` (str): The path to the HTML file.

**Returns:**
- `BeautifulSoup`: Parsed HTML content.

### `extract_curl`

Extracts `curl` commands from the HTML content.

**Parameters:**
- `code_text` (str): The `curl` command as a string.
- `api` (str): The API type.

### `write_curl`

Writes the extracted `curl` commands to a file.

**Parameters:**
- `path` (str): The file path to write to.
- `commands` (list): List of `curl` commands.

### `create_apis`

Creates API commands by reading HTML files and extracting `curl` commands.

**Parameters:**
- `apis` (list): List of API types.

### `generate_class_name`

Generates a class name based on a set of variables.

**Parameters:**
- `variable_set` (set): A set of variables.

**Returns:**
- `str`: The generated class name.

### `create_method_definition`

Generates a method definition from a command dictionary.

**Parameters:**
- `command` (dict): The command dictionary.

**Returns:**
- `str`: The method definition.

### `create_init_method`

Generates the `__init__` method for the class based on the variable set.

**Parameters:**
- `variable_set` (set): A set of variables.

**Returns:**
- `str`: The `__init__` method definition.

### `create_classes_and_methods`

Creates Python classes and methods from `curl_commands_with_params`.
## Appendix

1. **Place HTML Files**: Place your HTML files in a directory (e.g., `htmls/`).
2. **Update `apis` List**: Update the `apis` list with the desired API types.
3. **Run the Script**: Execute the script to generate the classes.
    ```sh
    python extract_and_generate.py
    ```

