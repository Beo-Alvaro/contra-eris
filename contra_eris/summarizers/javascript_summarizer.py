"""
JavaScript AST summarizer for Contra Eris
"""

from typing import Dict, Any, List

def summarize_javascript_ast(tree: Any, filename: str) -> Dict:
    """Extract summary information from JavaScript AST"""
    summary = {
        "file": filename, 
        "functions": [], 
        "classes": [], 
        "imports": [],
        "variables": [],
        "event_handlers": [],
        "code_snippets": {}
    }
    
    # Process the esprima-generated AST
    if hasattr(tree, 'body'):
        for node in tree.body:
            process_js_node(node, summary)
        
        # After initial processing, analyze function calls and relationships
        extract_function_call_graph(summary)
        detect_event_handlers(summary)
        extract_data_structure_contents(tree, summary)
            
    return summary

def process_js_node(node, summary, parent=None):
    """Process a JavaScript AST node to extract relevant information"""
    # Extract function declarations
    if node.type == 'FunctionDeclaration':
        func_info = {
            "name": node.id.name if hasattr(node, 'id') and node.id else 'anonymous',
            "docstring": extract_js_docstring(node),
            "lineno": node.loc.start.line if hasattr(node, 'loc') else 0,
            "params": extract_function_params(node),
            "implementation": extract_implementation_summary(node),
            "code": extract_node_code(node),
            "called_functions": []
        }
        summary["functions"].append(func_info)
        
        # Store code snippet for reference
        if hasattr(node, 'loc') and hasattr(node.loc, 'start') and hasattr(node.loc, 'end'):
            summary["code_snippets"][func_info["name"]] = {
                "start": node.loc.start.line,
                "end": node.loc.end.line,
                "code": func_info["code"]
            }
    
    # Extract class declarations
    elif node.type == 'ClassDeclaration':
        summary["classes"].append({
            "name": node.id.name if hasattr(node, 'id') and node.id else 'anonymous',
            "docstring": extract_js_docstring(node),
            "lineno": node.loc.start.line if hasattr(node, 'loc') else 0
        })
    
    # Extract ES6 imports
    elif node.type == 'ImportDeclaration':
        if hasattr(node, 'source') and hasattr(node.source, 'value'):
            module_name = node.source.value
            if hasattr(node, 'specifiers'):
                for specifier in node.specifiers:
                    if hasattr(specifier, 'imported') and hasattr(specifier.imported, 'name'):
                        summary["imports"].append(f"{module_name}.{specifier.imported.name}")
                    elif hasattr(specifier, 'local') and hasattr(specifier.local, 'name'):
                        summary["imports"].append(module_name)
            else:
                summary["imports"].append(module_name)
    
    # Extract variable declarations
    elif (node.type == 'VariableDeclaration' and hasattr(node, 'declarations')):
        for decl in node.declarations:
            # Add variable to the summary
            if hasattr(decl, 'id') and hasattr(decl.id, 'name'):
                var_info = {
                    "name": decl.id.name,
                    "kind": node.kind if hasattr(node, 'kind') else 'var',
                    "lineno": node.loc.start.line if hasattr(node, 'loc') else 0,
                    "code": extract_node_code(node)
                }
                
                # Add initial value type if available
                if hasattr(decl, 'init') and decl.init:
                    if hasattr(decl.init, 'type'):
                        var_info["value_type"] = decl.init.type
                        
                        # For arrays, add length and content information
                        if decl.init.type == 'ArrayExpression' and hasattr(decl.init, 'elements'):
                            var_info["is_array"] = True
                            var_info["array_length"] = len(decl.init.elements)
                            var_info["contents"] = extract_array_contents(decl.init)
                            
                        # For object expressions, add property count and contents
                        elif decl.init.type == 'ObjectExpression' and hasattr(decl.init, 'properties'):
                            var_info["is_object"] = True
                            var_info["property_count"] = len(decl.init.properties)
                            var_info["contents"] = extract_object_contents(decl.init)
                
                summary["variables"].append(var_info)
            
            # Check for require calls
            if (hasattr(decl, 'init') and decl.init and 
                hasattr(decl.init, 'callee') and decl.init.callee and
                hasattr(decl.init.callee, 'name') and decl.init.callee.name == 'require'):
                
                if (hasattr(decl.init, 'arguments') and decl.init.arguments and 
                    hasattr(decl.init.arguments[0], 'value')):
                    module_name = decl.init.arguments[0].value
                    summary["imports"].append(module_name)
            
            # Check for function expressions
            if (hasattr(decl, 'init') and decl.init and 
                hasattr(decl.init, 'type') and 
                (decl.init.type == 'FunctionExpression' or decl.init.type == 'ArrowFunctionExpression')):
                
                if hasattr(decl, 'id') and hasattr(decl.id, 'name'):
                    func_info = {
                        "name": decl.id.name,
                        "docstring": extract_js_docstring(decl.init),
                        "lineno": decl.loc.start.line if hasattr(decl, 'loc') else 0,
                        "params": extract_function_params(decl.init),
                        "is_arrow": decl.init.type == 'ArrowFunctionExpression',
                        "implementation": extract_implementation_summary(decl.init),
                        "code": extract_node_code(node),
                        "called_functions": []
                    }
                    summary["functions"].append(func_info)
                    
                    # Store code snippet
                    if hasattr(node, 'loc') and hasattr(node.loc, 'start') and hasattr(node.loc, 'end'):
                        summary["code_snippets"][func_info["name"]] = {
                            "start": node.loc.start.line,
                            "end": node.loc.end.line,
                            "code": func_info["code"]
                        }
    
    # Extract global variable assignments
    elif node.type == 'ExpressionStatement' and hasattr(node, 'expression'):
        if (hasattr(node.expression, 'type') and 
            node.expression.type == 'AssignmentExpression' and
            hasattr(node.expression, 'left') and
            hasattr(node.expression.left, 'name')):
            
            var_name = node.expression.left.name
            # Only add if not already in variables
            if not any(v["name"] == var_name for v in summary["variables"]):
                var_info = {
                    "name": var_name,
                    "kind": "assignment",
                    "lineno": node.loc.start.line if hasattr(node, 'loc') else 0,
                    "code": extract_node_code(node)
                }
                
                # Add value type if available
                if (hasattr(node.expression, 'right') and 
                    hasattr(node.expression.right, 'type')):
                    var_info["value_type"] = node.expression.right.type
                
                summary["variables"].append(var_info)
        
        # Check for event listener registrations
        if detect_event_listener(node):
            event_info = extract_event_listener_info(node)
            if event_info:
                summary["event_handlers"].append(event_info)
        
        # Continue processing expression
        process_js_node(node.expression, summary, node)
    
    # Recursively process blocks
    elif node.type == 'BlockStatement' and hasattr(node, 'body'):
        for stmt in node.body:
            process_js_node(stmt, summary, node)
    elif hasattr(node, 'body') and isinstance(node.body, list):
        for stmt in node.body:
            process_js_node(stmt, summary, node)
    elif hasattr(node, 'body') and hasattr(node.body, 'type'):
        process_js_node(node.body, summary, node)

