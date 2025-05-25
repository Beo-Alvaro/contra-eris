"""
Contra Eris Core - Main functionality
Core functions for analyzing projects and generating CBSF
"""

import os
import json
import pathlib
from typing import Dict, List, Set, Any, Optional

from contra_eris.crawler import crawl_project
from contra_eris.parsers import get_parser_for_extension
from contra_eris.summarizers import get_summarizer_for_extension
from contra_eris.dependency_graph import build_dependency_graph
from contra_eris.cbsf_generator import generate_cbsf

def analyze_project(
    project_path: str, 
    output_dir: str = "output", 
    extensions: Set[str] = {".py"},
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Analyze a project directory and generate CBSF files
    
    Args:
        project_path: Path to the project directory
        output_dir: Directory to save output files
        extensions: File extensions to include in analysis
        verbose: Whether to print progress messages
    
    Returns:
        Dictionary containing analysis results
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output paths
    cbsf_path = os.path.join(output_dir, "cbsf.json")
    graph_path = os.path.join(output_dir, "graph.json")
    
    if verbose:
        print(f"Analyzing project: {project_path}")
    
    # Step 1: Find all relevant files
    files = crawl_project(project_path, extensions)
    
    if verbose:
        print(f"Found {len(files)} files")
    
    if not files:
        if verbose:
            print(f"No files with extensions {extensions} found in {project_path}")
        return {"error": "No files found"}
    
    # Step 2: Process each file
    all_data = []
    error_count = 0
    unsupported_count = 0
    
    for file in files:
        try:
            # Get file extension
            file_ext = pathlib.Path(file).suffix.lower()
            
            # Skip if no parser is available for this extension
            try:
                parser = get_parser_for_extension(file_ext)
                summarizer = get_summarizer_for_extension(file_ext)
            except ValueError:
                if verbose:
                    print(f"  ⚠ No parser available for {file_ext} file: {file}")
                unsupported_count += 1
                continue
                
            # Parse and summarize the file
            parsed = parser(file)
            summary = summarizer(parsed, file)
            all_data.append(summary)
            
            if verbose:
                print(f"  ✓ Processed {file}")
                
        except Exception as e:
            error_count += 1
            if verbose:
                print(f"  ✗ Error processing {file}: {str(e)}")
    
    if verbose:
        print(f"Successfully processed {len(all_data)} files with {error_count} errors and {unsupported_count} unsupported files")
    
    # Step 3: Generate CBSF
    cbsf_data = generate_cbsf(all_data)
    
    # Step 4: Generate Graph
    graph_data = build_dependency_graph(all_data)
    
    # Add graph to CBSF
    cbsf_data["graph"] = graph_data
    
    # Save output files
    with open(cbsf_path, "w", encoding="utf-8") as f:
        json.dump(cbsf_data, f, indent=2)
        if verbose:
            print(f"CBSF saved to {cbsf_path}")
    
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)
        if verbose:
            print(f"Graph data saved to {graph_path}")
    
    return {
        "cbsf": cbsf_data,
        "graph": graph_data,
        "file_count": len(files),
        "processed_count": len(all_data),
        "error_count": error_count,
        "unsupported_count": unsupported_count,
        "output_files": {
            "cbsf": cbsf_path,
            "graph": graph_path
        }
    } 