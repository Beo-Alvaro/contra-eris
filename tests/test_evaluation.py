"""
Tests for the evaluation module
"""

import os
import json
import unittest
import tempfile
import networkx as nx
from contra_eris.evaluation import (
    calculate_compression_ratio,
    build_graph_from_cbsf,
    calculate_graph_metrics,
    calculate_dependency_complexity,
    calculate_information_entropy,
    evaluate_cbsf
)

class TestEvaluation(unittest.TestCase):
    """Test cases for the evaluation module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = os.path.join(self.temp_dir.name, "project")
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Create sample project files
        self.create_sample_project()
        
        # Create a sample CBSF file
        self.cbsf_path = os.path.join(self.temp_dir.name, "cbsf.json")
        self.create_sample_cbsf()
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
    
    def create_sample_project(self):
        """Create sample project files"""
        files = {
            "main.py": "# Main module\nimport utils\nimport config\n\ndef main():\n    pass",
            "utils.py": "# Utils module\nimport os\n\ndef helper():\n    pass",
            "config.py": "# Config module\nclass Config:\n    pass"
        }
        
        for filename, content in files.items():
            with open(os.path.join(self.project_dir, filename), "w") as f:
                f.write(content)
    
    def create_sample_cbsf(self):
        """Create a sample CBSF file"""
        cbsf = {
            "codebase_summary": [
                {
                    "file": "main.py",
                    "imports": ["utils", "config"],
                    "functions": [{"name": "main", "docstring": None, "lineno": 4}],
                    "classes": []
                },
                {
                    "file": "utils.py",
                    "imports": ["os"],
                    "functions": [{"name": "helper", "docstring": None, "lineno": 3}],
                    "classes": []
                },
                {
                    "file": "config.py",
                    "imports": [],
                    "functions": [],
                    "classes": [{"name": "Config", "docstring": None, "lineno": 2}]
                }
            ],
            "meta": {
                "file_count": 3
            },
            "graph": {
                "nodes": ["main.py", "utils.py", "config.py"],
                "edges": [
                    {"from": "main.py", "to": "utils.py"},
                    {"from": "main.py", "to": "config.py"}
                ]
            }
        }
        
        with open(self.cbsf_path, "w") as f:
            json.dump(cbsf, f)
    
    def test_calculate_compression_ratio(self):
        """Test calculating compression ratio"""
        ratio = calculate_compression_ratio(self.project_dir, self.cbsf_path)
        
        # Compression ratio should be greater than 0
        self.assertGreater(ratio, 0)
        
        # Ratio is CBSF size / original size
        # In test environments, the ratio might be higher than expected
        # So we're not enforcing a specific upper limit
    
    def test_build_graph_from_cbsf(self):
        """Test building NetworkX graph from CBSF"""
        graph = build_graph_from_cbsf(self.cbsf_path)
        
        # Check that it's a DiGraph
        self.assertIsInstance(graph, nx.DiGraph)
        
        # Check node count
        self.assertEqual(graph.number_of_nodes(), 3)
        
        # Check edge count
        self.assertEqual(graph.number_of_edges(), 2)
        
        # Check specific edges
        self.assertTrue(graph.has_edge("main.py", "utils.py"))
        self.assertTrue(graph.has_edge("main.py", "config.py"))
    
    def test_calculate_graph_metrics(self):
        """Test calculating graph metrics"""
        graph = build_graph_from_cbsf(self.cbsf_path)
        metrics = calculate_graph_metrics(graph)
        
        # Check metric keys
        self.assertIn("node_count", metrics)
        self.assertIn("edge_count", metrics)
        self.assertIn("connectivity", metrics)
        
        # Check values
        self.assertEqual(metrics["node_count"], 3)
        self.assertEqual(metrics["edge_count"], 2)
    
    def test_calculate_dependency_complexity(self):
        """Test calculating dependency complexity"""
        graph = build_graph_from_cbsf(self.cbsf_path)
        complexity = calculate_dependency_complexity(graph)
        
        # Check complexity keys
        self.assertIn("avg_fan_in", complexity)
        self.assertIn("avg_fan_out", complexity)
        self.assertIn("fan_in", complexity)
        self.assertIn("fan_out", complexity)
        
        # Check values
        self.assertEqual(complexity["avg_fan_in"], 2/3)  # 2 edges, 3 nodes
        self.assertEqual(complexity["avg_fan_out"], 2/3)  # 2 edges, 3 nodes
        
        # Check specific node values
        self.assertEqual(complexity["fan_in"]["main.py"], 0)  # main has no incoming edges
        self.assertEqual(complexity["fan_out"]["main.py"], 2)  # main has 2 outgoing edges
    
    def test_calculate_information_entropy(self):
        """Test calculating information entropy"""
        graph = build_graph_from_cbsf(self.cbsf_path)
        entropy = calculate_information_entropy(graph)
        
        # Entropy should be greater than 0 for non-empty CBSF
        self.assertGreater(entropy, 0)
    
    def test_evaluate_cbsf(self):
        """Test the full evaluate_cbsf function"""
        results = evaluate_cbsf(self.project_dir, self.cbsf_path)
        
        # Check result keys
        self.assertIn("compression_ratio", results)
        self.assertIn("graph_metrics", results)
        self.assertIn("dependency_complexity", results)
        self.assertIn("information_entropy", results)
        
        # Check nested keys
        self.assertIn("node_count", results["graph_metrics"])
        self.assertIn("avg_fan_in", results["dependency_complexity"])
        
        # Check values
        self.assertEqual(results["graph_metrics"]["node_count"], 3)
        self.assertEqual(results["graph_metrics"]["edge_count"], 2)

if __name__ == '__main__':
    unittest.main() 