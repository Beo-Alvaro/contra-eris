from typing import List, Dict, Any

def generate_cbsf(summaries: List[Dict]) -> Dict:
    """Generate CBSF data structure with enhanced code analysis"""
    # Create the base structure
    cbsf = {
        "codebase_summary": summaries,
        "meta": {
            "file_count": len(summaries),
            "summary_stats": calculate_summary_stats(summaries)
        },
        "code_relationships": extract_code_relationships(summaries)
    }
    
    return cbsf

def calculate_summary_stats(summaries: List[Dict]) -> Dict[str, Any]:
    """Calculate general statistics about the codebase"""
    stats = {
        "function_count": 0,
        "class_count": 0,
        "import_count": 0,
        "by_extension": {}
    }
    
    for summary in summaries:
        # Count elements by file extension
        file_ext = summary.get("file", "").split(".")[-1].lower() if "." in summary.get("file", "") else "unknown"
        if file_ext not in stats["by_extension"]:
            stats["by_extension"][file_ext] = {"count": 0}
        stats["by_extension"][file_ext]["count"] += 1
        
        # Count code elements
        stats["function_count"] += len(summary.get("functions", []))
        stats["class_count"] += len(summary.get("classes", []))
        stats["import_count"] += len(summary.get("imports", []))
        
        # Track element counts per file type
        if "functions" in summary:
            if "functions" not in stats["by_extension"][file_ext]:
                stats["by_extension"][file_ext]["functions"] = 0
            stats["by_extension"][file_ext]["functions"] = len(summary.get("functions", []))
            
        if "classes" in summary:
            if "classes" not in stats["by_extension"][file_ext]:
                stats["by_extension"][file_ext]["classes"] = 0
            stats["by_extension"][file_ext]["classes"] = len(summary.get("classes", []))
            
        if "imports" in summary:
            if "imports" not in stats["by_extension"][file_ext]:
                stats["by_extension"][file_ext]["imports"] = 0
            stats["by_extension"][file_ext]["imports"] = len(summary.get("imports", []))
    
    return stats

def extract_code_relationships(summaries: List[Dict]) -> Dict[str, Any]:
    """Extract general code relationships from the parsed files"""
    relationships = {
        "function_calls": [],
        "inheritance": [],
        "imports": [],
        "component_relationships": []
    }
    
    # Function call relationships from any function data that includes called_functions
    for summary in summaries:
        source_file = summary.get("file", "")
        
        for function in summary.get("functions", []):
            if "called_functions" in function and function["called_functions"]:
                for called_func in function.get("called_functions", []):
                    relationships["function_calls"].append({
                        "caller": function.get("name", ""),
                        "callee": called_func,
                        "source_file": source_file
                    })
    
        # Extract inheritance relationships from classes
        for cls in summary.get("classes", []):
            if "inherits_from" in cls and cls["inherits_from"]:
                for parent in cls.get("inherits_from", []):
                    relationships["inheritance"].append({
                        "child": cls.get("name", ""),
                        "parent": parent,
                        "source_file": source_file
                    })
    
        # Extract import relationships
        for imported in summary.get("imports", []):
            relationships["imports"].append({
                "importer": source_file,
                "imported": imported
            })
            
        # Extract UI component relationships (for web technologies)
        if "elements" in summary:
            for element in summary.get("elements", []):
                if "id" in element and element["id"]:
                    # Check if this element is referenced in any script
                    for other_summary in summaries:
                        if "functions" in other_summary:
                            for function in other_summary.get("functions", []):
                                # Very basic check - just look for element ID in function code
                                # A more sophisticated approach would parse the AST
                                if function.get("code_snippet") and element["id"] in function.get("code_snippet", ""):
                                    relationships["component_relationships"].append({
                                        "element_id": element["id"],
                                        "element_file": source_file,
                                        "function": function.get("name", ""),
                                        "function_file": other_summary.get("file", "")
                                    })
    
    return relationships 