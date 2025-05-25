"""
Language-specific parsers for Contra Eris
"""

from contra_eris.parsers.python_parser import parse_python_file
from contra_eris.parsers.javascript_parser import parse_javascript_file
from contra_eris.parsers.html_parser import parse_html_file

def get_parser_for_extension(extension):
    """Returns the appropriate parser function for a given file extension"""
    extension = extension.lower()
    if extension == '.py':
        return parse_python_file
    elif extension == '.js':
        return parse_javascript_file
    elif extension == '.html' or extension == '.htm':
        return parse_html_file
    else:
        raise ValueError(f"No parser available for extension: {extension}") 