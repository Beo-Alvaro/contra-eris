"""
Tests for the crawler module
"""

import os
import unittest
import tempfile
from contra_eris.crawler import crawl_project

class TestCrawler(unittest.TestCase):
    """Test cases for the crawler module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory with some files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # Create some test files
        self.python_files = ['test1.py', 'test2.py', 'subdir/test3.py']
        self.other_files = ['test.txt', 'test.md', 'subdir/test.json']
        
        # Create subdirectory
        os.makedirs(os.path.join(self.test_dir, 'subdir'), exist_ok=True)
        
        # Create the files
        for file in self.python_files + self.other_files:
            file_path = os.path.join(self.test_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write("# Test file")
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
    
    def test_crawl_project_default_extensions(self):
        """Test crawling with default extensions (.py)"""
        files = crawl_project(self.test_dir)
        
        # Convert to relative paths for easier comparison
        relative_files = [os.path.relpath(f, self.test_dir) for f in files]
        
        # Check that all Python files were found
        for py_file in self.python_files:
            self.assertIn(py_file.replace('/', os.sep), relative_files)
        
        # Check that no other files were found
        for other_file in self.other_files:
            self.assertNotIn(other_file.replace('/', os.sep), relative_files)
    
    def test_crawl_project_custom_extensions(self):
        """Test crawling with custom extensions"""
        files = crawl_project(self.test_dir, extensions={".txt", ".json"})
        
        # Convert to relative paths for easier comparison
        relative_files = [os.path.relpath(f, self.test_dir) for f in files]
        
        # Check that only files with specified extensions were found
        self.assertIn("test.txt", relative_files)
        self.assertIn(os.path.join("subdir", "test.json").replace('/', os.sep), relative_files)
        
        # Check that Python files and MD files were not found
        for py_file in self.python_files:
            self.assertNotIn(py_file.replace('/', os.sep), relative_files)
        self.assertNotIn("test.md", relative_files)
    
    def test_crawl_project_no_matching_files(self):
        """Test crawling when no files match the extensions"""
        files = crawl_project(self.test_dir, extensions={".cpp", ".java"})
        self.assertEqual(len(files), 0)

if __name__ == '__main__':
    unittest.main() 