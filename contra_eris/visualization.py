"""
Visualization module for Contra Eris
Provides functions to visualize dependency graphs and metrics
"""

import os
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import Dict

def visualize_dependency_graph(graph: nx.DiGraph, output_path: str = "output/dependency_graph.png"):
    """Visualize the dependency graph"""
    plt.figure(figsize=(12, 10))
    
    if graph.number_of_nodes() == 0:
        plt.text(0.5, 0.5, "No nodes in graph", ha='center', va='center', fontsize=14)
        plt.axis('off')
        plt.savefig(output_path)
        plt.close()
        return
    
    # Calculate node size based on degree
    node_size = [300 * (1 + graph.degree(n)) for n in graph.nodes()]
    
    # Calculate edge weights
    edge_width = [0.5 for _ in graph.edges()]
    
    # Use spring layout for node positioning
    pos = nx.spring_layout(graph, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, alpha=0.7)
    
    # Draw edges
    nx.draw_networkx_edges(graph, pos, width=edge_width, alpha=0.5, arrows=True)
    
    # Draw labels
    nx.draw_networkx_labels(graph, pos, font_size=8)
    
    plt.title("Codebase Dependency Graph")
    plt.axis("off")
    
    # Save figure
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Dependency graph visualization saved to {output_path}")

def visualize_metrics(metrics: Dict, output_dir: str = "output"):
    """Create visualizations for various metrics"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Dependency Complexity - Fan-in/Fan-out
    if "dependency_complexity" in metrics:
        dc = metrics["dependency_complexity"]
        if "fan_in" in dc and "fan_out" in dc and dc["fan_in"] and dc["fan_out"]:
            fan_in = dc["fan_in"]
            fan_out = dc["fan_out"]
            
            # Get nodes sorted by fan-in
            sorted_nodes = sorted(fan_in.keys(), key=lambda n: fan_in[n], reverse=True)
            top_nodes = sorted_nodes[:min(10, len(sorted_nodes))]
            
            plt.figure(figsize=(12, 6))
            
            # Plot Fan-in and Fan-out for top nodes
            x = np.arange(len(top_nodes))
            width = 0.35
            
            in_values = [fan_in[n] for n in top_nodes]
            out_values = [fan_out[n] for n in top_nodes]
            
            plt.bar(x - width/2, in_values, width, label='Fan-in')
            plt.bar(x + width/2, out_values, width, label='Fan-out')
            
            plt.xlabel('Nodes')
            plt.ylabel('Count')
            plt.title('Fan-in/Fan-out for Top 10 Nodes')
            plt.xticks(x, [os.path.basename(n) for n in top_nodes], rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            fan_in_out_path = os.path.join(output_dir, "fan_in_out.png")
            plt.savefig(fan_in_out_path)
            plt.close()
            
            print(f"Fan-in/Fan-out visualization saved to {fan_in_out_path}")
    
    # Instability Distribution
    if "dependency_complexity" in metrics and "instability" in metrics["dependency_complexity"]:
        instability = metrics["dependency_complexity"]["instability"]
        
        if instability and len(instability) > 0:
            plt.figure(figsize=(10, 6))
            
            # Create histogram of instability values
            plt.hist(list(instability.values()), bins=10, alpha=0.7)
            
            plt.xlabel('Instability (I)')
            plt.ylabel('Number of Components')
            plt.title('Distribution of Component Instability')
            plt.grid(alpha=0.3)
            
            instability_path = os.path.join(output_dir, "instability.png")
            plt.savefig(instability_path)
            plt.close()
            
            print(f"Instability distribution saved to {instability_path}")

def create_metrics_report(metrics: Dict, output_path: str = "output/report.html"):
    """Create an HTML report of the metrics"""
    # Create HTML content
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contra Eris Metrics Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .metric-value { font-weight: bold; }
            .visualization { margin: 20px 0; text-align: center; }
            .visualization img { max-width: 100%; }
        </style>
    </head>
    <body>
        <h1>Contra Eris Metrics Report</h1>
    """
    
    # Compression Ratio
    html += f"""
        <h2>Compression Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Compression Ratio</td><td class="metric-value">{metrics.get('compression_ratio', 'N/A'):.4f}</td></tr>
        </table>
    """
    
    # Graph Metrics
    if "graph_metrics" in metrics:
        gm = metrics["graph_metrics"]
        html += f"""
            <h2>Graph Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Node Count</td><td class="metric-value">{gm.get('node_count', 'N/A')}</td></tr>
                <tr><td>Edge Count</td><td class="metric-value">{gm.get('edge_count', 'N/A')}</td></tr>
                <tr><td>Connectivity</td><td class="metric-value">{gm.get('connectivity', 'N/A'):.4f}</td></tr>
                <tr><td>Community Count</td><td class="metric-value">{gm.get('community_count', 'N/A') if 'community_count' in gm else 'N/A'}</td></tr>
            </table>
        """
    
    # Dependency Complexity
    if "dependency_complexity" in metrics:
        dc = metrics["dependency_complexity"]
        html += f"""
            <h2>Dependency Complexity</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Average Fan-in</td><td class="metric-value">{dc.get('avg_fan_in', 'N/A')}</td></tr>
                <tr><td>Average Fan-out</td><td class="metric-value">{dc.get('avg_fan_out', 'N/A')}</td></tr>
                <tr><td>Average Instability</td><td class="metric-value">{dc.get('avg_instability', 'N/A')}</td></tr>
            </table>
        """
    
    # Information Entropy
    html += f"""
        <h2>Information Theory Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Information Entropy</td><td class="metric-value">{metrics.get('information_entropy', 'N/A'):.4f}</td></tr>
        </table>
    """
    
    # Visualizations
    html += """
        <h2>Visualizations</h2>
        <div class="visualization">
            <h3>Dependency Graph</h3>
            <img src="dependency_graph.png" alt="Dependency Graph" />
        </div>
        <div class="visualization">
            <h3>Fan-in/Fan-out Distribution</h3>
            <img src="fan_in_out.png" alt="Fan-in/Fan-out Distribution" />
        </div>
        <div class="visualization">
            <h3>Instability Distribution</h3>
            <img src="instability.png" alt="Instability Distribution" />
        </div>
    """
    
    html += """
    </body>
    </html>
    """
    
    # Write HTML to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"HTML report generated at {output_path}") 