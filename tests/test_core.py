"""
Tests for core functionality of Contra Eris
"""

import os
import unittest
import tempfile
import json
from contra_eris.core import analyze_project

class TestCore(unittest.TestCase):
    """Test cases for core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test output
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name
        
        # Path to demo project for testing
        self.demo_project = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo_project')
        
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
    
    def test_analyze_project(self):
        """Test that analyze_project runs successfully on demo project"""
        # Run analysis on demo project
        result = analyze_project(
            project_path=self.demo_project,
            output_dir=self.output_dir,
            verbose=False
        )
        
        # Check that output files were created
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'cbsf.json')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'graph.json')))
        
        # Check result has expected keys
        self.assertIn('cbsf', result)
        self.assertIn('graph', result)
        self.assertIn('file_count', result)
        self.assertIn('processed_count', result)
        
        # Check that files were found and processed
        self.assertGreater(result['file_count'], 0)
        self.assertGreater(result['processed_count'], 0)
        
        # Check CBSF structure
        with open(os.path.join(self.output_dir, 'cbsf.json'), 'r') as f:
            cbsf_data = json.load(f)
            
        self.assertIn('codebase_summary', cbsf_data)
        self.assertIn('meta', cbsf_data)
        self.assertIn('graph', cbsf_data)

if __name__ == '__main__':
    unittest.main() 