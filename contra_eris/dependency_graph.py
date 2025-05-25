from typing import List, Dict

def build_dependency_graph(summaries: List[Dict]) -> Dict:
    """Build dependency graph from file summaries"""
    graph = {"nodes": [], "edges": []}

    for summary in summaries:
        file_node = summary["file"]
        graph["nodes"].append(file_node)
        for imp in summary.get("imports", []):
            for target in summaries:
                if target["file"] != file_node and (imp in target["file"] or any(imp.endswith(f".{c['name']}") for c in target.get("classes", []))):
                    graph["edges"].append({"from": file_node, "to": target["file"]})

    return graph 