def extract_array_contents(array_node):
    """Extract contents from an array expression"""
    contents = []
    if hasattr(array_node, 'elements'):
        for element in array_node.elements:
            if not element:
                contents.append(None)
                continue
                
            if element.type == 'Literal' and hasattr(element, 'value'):
                contents.append(element.value)
            elif element.type == 'Identifier' and hasattr(element, 'name'):
                contents.append(element.name)
            elif element.type == 'ObjectExpression':
                contents.append(extract_object_contents(element))
            elif element.type == 'ArrayExpression':
                contents.append(extract_array_contents(element))
            else:
                contents.append(f"<{element.type}>")
                
    return contents[:10]  # Limit to first 10 items for brevity

def extract_object_contents(obj_node):
    """Extract contents from an object expression"""
    contents = {}
    if hasattr(obj_node, 'properties'):
        for prop in obj_node.properties:
            key = None
            value = None
            
            # Get property key
            if hasattr(prop, 'key'):
                if hasattr(prop.key, 'name'):
                    key = prop.key.name
                elif hasattr(prop.key, 'value'):
                    key = str(prop.key.value)
            
            # Get property value
            if hasattr(prop, 'value'):
                if prop.value.type == 'Literal' and hasattr(prop.value, 'value'):
                    value = prop.value.value
                elif prop.value.type == 'Identifier' and hasattr(prop.value, 'name'):
                    value = prop.value.name
                elif prop.value.type == 'ObjectExpression':
                    value = extract_object_contents(prop.value)
                elif prop.value.type == 'ArrayExpression':
                    value = extract_array_contents(prop.value)
                elif prop.value.type in ['FunctionExpression', 'ArrowFunctionExpression']:
                    value = f"<Function>"
                else:
                    value = f"<{prop.value.type}>"
            
            if key:
                contents[key] = value
                
    return contents

