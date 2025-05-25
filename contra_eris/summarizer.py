import ast
from typing import Dict

def summarize_ast(tree: ast.AST, filename: str) -> Dict:
    """Extract summary information from AST"""
    summary = {"file": filename, "functions": [], "classes": [], "imports": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            summary["functions"].append({
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "lineno": node.lineno
            })
        elif isinstance(node, ast.ClassDef):
            summary["classes"].append({
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "lineno": node.lineno
            })
        elif isinstance(node, ast.Import):
            for n in node.names:
                summary["imports"].append(n.name)
        elif isinstance(node, ast.ImportFrom):
            for n in node.names:
                summary["imports"].append(f"{node.module}.{n.name}" if node.module else n.name)
    return summary 