"""
Tests for the summarizer module
"""

import os
import ast
import unittest
import tempfile
from contra_eris.summarizer import summarize_ast

class TestSummarizer(unittest.TestCase):
    """Test cases for the summarizer module"""
    
    def setUp(self):
        """Set up test environment"""
        # Sample Python code to test with
        self.sample_code = """
import os
import sys
from datetime import datetime

CONSTANT = 42

def helper_function(param):
    \"\"\"A helper function\"\"\"
    return param * 2

class TestClass:
    \"\"\"A test class\"\"\"
    
    def __init__(self, value=0):
        \"\"\"Constructor\"\"\"
        self.value = value
    
    def process(self, data):
        \"\"\"Process some data\"\"\"
        return data + self.value
"""
        # Parse the sample code
        self.tree = ast.parse(self.sample_code)
        self.filename = "test_file.py"
    
    def test_summarize_ast_structure(self):
        """Test that summarize_ast returns the correct structure"""
        summary = summarize_ast(self.tree, self.filename)
        
        # Check basic structure
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["file"], self.filename)
        self.assertIn("functions", summary)
        self.assertIn("classes", summary)
        self.assertIn("imports", summary)
    
    def test_summarize_ast_imports(self):
        """Test that imports are correctly extracted"""
        summary = summarize_ast(self.tree, self.filename)
        
        # Check imports
        self.assertEqual(len(summary["imports"]), 3)
        self.assertIn("os", summary["imports"])
        self.assertIn("sys", summary["imports"])
        self.assertIn("datetime.datetime", summary["imports"])
    
    def test_summarize_ast_functions(self):
        """Test that functions are correctly extracted"""
        summary = summarize_ast(self.tree, self.filename)
        
        # Check functions - there are 3 functions: helper_function, __init__, and process
        self.assertEqual(len(summary["functions"]), 3)
        
        # Check if helper_function is present
        helper_function = next((f for f in summary["functions"] if f["name"] == "helper_function"), None)
        self.assertIsNotNone(helper_function)
        self.assertEqual(helper_function["docstring"], "A helper function")
        self.assertIn("lineno", helper_function)
        
        # Check if the class methods are present
        init_method = next((f for f in summary["functions"] if f["name"] == "__init__"), None)
        self.assertIsNotNone(init_method)
        
        process_method = next((f for f in summary["functions"] if f["name"] == "process"), None)
        self.assertIsNotNone(process_method)
    
    def test_summarize_ast_classes(self):
        """Test that classes are correctly extracted"""
        summary = summarize_ast(self.tree, self.filename)
        
        # Check classes
        self.assertEqual(len(summary["classes"]), 1)
        cls = summary["classes"][0]
        self.assertEqual(cls["name"], "TestClass")
        self.assertEqual(cls["docstring"], "A test class")
        self.assertIn("lineno", cls)
    
    def test_summarize_ast_empty(self):
        """Test summarizing an empty AST"""
        empty_tree = ast.parse("")
        summary = summarize_ast(empty_tree, "empty.py")
        
        # Check that structure is maintained even when empty
        self.assertEqual(summary["file"], "empty.py")
        self.assertEqual(summary["functions"], [])
        self.assertEqual(summary["classes"], [])
        self.assertEqual(summary["imports"], [])
    
    def test_summarize_ast_complex_imports(self):
        """Test summarizing complex imports"""
        complex_imports = """
import os.path as path
from sys import version, argv
from typing import Dict, List, Optional, Union
import matplotlib.pyplot as plt
"""
        tree = ast.parse(complex_imports)
        summary = summarize_ast(tree, "imports.py")
        
        # Check that complex imports are handled correctly
        imports = summary["imports"]
        # The actual number is 8 imports due to the way the imports are parsed
        self.assertEqual(len(imports), 8)
        self.assertIn("os.path", imports)
        self.assertIn("sys.version", imports)
        self.assertIn("sys.argv", imports)
        self.assertIn("typing.Dict", imports)
        self.assertIn("typing.List", imports)
        self.assertIn("typing.Optional", imports)
        self.assertIn("typing.Union", imports)
        self.assertIn("matplotlib.pyplot", imports)

if __name__ == '__main__':
    unittest.main()