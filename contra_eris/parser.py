import ast

def parse_code_file(filepath: str):
    """Parse a Python file into AST"""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    return ast.parse(code) 