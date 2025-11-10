# NSF TIP Awards Knowledge Graph - Project Summary

## Overview
Successfully created a comprehensive knowledge graph from NSF Technology Innovation Partnership (TIP) awards data with **16,912 nodes** and **37,115 edges**, representing a complex network of research funding, institutions, people, and technologies.

## What Was Built

### 1. Core Knowledge Graph System
- **Multi-entity graph** with 7 node types and 7 relationship types
- **GraphML export** for use with other graph tools (Gephi, Cytoscape, Neo4j)
- **NetworkX-based** implementation for powerful graph algorithms
- **Scalable architecture** that can handle thousands of records

### 2. Entity Types Captured
| Entity Type | Count | Description |
|------------|-------|-------------|
| Awards | 5,513 | NSF grant awards with funding details |
| People | 7,701 | Principal Investigators and Co-PIs |
| Organizations | 2,738 | Universities, companies, research labs |
| Technology Areas | 394 | AI, Biotech, Advanced Materials, etc. |
| Counties | 497 | Geographic distribution |
| States | 55 | All US states + territories |
| Programs | 14 | NSF funding programs |

### 3. Relationship Types Modeled
- **LEADS**: Person leads an award (6,029 connections)
- **CO_LEADS**: Person co-leads an award (3,240 connections)
- **AWARDED_TO**: Award given to organization (5,514 connections)
- **FUNDED_BY**: Award funded by program (5,514 connections)
- **INVOLVES_TECH**: Award involves technology area (5,790 connections)
- **LOCATED_IN_STATE**: Organization in state (5,514 connections)
- **LOCATED_IN_COUNTY**: Organization in county (5,514 connections)

## Key Scripts Created

### 1. `knowledge_graph.py` (Main Builder)
- Loads Excel data
- Constructs the knowledge graph
- Generates visualizations
- Exports to GraphML format
- Calculates statistics

**Usage:**
```bash
python knowledge_graph.py
```

### 2. `query_graph.py` (Query Engine)
- Load and query the graph
- Find nodes and relationships
- Calculate statistics
- Export to DataFrame
- Analyze collaborations

**Usage:**
```bash
python query_graph.py
```

### 3. `interactive_examples.py` (Demo Suite)
Generates 7 different types of analyses:
1. Organization network visualization
2. Technology area analysis
3. State-by-state comparison
4. Collaboration network analysis
5. Organization rankings
6. Custom subgraph visualizations
7. Award details deep dive

**Usage:**
```bash
python interactive_examples.py
```

### 4. `explore_data.py` (Data Explorer)
Initial data exploration and statistics

## Generated Files

### Visualizations (Interactive HTML)
- **mit_network.html** - MIT's research network (410 nodes)
- **ai_tech_network.html** - AI technology ecosystem (1,081 nodes)
- **california_network.html** - California research network (1,374 nodes)
- **sample_organization_network.html** - Example organization network

### Data Exports
- **nsf_knowledge_graph.graphml** - Complete graph (16,912 nodes, 37,115 edges)
- **graph_statistics.json** - Graph metrics and statistics
- **technology_analysis.csv** - Technology areas ranked by funding/awards
- **state_analysis.csv** - State-by-state funding breakdown
- **organization_analysis.csv** - Organization rankings and metrics

## Top Insights from the Data

### Most Connected Organizations (Research Powerhouses)
1. **MIT** - 195 connections (65 awards, $52.3M)
2. **University of Michigan** - 168 connections (56 awards, $45.2M)
3. **UT Austin** - 159 connections (53 awards, $27.2M)
4. **Cornell University** - 144 connections (48 awards, $34.5M)
5. **UC Berkeley** - 138 connections (46 awards, $29.3M)

### Top Technology Areas by Funding
1. **Cross-Cutting & Capacity Building** - $527.7M (281 awards)
2. **Biotechnology** - $410.5M (1,118 awards)
3. **Artificial Intelligence** - $140.0M (339 awards)
4. **Robotics and Manufacturing** - $102.6M (237 awards)
5. **Computing & Semiconductors** - $95.7M (219 awards)

### Top States by Total Funding
1. **California** - $506.9M (818 awards, 520 orgs)
2. **Massachusetts** - $271.7M (408 awards, 228 orgs)
3. **New York** - $262.9M (467 awards, 219 orgs)
4. **Texas** - $153.4M (378 awards, 150 orgs)
5. **Illinois** - $140.6M (144 awards, 79 orgs)

### Most Active Researchers
1. **Roman M Lubynsky** (MIT) - 24 awards
2. **Jin K Montclare** - 7 awards
3. **Dan Freeman** - 7 awards
4. **Marouane Kessentini** - 7 awards

### Largest Individual Awards
1. **$20M** - Entrepreneurial Fellowships (ACTIVATE GLOBAL)
2. **$20M** - Global Observatory (University of Chicago)
3. **$20M** - Technology Outcomes (Northwestern)
4. **$15M** - Multiple I-Corps Hubs and NSF Engines

## Use Cases Demonstrated

### 1. Network Analysis
- Identify research collaboration networks
- Find central/influential organizations
- Discover research communities

### 2. Funding Analysis
- Track investment by technology area
- Compare state-level funding
- Analyze organization portfolios

### 3. Collaboration Discovery
- Find researchers who work together
- Identify inter-organizational partnerships
- Map technology intersections

