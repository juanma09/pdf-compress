import base64
import os

def file_to_base64(filepath):
    """Reads a file and returns its Base64 string representation."""
    with open(filepath, "rb") as file:
        encoded_string = base64.b64encode(file.read())
        return encoded_string.decode('utf-8')

def base64_to_file(b64_string, output_filepath):
    """Converts a Base64 string back into a physical file."""
    with open(output_filepath, "wb") as file:
        file.write(base64.b64decode(b64_string))