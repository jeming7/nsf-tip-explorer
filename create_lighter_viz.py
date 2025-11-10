"""Create lighter, faster visualizations"""

from knowledge_graph import NSFKnowledgeGraph
import networkx as nx

kg = NSFKnowledgeGraph()
kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')

print("Creating faster visualizations with depth=1...")

# California - lighter version
print("\n1. California (lighter, faster)...")
kg.visualize_subgraph(
    "California",
    depth=1,  # Reduced from 2 to 1
    output_file="california_network_lite.html",
    title="California Research Network (Lite)",
    description="Faster visualization showing California's immediate connections - 818 awards and 520 organizations. Use depth=1 for better performance."
)

# MIT - lighter version
print("\n2. MIT (lighter, faster)...")
kg.visualize_subgraph(
    "Massachusetts Institute of Technology",
    depth=1,
    output_file="mit_network_lite.html",
    title="MIT Research Ecosystem (Lite)",
    description="Faster visualization of MIT's immediate research network. Shows awards and direct connections only."
)

# AI - lighter version
print("\n3. AI Technology (lighter, faster)...")
kg.visualize_subgraph(
    "Artificial Intelligence",
    depth=1,
    output_file="ai_tech_network_lite.html",
    title="AI Research Network (Lite)",
    description="Faster visualization of AI research showing 339 awards and their immediate connections."
)

print("\n" + "="*80)
print("Lite visualizations created!")
print("="*80)
print("\nAccess these faster versions at:")
print("  - http://localhost:8000/california_network_lite.html")
print("  - http://localhost:8000/mit_network_lite.html")
print("  - http://localhost:8000/ai_tech_network_lite.html")
print("\nThese should load much faster!")
