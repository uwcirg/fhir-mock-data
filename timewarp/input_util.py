import json


def determine_file_type(file_path: str) -> str:
    """
    Determine if a file is of type JSON or NDJSON (Newline Delimited JSON).

    Args:
        file_path (str): The path to the file.

    Returns:
        str: "JSON" if the file is JSON, "NDJSON" if the file is NDJSON.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()  # Read entire content and strip leading/trailing whitespace

        # Check for JSON by attempting to load the entire content
        try:
            json_obj = json.loads(content)
            if isinstance(json_obj, (dict, list)):  # Valid JSON must be a dictionary or a list
                return "JSON"
        except json.JSONDecodeError:
            pass  # Fall through to check NDJSON

        # Check for NDJSON by validating line by line
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():  # Ignore empty lines
                    json.loads(line)  # Validate each line as JSON
            return "NDJSON"

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON or NDJSON in file {}".format(file_path))
    except Exception as e:
        raise IOError(f"Error reading file: {e}")


def next_json_object(file_path: str) -> dict:
    if determine_file_type(file_path) == "NDJSON":
        with open(file_path, 'r') as ndjson:
            for line in ndjson:
                try:
                    obj = json.loads(line.strip())
                    yield obj
                except AttributeError as ae:
                    print(f"Can't parse line '{line}' from {file_path} : {ae}")
                    raise ae
    else:
        with open(file_path, 'r') as json_file:
            try:
                obj = json.loads(json_file.read().strip())
                yield obj
            except AttributeError as ae:
                print(f"Can't parse {file_path} : {ae}")
                raise ae
