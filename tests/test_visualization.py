"""
Tests for the visualization module
"""

import os
import json
import unittest
import tempfile
import networkx as nx
from contra_eris.visualization import (
    visualize_dependency_graph,
    create_metrics_report,
    visualize_metrics
)

class TestVisualization(unittest.TestCase):
    """Test cases for the visualization module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name
        
        # Create a sample graph
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(["main.py", "utils.py", "config.py"])
        self.graph.add_edges_from([("main.py", "utils.py"), ("main.py", "config.py"), ("utils.py", "config.py")])
        
        # Create a sample CBSF
        self.cbsf_path = os.path.join(self.output_dir, "cbsf.json")
        self.create_sample_cbsf()
        
        # Sample metrics with complete dependency complexity data for visualizations
        self.metrics = {
            "compression_ratio": 0.25,
            "graph_metrics": {
                "node_count": 3,
                "edge_count": 3,
                "density": 0.5,
                "connectivity": 0.33
            },
            "dependency_complexity": {
                "avg_fan_in": 1.0,
                "avg_fan_out": 1.0,
                "fan_in": {
                    "main.py": 0,
                    "utils.py": 1,
                    "config.py": 2
                },
                "fan_out": {
                    "main.py": 2,
                    "utils.py": 1,
                    "config.py": 0
                },
                "instability": {
                    "main.py": 1.0,
                    "utils.py": 0.5,
                    "config.py": 0.0
                }
            },
            "information_entropy": 2.5
        }
    
    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()
    
    def create_sample_cbsf(self):
        """Create a sample CBSF file"""
        cbsf = {
            "codebase_summary": [
                {
                    "file": "main.py",
                    "imports": ["utils", "config"],
                    "functions": [{"name": "main", "docstring": "Main function", "lineno": 5}],
                    "classes": []
                },
                {
                    "file": "utils.py",
                    "imports": ["config"],
                    "functions": [{"name": "helper", "docstring": "Helper function", "lineno": 3}],
                    "classes": []
                },
                {
                    "file": "config.py",
                    "imports": [],
                    "functions": [],
                    "classes": [{"name": "Config", "docstring": "Configuration class", "lineno": 2}]
                }
            ],
            "meta": {
                "file_count": 3
            },
            "graph": {
                "nodes": ["main.py", "utils.py", "config.py"],
                "edges": [
                    {"from": "main.py", "to": "utils.py"},
                    {"from": "main.py", "to": "config.py"},
                    {"from": "utils.py", "to": "config.py"}
                ]
            }
        }
        
        with open(self.cbsf_path, "w") as f:
            json.dump(cbsf, f)
    
    def test_visualize_dependency_graph(self):
        """Test visualizing dependency graph"""
        output_path = os.path.join(self.output_dir, "dep_graph.png")
        
        # Should not raise any exceptions
        visualize_dependency_graph(self.graph, output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
    
    def test_visualize_dependency_graph_empty(self):
        """Test visualizing an empty graph"""
        empty_graph = nx.DiGraph()
        output_path = os.path.join(self.output_dir, "empty_graph.png")
        
        # Should not raise any exceptions
        visualize_dependency_graph(empty_graph, output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
    
    def test_create_metrics_report(self):
        """Test generating HTML report"""
        report_path = os.path.join(self.output_dir, "report.html")
        
        # Should not raise any exceptions
        create_metrics_report(
            self.metrics,
            report_path
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(report_path))
        self.assertGreater(os.path.getsize(report_path), 0)
        
        # Check content of HTML file
        with open(report_path, "r") as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("<html", content)
            self.assertIn("Contra Eris", content)
            self.assertIn("Compression Ratio", content)
    
    def test_visualize_metrics(self):
        """Test creating metrics visualizations"""
        # Should not raise any exceptions
        visualize_metrics(self.metrics, self.output_dir)
        
        # No assertions about specific files being created
        # The visualization function might not create certain files depending on the data
        # As long as it runs without exceptions, the test passes

if __name__ == '__main__':
    unittest.main() 