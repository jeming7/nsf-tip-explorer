# NSF TIP Awards Knowledge Graph

A comprehensive knowledge graph built from NSF Technology Innovation Partnership (TIP) awards data using Python, NetworkX, and PyVis.

## Overview

This project transforms NSF awards data into an interactive knowledge graph that captures relationships between:
- **Awards**: NSF grant awards with funding information
- **People**: Principal Investigators (PIs) and Co-Principal Investigators (CoPIs)
- **Organizations**: Universities, companies, and research institutions
- **Locations**: States and counties
- **Programs**: NSF funding programs
- **Technology Areas**: Key technology focus areas

## Knowledge Graph Schema

### Entities (Nodes)
1. **Award**: Individual NSF awards with title, amount, dates
2. **Person**: PIs and CoPIs
3. **Organization**: Institutions receiving awards
4. **State**: US states
5. **County**: US counties
6. **Program**: NSF programs (e.g., SBIR/STTR)
7. **Technology_Area**: Technology focus areas (AI, Biotech, etc.)

### Relationships (Edges)
- `Person -> LEADS -> Award`: PI leads the award
- `Person -> CO_LEADS -> Award`: CoPI co-leads the award
- `Award -> AWARDED_TO -> Organization`: Award given to organization
- `Award -> FUNDED_BY -> Program`: Award funded by program
- `Award -> INVOLVES_TECH -> Technology_Area`: Award involves technology
- `Organization -> LOCATED_IN_STATE -> State`: Org location
- `Organization -> LOCATED_IN_COUNTY -> County`: Org county location

## Files

### Core Scripts
- **`knowledge_graph.py`**: Main script to build the knowledge graph from Excel data
- **`query_graph.py`**: Utility script for querying and analyzing the graph
- **`explore_data.py`**: Data exploration and statistics script

### Generated Files
- **`nsf_knowledge_graph.graphml`**: The complete knowledge graph in GraphML format
- **`graph_statistics.json`**: Graph statistics and metrics
- **`sample_organization_network.html`**: Interactive visualization example

## Installation

1. Install required Python packages:
```bash
pip install pandas openpyxl networkx matplotlib pyvis
```

## Usage

### 1. Build the Knowledge Graph

```bash
python knowledge_graph.py
```

This will:
- Load the Excel data (5,515 awards)
- Build a graph with 16,912 nodes and 37,115 edges
- Generate visualizations and statistics
- Save the graph to `nsf_knowledge_graph.graphml`

### 2. Query and Analyze

```bash
python query_graph.py
```

This provides:
- Top connected organizations
- Technology area statistics
- State-by-state funding analysis
- Sample node details

### 3. Custom Queries

You can write custom Python scripts using the `KnowledgeGraphQuery` class:

```python
from query_graph import KnowledgeGraphQuery

# Load the graph
kgq = KnowledgeGraphQuery()

# Find a specific person
results = kgq.find_node("Smith", node_type="Person")

# Get node details
details = kgq.get_node_details("2429456")  # Award ID

# Find collaborations
collaborators = kgq.find_collaborations("John Doe")

# Get most connected organizations
top_orgs = kgq.get_most_connected_nodes("Organization", top_n=20)

# Export to DataFrame for analysis
df_awards = kgq.export_to_dataframe("Award")
```

### 4. Create Custom Visualizations

```python
from knowledge_graph import NSFKnowledgeGraph
import networkx as nx

kg = NSFKnowledgeGraph()
kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')

# Visualize a specific organization's network
kg.visualize_subgraph("Massachusetts Institute of Technology",
                      depth=2,
                      output_file="mit_network.html")

# Create a subgraph
subgraph = kg.get_subgraph("Artificial Intelligence", depth=1)
```

## Key Statistics

From the NSF TIP dataset (as of Nov 2025):

### Graph Size
- **Total Nodes**: 16,912
- **Total Edges**: 37,115

### Entities
- **Awards**: 5,513
- **People**: 7,701
- **Organizations**: 2,738
- **States**: 55
- **Counties**: 497
- **Programs**: 14
- **Technology Areas**: 394

### Top Insights

**Most Connected Organizations:**
1. Massachusetts Institute of Technology (195 connections)
2. University of Michigan - Ann Arbor (168 connections)
3. University of Texas at Austin (159 connections)

**Top Technology Areas by Funding:**
1. Biotechnology: $410M+ (1,118 awards)
2. Cross-Cutting: $527M+ (281 awards)
3. Artificial Intelligence: $140M+ (339 awards)

**Top States by Funding:**
1. California: $506M+ (818 awards)
2. Massachusetts: $271M+ (408 awards)
3. New York: $262M+ (467 awards)

## Example Queries

### Find all awards for a specific organization
```python
kgq = KnowledgeGraphQuery()
mit_details = kgq.get_node_details("Massachusetts Institute of Technology")
print(f"MIT has {mit_details['total_incoming']} awards")
```

### Analyze collaboration networks
```python
# Find who someone has collaborated with
collaborators = kgq.find_collaborations("Shatha D Denno")
print(f"Found {len(collaborators)} collaborators")
```

### Technology area analysis
```python
tech_stats, tech_funding = kgq.get_technology_statistics()
sorted_tech = sorted(tech_stats.items(), key=lambda x: x[1], reverse=True)

for tech, count in sorted_tech[:10]:
    print(f"{tech}: {count} awards, ${tech_funding[tech]:,.2f} funding")
```

## Data Format

The input Excel file should contain these columns:
- Award ID
- Award Title
- Total Intended Amount (USD)
- Award URL
- Award Date, Start Date, End Date
- PI/CoPI
- Award Organization
- State, Congressional District, County
- TIP Programs
- Key Technology Areas
- Active, EPSCoR
- Portal URL

## Advanced Features

### Graph Analysis with NetworkX

Since the graph is stored in GraphML format, you can use any NetworkX functions:

```python
import networkx as nx

G = nx.read_graphml('nsf_knowledge_graph.graphml')

# Find shortest path between two entities
path = nx.shortest_path(G, source_node, target_node)

# Calculate centrality measures
betweenness = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

# Find communities
communities = nx.community.greedy_modularity_communities(G)

# Export to other formats
nx.write_gexf(G, 'graph.gexf')  # For Gephi
nx.write_graphml(G, 'graph.graphml')  # GraphML
```

### Visualization Options

The interactive HTML visualizations support:
- Zoom and pan
- Click nodes for details
- Physics-based layout
- Color-coded node types
- Relationship labels on edges

## Future Enhancements

Potential improvements:
1. **Time-series analysis**: Track funding trends over time
2. **Neo4j integration**: Export to graph database for complex queries
3. **Network metrics**: Calculate centrality, clustering coefficients
4. **Collaboration analysis**: Identify research communities
5. **Geospatial visualization**: Map-based views of funding distribution
6. **NLP integration**: Extract insights from award titles/abstracts

## License

This project uses publicly available NSF data.

## Contact

For questions or issues, please open an issue in the repository.
