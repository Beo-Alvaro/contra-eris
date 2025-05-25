"""
JavaScript code parser for Contra Eris
"""

import esprima

def parse_javascript_file(filepath):
    """Parse a JavaScript file into AST using esprima"""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    
    try:
        # Parse JS with full source info and location data
        return esprima.parseScript(code, options={
            'loc': True,
            'range': True,
            'comment': True
        })
    except Exception as e:
        # Add file info to error message
        error_msg = f"Error parsing JavaScript file {filepath}: {str(e)}"
        raise SyntaxError(error_msg) from e 