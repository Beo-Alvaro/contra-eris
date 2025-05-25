# Contra Eris

A system for generating and evaluating Compressed Base Summary Files (CBSF) of codebases.

## Overview

Contra Eris provides tools to:
1. Generate CBSF files from codebases
2. Evaluate them with various metrics
3. Visualize dependencies and metrics
4. Create HTML reports for analysis

## Installation

```bash
pip install contra-eris
```

## Usage

### Command Line Interface

Contra Eris provides three command-line tools:

#### 1. Main command with subcommands

```bash
# Generate a CBSF
contra-eris generate --project path/to/project

# Evaluate a CBSF
contra-eris evaluate --project path/to/project --cbsf path/to/cbsf.json --visualize
```

#### 2. Direct commands

```bash
# Generate a CBSF
contra-eris-generate --project path/to/project

# Evaluate a CBSF
contra-eris-evaluate --project path/to/project --cbsf path/to/cbsf.json --visualize
```

### Python API

You can also use Contra Eris as a Python library:

```python
import contra_eris

# Generate a CBSF
results = contra_eris.analyze_project("path/to/project")

# Evaluate a CBSF
metrics = contra_eris.evaluate_cbsf("path/to/project", "path/to/cbsf.json")

# Evaluate with visualizations
metrics = contra_eris.evaluate_with_visualization(
    "path/to/project", 
    "path/to/cbsf.json", 
    "output_dir"
)
```

## Command Options

### Generate Command

```
--project       Project directory to analyze (default: current directory)
--output        Output directory for results (default: output)
--extensions    Comma-separated list of file extensions to include (default: .py)
--quiet         Suppress output messages
```

### Evaluate Command

```
--project       Original project directory
--cbsf          Path to CBSF file to evaluate
--output        Output directory for results (default: output)
--metrics-file  Path to save metrics JSON file
--visualize     Generate visualizations and HTML report
--quiet         Suppress output messages
```

## Metrics

Contra Eris evaluates the following metrics:

1. **Compression Ratio**: Ratio between CBSF size and original codebase size
2. **Graph Metrics**: 
   - Node count
   - Edge count
   - Connectivity
   - Community structure
3. **Dependency Complexity**:
   - Fan-in/Fan-out ratios
   - Instability
4. **Information Entropy**: Measures the complexity of dependency distribution

## Output

The evaluation generates:
- `dependency_graph.png`: Visualization of dependencies
- `fan_in_out.png`: Fan-in/Fan-out distribution
- `instability.png`: Instability distribution
- `report.html`: Comprehensive HTML report
- `metrics.json`: Raw metrics data (if specified)
