"""Check if all organizations are connected to awards"""

import networkx as nx

# Load the graph
graph = nx.read_graphml('nsf_knowledge_graph.graphml')

# Get all organization nodes
orgs = [node for node, data in graph.nodes(data=True) if data.get('type') == 'Organization']

print(f"Total organizations in graph: {len(orgs)}")

# Check which organizations have awards
orgs_with_awards = 0
orgs_without_awards = []

for org in orgs:
    # Check for incoming AWARDED_TO edges from awards
    has_award = False
    for predecessor in graph.predecessors(org):
        pred_type = graph.nodes[predecessor].get('type')
        # Check if there's an AWARDED_TO edge from an Award node
        for edge_key, edge_data in graph[predecessor][org].items():
            if edge_data.get('relationship') == 'AWARDED_TO' and pred_type == 'Award':
                has_award = True
                break
        if has_award:
            break

    if has_award:
        orgs_with_awards += 1
    else:
        orgs_without_awards.append(org)

print(f"Organizations WITH awards: {orgs_with_awards}")
print(f"Organizations WITHOUT awards: {len(orgs_without_awards)}")

if orgs_without_awards:
    print(f"\nFirst 10 organizations without awards:")
    for org in orgs_without_awards[:10]:
        print(f"  - {org}")
        # Check what connections they DO have
        in_edges = list(graph.in_edges(org, data=True))
        out_edges = list(graph.out_edges(org, data=True))
        print(f"    Incoming edges: {len(in_edges)}")
        print(f"    Outgoing edges: {len(out_edges)}")
        if out_edges:
            for src, tgt, data in out_edges[:3]:
                print(f"      -> {data.get('relationship')} -> {graph.nodes[tgt].get('type')}")
