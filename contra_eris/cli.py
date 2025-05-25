"""
Contra Eris CLI - Command Line Interface
Provides command line tools for both CBSF generation and evaluation
"""

import argparse
import os
import json
import sys
from typing import Dict, Any, Optional

from contra_eris.core import analyze_project
from contra_eris.evaluation import evaluate_cbsf, evaluate_with_visualization

def generate_command(args) -> Dict[str, Any]:
    """Run the CBSF generation command"""
    # Handle extensions as a list
    extensions = set(args.extensions)
    
    return analyze_project(
        project_path=args.project,
        output_dir=args.output,
        extensions=extensions,
        verbose=not args.quiet
    )

def evaluate_command(args) -> Dict[str, Any]:
    """Run the evaluation command"""
    # Check if CBSF file exists
    if not os.path.exists(args.cbsf):
        if not args.quiet:
            print(f"Error: CBSF file not found at {args.cbsf}")
        return {"error": "CBSF file not found"}
    
    # Choose evaluation function based on visualization flag
    if args.visualize:
        results = evaluate_with_visualization(
            project_dir=args.project,
            cbsf_path=args.cbsf,
            output_dir=args.output
        )
    else:
        results = evaluate_cbsf(args.project, args.cbsf)
    
    # Save results to file if output specified
    if args.metrics_file:
        os.makedirs(os.path.dirname(args.metrics_file), exist_ok=True)
        with open(args.metrics_file, 'w') as f:
            # Convert non-serializable objects to strings
            serializable_results = json.loads(json.dumps(results, default=str))
            json.dump(serializable_results, f, indent=2)
        
        if not args.quiet:
            print(f"Evaluation results saved to {args.metrics_file}")
    
    # Print key metrics if not quiet
    if not args.quiet:
        print("\nKey Metrics:")
        if "compression_ratio" in results:
            print(f"Compression Ratio: {results['compression_ratio']:.4f}")
        
        if "graph_metrics" in results:
            gm = results["graph_metrics"]
            print(f"Node Count: {gm.get('node_count', 'N/A')}")
            print(f"Edge Count: {gm.get('edge_count', 'N/A')}")
            print(f"Connectivity: {gm.get('connectivity', 'N/A'):.4f}")
        
        if "information_entropy" in results:
            print(f"Information Entropy: {results['information_entropy']:.4f}")
        
        # Print average fan-in/fan-out if available
        if "dependency_complexity" in results:
            dc = results["dependency_complexity"]
            if "avg_fan_in" in dc:
                print(f"Avg Fan-in: {dc['avg_fan_in']:.2f}")
            if "avg_fan_out" in dc:
                print(f"Avg Fan-out: {dc['avg_fan_out']:.2f}")
            if "avg_instability" in dc:
                print(f"Avg Instability: {dc['avg_instability']:.2f}")
    
    return results

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Contra Eris - Codebase Analysis and Evaluation System"
    )
    
    # For clarity, separate the commands from other args
    parser.add_argument("--project", default=".", 
                      help="Project directory to analyze (default: current directory)")
    parser.add_argument("--output", default="output", 
                      help="Output directory for results (default: output)")
    parser.add_argument("--extensions", nargs="+", default=[".py"], 
                      help="File extensions to include (default: .py)")
    parser.add_argument("--quiet", action="store_true", 
                      help="Suppress output messages")
    parser.add_argument("--verbose", action="store_true",
                      help="Show verbose output")
    
    args = parser.parse_args()
    
    # Set verbose flag based on quiet/verbose settings
    verbose = args.verbose and not args.quiet
    
    # Run the generate command
    result = analyze_project(
        project_path=args.project,
        output_dir=args.output,
        extensions=set(args.extensions),
        verbose=verbose
    )
    
    return 0

def generate_main():
    """Entry point for the generate command"""
    return main()

if __name__ == "__main__":
    sys.exit(main()) 