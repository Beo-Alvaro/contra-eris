import os
import json
import math
import networkx as nx
from typing import Dict, List, Tuple, Any

def calculate_compression_ratio(original_dir: str, cbsf_path: str) -> float:
    """Calculate compression ratio between original codebase and CBSF"""
    # Calculate original size
    original_size = 0
    for root, _, files in os.walk(original_dir):
        for file in files:
            file_path = os.path.join(root, file)
            original_size += os.path.getsize(file_path)
    
    # Calculate CBSF size
    cbsf_size = os.path.getsize(cbsf_path)
    
    # Return ratio (smaller is better)
    return cbsf_size / original_size if original_size > 0 else float('inf')

def build_graph_from_cbsf(cbsf_path: str) -> nx.DiGraph:
    """Create a NetworkX graph from CBSF data"""
    with open(cbsf_path, 'r') as f:
        cbsf_data = json.load(f)
    
    G = nx.DiGraph()
    
    # Add nodes from the graph data if available
    if "graph" in cbsf_data and "nodes" in cbsf_data["graph"]:
        for node in cbsf_data["graph"]["nodes"]:
            G.add_node(node)
        
        # Add edges
        if "edges" in cbsf_data["graph"]:
            for edge in cbsf_data["graph"]["edges"]:
                G.add_edge(edge["from"], edge["to"])
    
    # If no graph data, build from codebase_summary
    elif "codebase_summary" in cbsf_data:
        summaries = cbsf_data["codebase_summary"]
        for summary in summaries:
            G.add_node(summary["file"])
        
        # Try to add edges based on imports
        for summary in summaries:
            for imp in summary.get("imports", []):
                for target in summaries:
                    if target["file"] != summary["file"] and (
                        imp in target["file"] or 
                        any(imp.endswith(f".{c['name']}") for c in target.get("classes", []))
                    ):
                        G.add_edge(summary["file"], target["file"])
    
    return G

def calculate_graph_metrics(graph: nx.DiGraph) -> Dict:
    """Calculate various graph metrics for dependency analysis"""
    metrics = {}
    
    # Number of nodes and edges
    metrics["node_count"] = graph.number_of_nodes()
    metrics["edge_count"] = graph.number_of_edges()
    
    # Connectivity (edge density)
    if metrics["node_count"] > 1:
        max_edges = metrics["node_count"] * (metrics["node_count"] - 1)
        metrics["connectivity"] = metrics["edge_count"] / max_edges
    else:
        metrics["connectivity"] = 0
    
    # Centrality measures
    if metrics["node_count"] > 0:
        # In-degree and out-degree centrality
        metrics["in_degree_centrality"] = nx.in_degree_centrality(graph)
        metrics["out_degree_centrality"] = nx.out_degree_centrality(graph)
        
        # Try to calculate betweenness centrality (may fail if graph is not connected)
        try:
            metrics["betweenness_centrality"] = nx.betweenness_centrality(graph)
        except:
            metrics["betweenness_centrality"] = "Graph not connected enough for betweenness"
        
        # Try to calculate modularity with community detection
        try:
            # Convert to undirected for community detection
            undirected_graph = graph.to_undirected()
            communities = nx.community.greedy_modularity_communities(undirected_graph)
            metrics["modularity_communities"] = [list(c) for c in communities]
            metrics["community_count"] = len(communities)
        except Exception as e:
            metrics["modularity_communities"] = f"Failed to detect communities: {str(e)}"
    
    return metrics

def calculate_dependency_complexity(graph: nx.DiGraph) -> Dict:
    """Calculate dependency complexity metrics"""
    metrics = {}
    
    # Fan-in and fan-out for each node
    fan_in = {}
    fan_out = {}
    instability = {}
    
    for node in graph.nodes():
        in_degree = graph.in_degree(node)
        out_degree = graph.out_degree(node)
        
        fan_in[node] = in_degree
        fan_out[node] = out_degree
        
        # Calculate instability: I = fan-out / (fan-in + fan-out)
        total = in_degree + out_degree
        if total > 0:
            instability[node] = out_degree / total
        else:
            instability[node] = 0
    
    metrics["fan_in"] = fan_in
    metrics["fan_out"] = fan_out
    metrics["instability"] = instability
    
    # Average metrics
    if len(graph.nodes()) > 0:
        metrics["avg_fan_in"] = sum(fan_in.values()) / len(graph.nodes())
        metrics["avg_fan_out"] = sum(fan_out.values()) / len(graph.nodes())
        metrics["avg_instability"] = sum(instability.values()) / len(graph.nodes())
    
    return metrics

def calculate_information_entropy(graph: nx.DiGraph) -> float:
    """Calculate information entropy of the dependency distribution"""
    if graph.number_of_nodes() == 0:
        return 0
    
    # Get degree distribution
    degrees = [d for _, d in graph.degree()]
    total_degrees = sum(degrees)
    
    if total_degrees == 0:
        return 0
    
    # Calculate probabilities
    probabilities = [d / total_degrees for d in degrees if d > 0]
    
    if not probabilities:
        return 0
    
    # Calculate entropy: H(X) = -∑p(x)log₂p(x)
    entropy = -sum(p * math.log2(p) for p in probabilities)
    
    return entropy

def evaluate_cbsf(project_dir: str, cbsf_path: str) -> Dict[str, Any]:
    """Evaluate a CBSF file with multiple metrics"""
    results = {}
    
    print("Calculating compression ratio...")
    # Calculate compression ratio
    results["compression_ratio"] = calculate_compression_ratio(project_dir, cbsf_path)
    
    print("Building graph from CBSF...")
    # Build graph from CBSF
    graph = build_graph_from_cbsf(cbsf_path)
    
    print("Calculating graph metrics...")
    # Calculate graph metrics
    results["graph_metrics"] = calculate_graph_metrics(graph)
    
    print("Calculating dependency complexity...")
    # Calculate dependency complexity
    results["dependency_complexity"] = calculate_dependency_complexity(graph)
    
    print("Calculating information entropy...")
    # Calculate information entropy
    results["information_entropy"] = calculate_information_entropy(graph)
    
    return results

def evaluate_with_visualization(project_dir: str, cbsf_path: str, output_dir: str = "output") -> Dict[str, Any]:
    """Evaluate CBSF and generate visualizations"""
    from contra_eris.visualization import visualize_dependency_graph, visualize_metrics, create_metrics_report
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run evaluation
    results = evaluate_cbsf(project_dir, cbsf_path)
    
    # Build graph
    graph = build_graph_from_cbsf(cbsf_path)
    
    # Create visualizations
    print("Generating visualizations...")
    visualize_dependency_graph(graph, os.path.join(output_dir, "dependency_graph.png"))
    visualize_metrics(results, output_dir)
    
    # Create HTML report
    print("Generating HTML report...")
    create_metrics_report(results, os.path.join(output_dir, "report.html"))
    
    return results 