def extract_implementation_summary(node):
    """Extract a summary of the function implementation"""
    implementation = {
        "has_conditionals": False,
        "has_loops": False,
        "has_try_catch": False,
        "has_dom_operations": False,
        "called_functions": []
    }
    
    # Function to walk through the AST and identify key implementation details
    def walk_node(node):
        if not node:
            return
            
        # Check node type
        if hasattr(node, 'type'):
            # Detect conditionals
            if node.type in ['IfStatement', 'SwitchStatement', 'ConditionalExpression']:
                implementation["has_conditionals"] = True
                
            # Detect loops
            elif node.type in ['ForStatement', 'WhileStatement', 'DoWhileStatement', 'ForInStatement', 'ForOfStatement']:
                implementation["has_loops"] = True
                
            # Detect try-catch blocks
            elif node.type == 'TryStatement':
                implementation["has_try_catch"] = True
                
            # Detect DOM operations
            elif node.type == 'CallExpression' and hasattr(node, 'callee'):
                if hasattr(node.callee, 'object') and hasattr(node.callee.object, 'name'):
                    # Check for common DOM manipulation objects
                    if node.callee.object.name in ['document', 'window', 'element', 'node']:
                        implementation["has_dom_operations"] = True
                
                # Collect function calls
                if hasattr(node.callee, 'name'):
                    func_name = node.callee.name
                    if func_name and func_name not in implementation["called_functions"]:
                        implementation["called_functions"].append(func_name)
                elif hasattr(node.callee, 'property') and hasattr(node.callee.property, 'name'):
                    # For method calls like obj.method()
                    if hasattr(node.callee, 'object') and hasattr(node.callee.object, 'name'):
                        func_name = f"{node.callee.object.name}.{node.callee.property.name}"
                        if func_name not in implementation["called_functions"]:
                            implementation["called_functions"].append(func_name)
        
        # Recursively walk through properties
        if hasattr(node, 'body'):
            if isinstance(node.body, list):
                for item in node.body:
                    walk_node(item)
            else:
                walk_node(node.body)
                
        if hasattr(node, 'consequent'):
            walk_node(node.consequent)
            
        if hasattr(node, 'alternate'):
            walk_node(node.alternate)
            
        if hasattr(node, 'cases') and isinstance(node.cases, list):
            for case in node.cases:
                if hasattr(case, 'consequent'):
                    for item in case.consequent:
                        walk_node(item)
    
    # Start walking from function body
    if hasattr(node, 'body'):
        walk_node(node.body)
        
    return implementation

def extract_function_call_graph(summary):
    """Extract function call relationships"""
    function_map = {func["name"]: func for func in summary["functions"]}
    
    for func in summary["functions"]:
        # Extract function calls from code snippets
        for other_func_name in function_map.keys():
            # Basic pattern matching for function calls
            if other_func_name != func["name"] and f"{other_func_name}(" in func.get("code", ""):
                if other_func_name not in func["called_functions"]:
                    func["called_functions"].append(other_func_name)
        
        # Extract function calls from implementation analysis
        for called_func in func.get("implementation", {}).get("called_functions", []):
            if called_func in function_map and called_func not in func["called_functions"]:
                func["called_functions"].append(called_func)

