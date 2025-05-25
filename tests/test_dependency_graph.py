"""
Tests for the dependency_graph module
"""

import unittest
from contra_eris.dependency_graph import build_dependency_graph

class TestDependencyGraph(unittest.TestCase):
    """Test cases for the dependency_graph module"""
    
    def setUp(self):
        """Set up test environment"""
        # Sample file summaries for testing
        self.summaries = [
            {
                "file": "main.py",
                "imports": ["utils", "data_processor", "config"],
                "functions": [],
                "classes": []
            },
            {
                "file": "utils.py",
                "imports": ["math", "datetime"],
                "functions": [{"name": "helper", "docstring": "Helper function", "lineno": 5}],
                "classes": []
            },
            {
                "file": "data_processor.py",
                "imports": ["utils", "numpy"],
                "functions": [],
                "classes": [{"name": "Processor", "docstring": "Data processor", "lineno": 10}]
            },
            {
                "file": "config.py",
                "imports": [],
                "functions": [],
                "classes": [{"name": "Config", "docstring": "Configuration", "lineno": 3}]
            }
        ]
    
    def test_build_dependency_graph_structure(self):
        """Test that the graph has the correct structure"""
        graph = build_dependency_graph(self.summaries)
        
        # Check that the graph has nodes and edges
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertIsInstance(graph["nodes"], list)
        self.assertIsInstance(graph["edges"], list)
    
    def test_build_dependency_graph_nodes(self):
        """Test that all files are added as nodes"""
        graph = build_dependency_graph(self.summaries)
        
        # Check that all files are added as nodes
        self.assertEqual(len(graph["nodes"]), len(self.summaries))
        for summary in self.summaries:
            self.assertIn(summary["file"], graph["nodes"])
    
    def test_build_dependency_graph_edges(self):
        """Test that dependencies are correctly identified as edges"""
        graph = build_dependency_graph(self.summaries)
        
        # Convert edges to tuples for easier testing
        edges = [(e["from"], e["to"]) for e in graph["edges"]]
        
        # Check main.py dependencies
        self.assertIn(("main.py", "utils.py"), edges)
        self.assertIn(("main.py", "data_processor.py"), edges)
        self.assertIn(("main.py", "config.py"), edges)
        
        # Check data_processor.py dependencies
        self.assertIn(("data_processor.py", "utils.py"), edges)
        
        # utils.py and config.py don't have internal dependencies
        
        # Check total number of edges
        self.assertEqual(len(graph["edges"]), 4)
    
    def test_build_dependency_graph_empty(self):
        """Test building a graph with no files"""
        graph = build_dependency_graph([])
        self.assertEqual(len(graph["nodes"]), 0)
        self.assertEqual(len(graph["edges"]), 0)
    
    def test_build_dependency_graph_no_dependencies(self):
        """Test building a graph with files that have no dependencies"""
        summaries = [
            {
                "file": "standalone1.py",
                "imports": [],
                "functions": [],
                "classes": []
            },
            {
                "file": "standalone2.py",
                "imports": [],
                "functions": [],
                "classes": []
            }
        ]
        
        graph = build_dependency_graph(summaries)
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(len(graph["edges"]), 0)
    
    def test_build_dependency_graph_class_imports(self):
        """Test that imports of specific classes are detected"""
        summaries = [
            {
                "file": "app.py",
                "imports": ["models.User", "utils"],
                "functions": [],
                "classes": []
            },
            {
                "file": "models.py",
                "imports": [],
                "functions": [],
                "classes": [{"name": "User", "docstring": "User model", "lineno": 5}]
            },
            {
                "file": "utils.py",
                "imports": [],
                "functions": [],
                "classes": []
            }
        ]
        
        graph = build_dependency_graph(summaries)
        edges = [(e["from"], e["to"]) for e in graph["edges"]]
        
        self.assertIn(("app.py", "models.py"), edges)
        self.assertIn(("app.py", "utils.py"), edges)
        self.assertEqual(len(graph["edges"]), 2)

if __name__ == '__main__':
    unittest.main() 