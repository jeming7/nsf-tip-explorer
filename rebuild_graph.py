"""Rebuild the knowledge graph with duplicate edge fix"""

from knowledge_graph import NSFKnowledgeGraph

print("="*80)
print("REBUILDING KNOWLEDGE GRAPH")
print("="*80)
print("\nThis will rebuild the graph with the fix for duplicate LOCATED_IN edges.")
print("Each organization will now have only ONE edge to its state/county.\n")

# Create and build the knowledge graph
kg = NSFKnowledgeGraph()

# Load data
df = kg.load_data('nsf-awards-export-2025-11-07.xlsx')

# Build graph
kg.build_graph()

# Save graph to GraphML
kg.save_graph('nsf_knowledge_graph.graphml')

# Export statistics
kg.export_statistics('graph_statistics.json')

print("\n" + "="*80)
print("REBUILD COMPLETE!")
print("="*80)
print("\nThe knowledge graph has been rebuilt and saved.")
print("All visualizations will now show single edges between organizations and states.")