def detect_event_handlers(summary):
    """Identify event handlers in the code"""
    # Look for function calls to addEventListener or onclick assignments
    function_map = {func["name"]: func for func in summary["functions"]}
    
    # Check variables that might be DOM elements
    dom_elements = []
    for variable in summary["variables"]:
        if "code" in variable and "document.getElementById" in variable["code"]:
            dom_elements.append(variable["name"])
    
    # Check all code snippets for event listener patterns
    for func_name, snippet in summary.get("code_snippets", {}).items():
        code = snippet.get("code", "")
        
        # Look for addEventListener calls
        for element in dom_elements:
            if f"{element}.addEventListener" in code:
                event_info = {
                    "element": element,
                    "type": "addEventListener",
                    "handler": None,
                    "event": None
                }
                
                # Simple pattern matching - not perfect but gives a general idea
                if "click" in code:
                    event_info["event"] = "click"
                elif "change" in code:
                    event_info["event"] = "change"
                elif "submit" in code:
                    event_info["event"] = "submit"
                elif "keydown" in code or "keypress" in code:
                    event_info["event"] = "key"
                
                # Look for handler in the same line
                for function_name in function_map.keys():
                    if function_name in code and "addEventListener" in code and function_name in code:
                        event_info["handler"] = function_name
                        break
                
                if event_info["handler"] or event_info["event"]:
                    summary["event_handlers"].append(event_info)
            
            # Look for onclick style assignments
            elif f"{element}.onclick" in code:
                event_info = {
                    "element": element,
                    "type": "property",
                    "handler": None,
                    "event": "click"
                }
                
                # Look for function assignment
                for function_name in function_map.keys():
                    if function_name in code and "onclick" in code and function_name in code:
                        event_info["handler"] = function_name
                        break
                
                if event_info["handler"]:
                    summary["event_handlers"].append(event_info)

def detect_event_listener(node):
    """Detect if a node is an event listener registration"""
    if (node.type == 'ExpressionStatement' and 
        hasattr(node, 'expression') and 
        hasattr(node.expression, 'type') and
        node.expression.type == 'CallExpression'):
        
        # Check for element.addEventListener pattern
        if (hasattr(node.expression, 'callee') and 
            hasattr(node.expression.callee, 'type') and
            node.expression.callee.type == 'MemberExpression'):
            
            if (hasattr(node.expression.callee, 'property') and
                hasattr(node.expression.callee.property, 'name') and
                node.expression.callee.property.name == 'addEventListener'):
                return True
    
    # Check for element.onclick = function pattern
    if (node.type == 'ExpressionStatement' and 
        hasattr(node, 'expression') and 
        hasattr(node.expression, 'type') and
        node.expression.type == 'AssignmentExpression'):
        
        if (hasattr(node.expression, 'left') and 
            hasattr(node.expression.left, 'type') and
            node.expression.left.type == 'MemberExpression'):
            
            if (hasattr(node.expression.left, 'property') and 
                hasattr(node.expression.left.property, 'name') and
                node.expression.left.property.name.startswith('on')):
                return True
    
    return False

def extract_event_listener_info(node):
    """Extract information from an event listener node"""
    event_info = {
        "element": None,
        "event": None,
        "handler": None,
        "type": None,
        "lineno": node.loc.start.line if hasattr(node, 'loc') and hasattr(node.loc, 'start') else 0
    }
    
    # Handle addEventListener pattern
    if (hasattr(node, 'expression') and 
        hasattr(node.expression, 'type') and
        node.expression.type == 'CallExpression'):
        
        if (hasattr(node.expression, 'callee') and 
            hasattr(node.expression.callee, 'type') and
            node.expression.callee.type == 'MemberExpression'):
            
            # Get element name
            if (hasattr(node.expression.callee, 'object') and 
                hasattr(node.expression.callee.object, 'name')):
                event_info["element"] = node.expression.callee.object.name
            
            # Check if it's an addEventListener call
            if (hasattr(node.expression.callee, 'property') and
                hasattr(node.expression.callee.property, 'name') and
                node.expression.callee.property.name == 'addEventListener'):
                
                event_info["type"] = "addEventListener"
                
                # Get event type (first argument)
                if (hasattr(node.expression, 'arguments') and 
                    len(node.expression.arguments) >= 1 and
                    hasattr(node.expression.arguments[0], 'value')):
                    event_info["event"] = node.expression.arguments[0].value
                
                # Get handler (second argument)
                if (len(node.expression.arguments) >= 2):
                    # Function expression directly
                    if node.expression.arguments[1].type in ['FunctionExpression', 'ArrowFunctionExpression']:
                        event_info["handler"] = "anonymous"
                    # Named function reference
                    elif node.expression.arguments[1].type == 'Identifier':
                        event_info["handler"] = node.expression.arguments[1].name
    
    # Handle onclick style assignments
    if (hasattr(node, 'expression') and 
        hasattr(node.expression, 'type') and
        node.expression.type == 'AssignmentExpression'):
        
        if (hasattr(node.expression, 'left') and 
            hasattr(node.expression.left, 'type') and
            node.expression.left.type == 'MemberExpression'):
            
            # Get element name
            if (hasattr(node.expression.left, 'object') and 
                hasattr(node.expression.left.object, 'name')):
                event_info["element"] = node.expression.left.object.name
            
            # Get event type from property name (onclick -> click)
            if (hasattr(node.expression.left, 'property') and 
                hasattr(node.expression.left.property, 'name')):
                prop_name = node.expression.left.property.name
                if prop_name.startswith('on'):
                    event_info["event"] = prop_name[2:]  # Remove 'on' prefix
                    event_info["type"] = "property"
            
            # Get handler from right side
            if (hasattr(node.expression, 'right')):
                # Function expression directly
                if node.expression.right.type in ['FunctionExpression', 'ArrowFunctionExpression']:
                    event_info["handler"] = "anonymous"
                # Named function reference
                elif node.expression.right.type == 'Identifier':
                    event_info["handler"] = node.expression.right.name
    
    # Only return if we have meaningful information
    if event_info["element"] or event_info["event"] or event_info["handler"]:
        return event_info
    return None

