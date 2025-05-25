"""
HTML parser for Contra Eris
"""

from bs4 import BeautifulSoup

def parse_html_file(filepath):
    """Parse an HTML file using BeautifulSoup"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    try:
        # Create a structured HTML tree
        soup = BeautifulSoup(content, 'html.parser')
        
        # Store source file in the parser result
        soup.source_file = filepath
        
        # Attach line numbers to elements if possible
        # BeautifulSoup doesn't provide line numbers directly, 
        # but we can try to calculate them
        line_counter = 1
        for line in content.split('\n'):
            line_counter += 1
            
        return soup
    except Exception as e:
        # Add file info to error message
        error_msg = f"Error parsing HTML file {filepath}: {str(e)}"
        raise SyntaxError(error_msg) from e 