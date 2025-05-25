"""
Python code parser for Contra Eris
"""

import ast

def parse_python_file(filepath):
    """Parse a Python file into AST"""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    return ast.parse(code) 