### 4. Geographic Analysis
- Visualize regional research ecosystems
- Compare state capabilities
- Identify funding distribution patterns

### 5. Technology Mapping
- See which technologies are interconnected
- Find organizations specializing in areas
- Track technology adoption trends

## Technical Architecture

### Data Flow
```
Excel Data (5,515 awards)
    ↓
pandas DataFrame
    ↓
NetworkX MultiDiGraph (16,912 nodes, 37,115 edges)
    ↓
├─ GraphML Export → For external tools
├─ PyVis Visualization → Interactive HTML
├─ Statistics → JSON/CSV exports
└─ Query Engine → Programmatic access
```

### Key Design Decisions

1. **MultiDiGraph**: Supports multiple edges between nodes with different relationships
2. **NetworkX**: Industry-standard graph library with rich algorithms
3. **GraphML Format**: Standard format for interoperability
4. **PyVis**: Interactive visualizations with physics-based layouts
5. **Modular Design**: Separate builder, query, and visualization components

## What You Can Do With This Graph

### Immediate Use Cases
1. **Open HTML files** in a browser to explore interactive visualizations
2. **Query specific entities** using the Python scripts
3. **Export subgraphs** for focused analysis
4. **Generate custom reports** with CSV exports
5. **Calculate network metrics** (centrality, clustering, etc.)

### Advanced Use Cases
1. **Import into Neo4j** for advanced graph queries (Cypher)
2. **Use Gephi** for large-scale network visualization
3. **Apply community detection** algorithms
4. **Perform time-series analysis** of funding trends
5. **Build recommendation systems** (similar awards, collaborators)
6. **Create dashboards** with Plotly/Dash
7. **Train ML models** on graph embeddings

## Graph Statistics

```json
{
  "total_nodes": 16912,
  "total_edges": 37115,
  "density": 0.00013,
  "node_types": 7,
  "relationship_types": 7,
  "largest_component": "~16,000 nodes connected"
}
```

## Example Queries You Can Run

### Python API Examples

```python
from query_graph import KnowledgeGraphQuery

kgq = KnowledgeGraphQuery()

# Find all awards for an organization
mit_info = kgq.get_node_details("Massachusetts Institute of Technology")

# Get technology statistics
tech_stats, tech_funding = kgq.get_technology_statistics()

# Find collaborators
collaborators = kgq.find_collaborations("Roman M Lubynsky")

# Most connected nodes
top_orgs = kgq.get_most_connected_nodes("Organization", top_n=20)

# Export to DataFrame
awards_df = kgq.export_to_dataframe("Award")
```

### NetworkX Examples

```python
import networkx as nx

G = nx.read_graphml('nsf_knowledge_graph.graphml')

# Calculate centrality
betweenness = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

# Find shortest path
path = nx.shortest_path(G, "MIT", "Stanford University")

# Community detection
communities = nx.community.greedy_modularity_communities(G)

# Degree distribution
degrees = dict(G.degree())
```

## Future Enhancement Opportunities

1. **Time-based analysis** - Track evolution over years
2. **Sentiment analysis** - Analyze award abstracts with NLP
3. **Prediction models** - Predict successful collaborations
4. **Real-time updates** - Automatically ingest new NSF data
5. **Web dashboard** - Interactive web-based exploration tool
6. **Integration with other datasets** - Publications, patents, citations
7. **Machine learning** - Node classification, link prediction
8. **Geospatial maps** - Interactive geographic visualizations

## Requirements

```
pandas >= 2.0
openpyxl >= 3.0
networkx >= 3.0
matplotlib >= 3.0
pyvis >= 0.3
```

## Installation

```bash
pip install pandas openpyxl networkx matplotlib pyvis
```

## Project Structure

```
TIP_KG/
├── nsf-awards-export-2025-11-07.xlsx    # Source data
├── knowledge_graph.py                    # Main graph builder
├── query_graph.py                        # Query engine
├── interactive_examples.py               # Example analyses
├── explore_data.py                       # Data exploration
├── README.md                             # Documentation
├── SUMMARY.md                            # This file
├── nsf_knowledge_graph.graphml          # Graph export
├── graph_statistics.json                # Statistics
├── *.html                               # Interactive visualizations
└── *.csv                                # Analysis exports
```

## Success Metrics

- ✅ Successfully parsed 5,515 awards
- ✅ Created 16,912 nodes with 37,115 relationships
- ✅ Generated 4 interactive HTML visualizations
- ✅ Exported 3 CSV analysis files
- ✅ Built reusable query engine
- ✅ Comprehensive documentation
- ✅ Multiple example use cases
- ✅ GraphML export for tool interoperability

## Conclusion

This project demonstrates **Option 1 (Python + NetworkX)** as recommended - a powerful, flexible approach to building knowledge graphs that:

1. **Scales well** - Handles thousands of entities efficiently
2. **Integrates easily** - Works with pandas, visualization tools, databases
3. **Enables rich queries** - Leverages NetworkX's extensive algorithms
4. **Produces interactive visualizations** - PyVis creates engaging HTML outputs
5. **Exports to standards** - GraphML for use with other tools
6. **Supports iteration** - Easy to extend and customize

The knowledge graph is now ready for analysis, visualization, and integration into larger systems. You can explore relationships, discover patterns, and gain insights into the NSF TIP research ecosystem!
