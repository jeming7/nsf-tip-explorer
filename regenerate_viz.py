"""Quick script to regenerate specific visualizations"""

from knowledge_graph import NSFKnowledgeGraph
import networkx as nx

kg = NSFKnowledgeGraph()
kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')

print("Regenerating visualizations with fixes...")

# MIT
print("\n1. MIT Network...")
kg.visualize_subgraph(
    "Massachusetts Institute of Technology",
    depth=2,
    output_file="mit_network.html",
    title="MIT Research Ecosystem",
    description="Explore MIT's 65 NSF TIP awards, the researchers leading them, technology areas, and connections to programs and locations. This network shows MIT's research strengths and collaboration patterns."
)

# AI
print("\n2. AI Network...")
kg.visualize_subgraph(
    "Artificial Intelligence",
    depth=2,
    output_file="ai_tech_network.html",
    title="Artificial Intelligence Research Ecosystem",
    description="Network of 339 AI-related awards across the U.S. See which organizations lead AI research, how AI intersects with other technologies (Biotech, Robotics, etc.), and the key researchers driving innovation in artificial intelligence."
)

# California
print("\n3. California Network...")
kg.visualize_subgraph(
    "California",
    depth=2,
    output_file="california_network.html",
    title="California Research & Innovation Network",
    description="California's dominant research ecosystem with 818 awards totaling $507M across 520 organizations. Explore connections between Stanford, Berkeley, Caltech, and other institutions, their technology focus areas, and the researchers driving innovation."
)

print("\nAll visualizations regenerated with fixes!")
print("Refresh your browser to see the updated versions.")