def extract_data_structure_contents(tree, summary):
    """Extract and attach actual contents of important data structures"""
    # Find important variables by name
    important_vars = ["questions", "rules", "penalties", "haroldPersonality"]
    
    # Update variables with more detailed content
    for var in summary["variables"]:
        if var["name"] in important_vars:
            # The contents are already extracted in the variable processing
            if "contents" not in var:
                # For any that were missed, try to extract them directly
                code = var.get("code", "")
                if code and var.get("is_array") or var.get("is_object"):
                    var["description"] = f"Contains {var.get('property_count', var.get('array_length', 0))} items"
                    
    # Add function implementations as code snippets
    for func in summary["functions"]:
        if func["name"] in ["evaluateRules", "displayQuestion", "displayResult"]:
            # These important functions should have their full code available
            if "code" in func:
                func["implementation"]["full_code"] = func["code"]

def extract_node_code(node):
    """Extract the code represented by a node (simplified version)"""
    if not node:
        return ""
        
    # This is a simplified version - in a real implementation we would use 
    # source maps or the original source code with the node's location info
    if node.type == 'FunctionDeclaration':
        params = ", ".join(extract_function_params(node))
        return f"function {node.id.name if hasattr(node, 'id') and node.id else 'anonymous'}({params}) { ... }"
    
    elif node.type == 'VariableDeclaration':
        if hasattr(node, 'declarations') and len(node.declarations) > 0:
            decl = node.declarations[0]
            if hasattr(decl, 'id') and hasattr(decl.id, 'name'):
                var_name = decl.id.name
                var_type = node.kind if hasattr(node, 'kind') else 'var'
                
                if hasattr(decl, 'init') and decl.init:
                    if decl.init.type == 'ObjectExpression':
                        return f"{var_type} {var_name} = {{ ... }}"
                    elif decl.init.type == 'ArrayExpression':
                        return f"{var_type} {var_name} = [ ... ]"
                    elif decl.init.type == 'FunctionExpression':
                        return f"{var_type} {var_name} = function(...) {{ ... }}"
                    elif decl.init.type == 'ArrowFunctionExpression':
                        return f"{var_type} {var_name} = (...) => {{ ... }}"
                    else:
                        return f"{var_type} {var_name} = ..."
                else:
                    return f"{var_type} {var_name}"
    
    # Simple representation for other node types
    return f"<{node.type}>"

def extract_js_docstring(node):
    """Extract docstring comment from a JS node if present"""
    # Check for leading comments
    if hasattr(node, 'leadingComments') and node.leadingComments:
        for comment in node.leadingComments:
            if comment.type == 'Block':
                return comment.value.strip()
    return None

def extract_function_params(node):
    """Extract function parameters"""
    params = []
    if hasattr(node, 'params'):
        for param in node.params:
            if hasattr(param, 'name'):
                params.append(param.name)
            elif hasattr(param, 'left') and hasattr(param.left, 'name'):
                # Default parameters (param = value)
                params.append(param.left.name)
    return params

