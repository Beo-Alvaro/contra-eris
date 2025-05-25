"""
AST summarizers for different languages
"""

from contra_eris.summarizers.python_summarizer import summarize_python_ast
from contra_eris.summarizers.javascript_summarizer import summarize_javascript_ast
from contra_eris.summarizers.html_summarizer import summarize_html_ast

def get_summarizer_for_extension(extension):
    """Returns the appropriate summarizer function for a given file extension"""
    extension = extension.lower()
    if extension == '.py':
        return summarize_python_ast
    elif extension == '.js':
        return summarize_javascript_ast
    elif extension == '.html' or extension == '.htm':
        return summarize_html_ast
    else:
        raise ValueError(f"No summarizer available for extension: {extension}") 