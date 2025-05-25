"""
Tests for the cbsf_generator module
"""

import unittest
from contra_eris.cbsf_generator import generate_cbsf

class TestCbsfGenerator(unittest.TestCase):
    """Test cases for the cbsf_generator module"""
    
    def setUp(self):
        """Set up test environment"""
        # Sample file summaries for testing
        self.summaries = [
            {
                "file": "main.py",
                "imports": ["utils", "config"],
                "functions": [{"name": "main", "docstring": "Main function", "lineno": 10}],
                "classes": []
            },
            {
                "file": "utils.py",
                "imports": ["os", "sys"],
                "functions": [{"name": "helper", "docstring": "Helper function", "lineno": 5}],
                "classes": []
            },
            {
                "file": "config.py",
                "imports": [],
                "functions": [],
                "classes": [{"name": "Config", "docstring": "Configuration", "lineno": 3}]
            }
        ]
    
    def test_generate_cbsf_structure(self):
        """Test that the CBSF has the correct structure"""
        cbsf = generate_cbsf(self.summaries)
        
        # Check overall structure
        self.assertIn("codebase_summary", cbsf)
        self.assertIn("meta", cbsf)
    
    def test_generate_cbsf_summary(self):
        """Test that the summary contains all file data"""
        cbsf = generate_cbsf(self.summaries)
        
        # Check that the summary contains all file data
        self.assertEqual(cbsf["codebase_summary"], self.summaries)
    
    def test_generate_cbsf_meta(self):
        """Test that the meta section has the correct data"""
        cbsf = generate_cbsf(self.summaries)
        
        # Check meta data
        self.assertIn("file_count", cbsf["meta"])
        self.assertEqual(cbsf["meta"]["file_count"], len(self.summaries))
    
    def test_generate_cbsf_empty(self):
        """Test generating CBSF with no file summaries"""
        cbsf = generate_cbsf([])
        
        # Check that structure is maintained
        self.assertIn("codebase_summary", cbsf)
        self.assertEqual(cbsf["codebase_summary"], [])
        self.assertIn("meta", cbsf)
        self.assertEqual(cbsf["meta"]["file_count"], 0)
    
    def test_generate_cbsf_with_graph(self):
        """Test generating CBSF with a graph included"""
        # Sample graph
        graph = {
            "nodes": ["main.py", "utils.py", "config.py"],
            "edges": [
                {"from": "main.py", "to": "utils.py"},
                {"from": "main.py", "to": "config.py"}
            ]
        }
        
        # Add graph to summaries
        summaries_with_graph = self.summaries.copy()
        
        # Generate CBSF with graph
        cbsf = generate_cbsf(summaries_with_graph)
        cbsf["graph"] = graph
        
        # Check that graph is included
        self.assertIn("graph", cbsf)
        self.assertEqual(cbsf["graph"]["nodes"], graph["nodes"])
        self.assertEqual(cbsf["graph"]["edges"], graph["edges"])

if __name__ == '__main__':
    unittest.main() 