def extract_function_returns(node):
    """Attempt to identify return statements in a function"""
    returns = []
    
    # Helper function to walk the body
    def find_returns(body_node):
        if not body_node:
            return
            
        # If it's a return statement
        if hasattr(body_node, 'type') and body_node.type == 'ReturnStatement':
            return_info = {"lineno": body_node.loc.start.line if hasattr(body_node, 'loc') else 0}
            
            # Try to determine return type
            if hasattr(body_node, 'argument') and body_node.argument:
                if hasattr(body_node.argument, 'type'):
                    return_info["type"] = body_node.argument.type
                    
                    # For literals, get the value
                    if body_node.argument.type == 'Literal' and hasattr(body_node.argument, 'value'):
                        return_info["value"] = str(body_node.argument.value)
                    # For identifiers, get the name
                    elif body_node.argument.type == 'Identifier' and hasattr(body_node.argument, 'name'):
                        return_info["value"] = body_node.argument.name
            
            returns.append(return_info)
        
        # Recursively process blocks
        if hasattr(body_node, 'body'):
            if isinstance(body_node.body, list):
                for child in body_node.body:
                    find_returns(child)
            else:
                find_returns(body_node.body)
    
    # Start walking from function body
    if hasattr(node, 'body'):
        find_returns(node.body)
        
    return returns

def extract_object_properties(obj_node):
    """Extract properties from an object literal"""
    properties = []
    if hasattr(obj_node, 'properties'):
        for prop in obj_node.properties:
            prop_info = {}
            
            # Property name
            if hasattr(prop, 'key'):
                if hasattr(prop.key, 'name'):
                    prop_info["name"] = prop.key.name
                elif hasattr(prop.key, 'value'):
                    prop_info["name"] = str(prop.key.value)
            
            # Property value type
            if hasattr(prop, 'value') and hasattr(prop.value, 'type'):
                prop_info["value_type"] = prop.value.type
                
                # For literal values, store the actual value
                if prop.value.type == 'Literal' and hasattr(prop.value, 'value'):
                    prop_info["value"] = str(prop.value.value)
                # For function expressions, mark as method
                elif prop.value.type in ['FunctionExpression', 'ArrowFunctionExpression']:
                    prop_info["is_method"] = True
                    prop_info["params"] = extract_function_params(prop.value)
            
            if prop_info:
                properties.append(prop_info)
    
    return properties

def extract_condition_text(condition_node):
    """Extract human-readable text from a condition node"""
    if not condition_node:
        return "unknown"
        
    # For identifiers, use the name
    if condition_node.type == 'Identifier' and hasattr(condition_node, 'name'):
        return condition_node.name
        
    # For literals, use the value
    if condition_node.type == 'Literal' and hasattr(condition_node, 'value'):
        return str(condition_node.value)
        
    # For binary expressions, try to reconstruct the expression
    if condition_node.type == 'BinaryExpression':
        left = extract_condition_text(condition_node.left) if hasattr(condition_node, 'left') else "?"
        right = extract_condition_text(condition_node.right) if hasattr(condition_node, 'right') else "?"
        operator = condition_node.operator if hasattr(condition_node, 'operator') else "?"
        return f"{left} {operator} {right}"
        
    # For member expressions (obj.prop), reconstruct
    if condition_node.type == 'MemberExpression':
        object_part = extract_condition_text(condition_node.object) if hasattr(condition_node, 'object') else "?"
        property_part = ""
        if hasattr(condition_node, 'property'):
            if hasattr(condition_node.property, 'name'):
                property_part = condition_node.property.name
            elif hasattr(condition_node.property, 'value'):
                property_part = str(condition_node.property.value)
        
        return f"{object_part}.{property_part}"
        
    # For call expressions, show the function name
    if condition_node.type == 'CallExpression' and hasattr(condition_node, 'callee'):
        if hasattr(condition_node.callee, 'name'):
            return f"{condition_node.callee.name}(...)"
        elif hasattr(condition_node.callee, 'type') and condition_node.callee.type == 'MemberExpression':
            return f"{extract_condition_text(condition_node.callee)}(...)"
    
    # Return the node type if we can't extract better info
    return condition_node.type 