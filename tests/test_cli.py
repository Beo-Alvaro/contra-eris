"""
Tests for Contra Eris CLI functionality
"""

import os
import unittest
import tempfile
import subprocess
import sys

class TestCLI(unittest.TestCase):
    """Test cases for CLI commands"""
    
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
    
    def test_generate_command(self):
        """Test the generate command"""
        # Run the command through subprocess
        result = subprocess.run(
            [
                sys.executable, '-m', 'contra_eris.cli', 'generate',
                '--project', self.demo_project,
                '--output', self.output_dir,
                '--quiet'
            ],
            capture_output=True,
            text=True
        )
        
        # Check command executed successfully
        self.assertEqual(result.returncode, 0, f"CLI command failed: {result.stderr}")
        
        # Check output files exist
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'cbsf.json')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'graph.json')))

    def test_evaluate_command(self):
        """Test the evaluate command"""
        # First generate a CBSF
        subprocess.run(
            [
                sys.executable, '-m', 'contra_eris.cli', 'generate',
                '--project', self.demo_project,
                '--output', self.output_dir,
                '--quiet'
            ]
        )
        
        # Now run the evaluate command
        result = subprocess.run(
            [
                sys.executable, '-m', 'contra_eris.cli', 'evaluate',
                '--project', self.demo_project,
                '--cbsf', os.path.join(self.output_dir, 'cbsf.json'),
                '--quiet'
            ],
            capture_output=True,
            text=True
        )
        
        # Check command executed successfully
        self.assertEqual(result.returncode, 0, f"CLI command failed: {result.stderr}")

if __name__ == '__main__':
    unittest.main() 