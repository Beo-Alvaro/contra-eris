"""
Tests for the parser module
"""

import os
import ast
import unittest
import tempfile
from contra_eris.parser import parse_code_file

class TestParser(unittest.TestCase):
    """Test cases for the parser module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory with a test file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "test_sample.py")
        
        # Create a Python file with various elements
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("""
# Test Python file
import os
import sys
from datetime import datetime

def test_function():
    \"\"\"This is a test function\"\"\"
    return "Hello, world!"

class TestClass:
    \"\"\"This is a test class\"\"\"
    
    def __init__(self):
        \"\"\"Constructor\"\"\"
        self.value = 42
    
    def method(self, param):
        \"\"\"A method with a parameter\"\"\"
        return param * self.value
""")
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
    
    def test_parse_code_file(self):
        """Test parsing a Python file into AST"""
        tree = parse_code_file(self.test_file)
        
        # Check that the result is an AST Module
        self.assertIsInstance(tree, ast.Module)
        
        # Check imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 3)
        
        # Check function definition
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "test_function"]
        self.assertEqual(len(functions), 1)
        self.assertEqual(ast.get_docstring(functions[0]), "This is a test function")
        
        # Check class definition
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].name, "TestClass")
        self.assertEqual(ast.get_docstring(classes[0]), "This is a test class")
        
        # Check methods in the class
        methods = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name in ("__init__", "method")]
        self.assertEqual(len(methods), 2)
    
    def test_parse_invalid_file(self):
        """Test parsing an invalid Python file"""
        # Create a file with syntax error
        invalid_file = os.path.join(self.temp_dir.name, "invalid.py")
        with open(invalid_file, "w") as f:
            f.write("def invalid_function(:\n    return 'missing parenthesis'")
        
        # Parsing should raise a SyntaxError
        with self.assertRaises(SyntaxError):
            parse_code_file(invalid_file)
    
    def test_parse_empty_file(self):
        """Test parsing an empty file"""
        empty_file = os.path.join(self.temp_dir.name, "empty.py")
        with open(empty_file, "w") as f:
            f.write("")
        
        # Should parse successfully and return an empty Module
        tree = parse_code_file(empty_file)
        self.assertIsInstance(tree, ast.Module)
        self.assertEqual(len(tree.body), 0)
    
    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        nonexistent_file = os.path.join(self.temp_dir.name, "nonexistent.py")
        
        # Should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            parse_code_file(nonexistent_file)

if __name__ == '__main__':
    unittest.main() 