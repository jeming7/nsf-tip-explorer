import networkx as nx
import json
from collections import Counter, defaultdict
import pandas as pd

class KnowledgeGraphQuery:
    """Utility class for querying the NSF Knowledge Graph"""

    def __init__(self, graphml_file='nsf_knowledge_graph.graphml'):
        print(f"Loading knowledge graph from {graphml_file}...")
        self.graph = nx.read_graphml(graphml_file)
        print(f"Graph loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def find_node(self, search_term, node_type=None):
        """Find nodes containing the search term"""
        results = []
        search_lower = search_term.lower()

        for node, data in self.graph.nodes(data=True):
            if node_type and data.get('type') != node_type:
                continue

            if search_lower in node.lower():
                results.append((node, data))

        return results

    def get_node_details(self, node_id):
        """Get detailed information about a node"""
        if not self.graph.has_node(node_id):
            print(f"Node '{node_id}' not found in graph")
            return None

        node_data = dict(self.graph.nodes[node_id])

        # Get incoming relationships
        incoming = []
        for pred in self.graph.predecessors(node_id):
            edge_data = self.graph.get_edge_data(pred, node_id)
            for edge in edge_data.values():
                incoming.append({
                    'from': pred,
                    'relationship': edge.get('relationship', 'unknown'),
                    'type': self.graph.nodes[pred].get('type', 'unknown')
                })

        # Get outgoing relationships
        outgoing = []
        for succ in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, succ)
            for edge in edge_data.values():
                outgoing.append({
                    'to': succ,
                    'relationship': edge.get('relationship', 'unknown'),
                    'type': self.graph.nodes[succ].get('type', 'unknown')
                })

        return {
            'id': node_id,
            'attributes': node_data,
            'incoming_connections': incoming,
            'outgoing_connections': outgoing,
            'total_incoming': len(incoming),
            'total_outgoing': len(outgoing)
        }

    def get_most_connected_nodes(self, node_type=None, top_n=10, by='total'):
        """Find the most connected nodes"""
        nodes_degrees = []

        for node, data in self.graph.nodes(data=True):
            if node_type and data.get('type') != node_type:
                continue

            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            total_degree = in_degree + out_degree

            if by == 'in':
                degree = in_degree
            elif by == 'out':
                degree = out_degree
            else:
                degree = total_degree

            nodes_degrees.append((node, degree, in_degree, out_degree, data))

        # Sort by degree
        nodes_degrees.sort(key=lambda x: x[1], reverse=True)

        return nodes_degrees[:top_n]

    def get_technology_statistics(self):
        """Get statistics about technology areas"""
        tech_stats = defaultdict(int)
        tech_funding = defaultdict(float)

        for node, data in self.graph.nodes(data=True):
            if data.get('type') != 'Technology_Area':
                continue

            # Count awards connected to this technology
            tech_awards = list(self.graph.predecessors(node))
            tech_stats[node] = len(tech_awards)

            # Sum funding
            total_funding = 0
            for award in tech_awards:
                award_data = self.graph.nodes[award]
                amount = award_data.get('amount', '0')
                try:
                    total_funding += float(amount) if amount else 0
                except (ValueError, TypeError):
                    pass

            tech_funding[node] = total_funding

        return tech_stats, tech_funding

    def get_organization_statistics(self):
        """Get statistics about organizations"""
        org_stats = defaultdict(lambda: {'awards': 0, 'total_funding': 0, 'people': set()})

        for node, data in self.graph.nodes(data=True):
            if data.get('type') != 'Organization':
                continue

            # Get awards
            awards = list(self.graph.predecessors(node))
            org_stats[node]['awards'] = len(awards)

            # Calculate total funding
            total_funding = 0
            for award in awards:
                award_data = self.graph.nodes[award]
                amount = award_data.get('amount', '0')
                try:
                    total_funding += float(amount) if amount else 0
                except (ValueError, TypeError):
                    pass

            org_stats[node]['total_funding'] = total_funding

            # Count people
            for award in awards:
                people = list(self.graph.predecessors(award))
                for person in people:
                    person_data = self.graph.nodes[person]
                    if person_data.get('type') == 'Person':
                        org_stats[node]['people'].add(person)

        # Convert sets to counts
        for org in org_stats:
            org_stats[org]['people'] = len(org_stats[org]['people'])

        return org_stats

    def get_state_statistics(self):
        """Get statistics by state"""
        state_stats = defaultdict(lambda: {'organizations': set(), 'awards': 0, 'total_funding': 0})

        for node, data in self.graph.nodes(data=True):
            if data.get('type') != 'State':
                continue

            # Get organizations in this state
            orgs = list(self.graph.predecessors(node))
            state_stats[node]['organizations'] = set(orgs)

            # Get awards
            total_awards = 0
            total_funding = 0

            for org in orgs:
                awards = list(self.graph.predecessors(org))
                total_awards += len(awards)

                for award in awards:
                    award_data = self.graph.nodes[award]
                    amount = award_data.get('amount', '0')
                    try:
                        total_funding += float(amount) if amount else 0
                    except (ValueError, TypeError):
                        pass

            state_stats[node]['awards'] = total_awards
            state_stats[node]['total_funding'] = total_funding
            state_stats[node]['organizations'] = len(state_stats[node]['organizations'])

        return state_stats

    def find_collaborations(self, person_name):
        """Find collaborators of a specific person"""
        # Find the person node
        people = self.find_node(person_name, 'Person')

        if not people:
            print(f"Person '{person_name}' not found")
            return []

        person_node = people[0][0]
        print(f"\nFinding collaborations for: {person_node}")

        # Get awards this person is involved in
        awards = list(self.graph.successors(person_node))

        collaborators = set()
        for award in awards:
            # Get all people on this award
            people_on_award = [p for p in self.graph.predecessors(award)
                             if self.graph.nodes[p].get('type') == 'Person']

            collaborators.update(people_on_award)

        # Remove the person themselves
        collaborators.discard(person_node)

        return list(collaborators)

    def export_to_dataframe(self, node_type):
        """Export nodes of a specific type to a pandas DataFrame"""
        data = []

        for node, attrs in self.graph.nodes(data=True):
            if attrs.get('type') == node_type:
                row = {'id': node}
                row.update(attrs)

                # Add degree information
                row['in_degree'] = self.graph.in_degree(node)
                row['out_degree'] = self.graph.out_degree(node)

                data.append(row)

        return pd.DataFrame(data)


# Example usage
if __name__ == "__main__":
    # Load graph
    kgq = KnowledgeGraphQuery()

    print("\n" + "="*80)
    print("TOP 10 MOST CONNECTED ORGANIZATIONS (by total connections)")
    print("="*80)
    top_orgs = kgq.get_most_connected_nodes('Organization', top_n=10)
    for i, (org, total, in_deg, out_deg, data) in enumerate(top_orgs, 1):
        print(f"{i}. {org}")
        print(f"   Total connections: {total} (In: {in_deg}, Out: {out_deg})")

    print("\n" + "="*80)
    print("TOP 10 TECHNOLOGY AREAS (by number of awards)")
    print("="*80)
    tech_stats, tech_funding = kgq.get_technology_statistics()
    sorted_tech = sorted(tech_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (tech, count) in enumerate(sorted_tech, 1):
        funding = tech_funding[tech]
        print(f"{i}. {tech}")
        print(f"   Awards: {count}, Total Funding: ${funding:,.2f}")

    print("\n" + "="*80)
    print("TOP 10 STATES (by total funding)")
    print("="*80)
    state_stats = kgq.get_state_statistics()
    sorted_states = sorted(state_stats.items(), key=lambda x: x[1]['total_funding'], reverse=True)[:10]
    for i, (state, stats) in enumerate(sorted_states, 1):
        print(f"{i}. {state}")
        print(f"   Organizations: {stats['organizations']}, Awards: {stats['awards']}, Funding: ${stats['total_funding']:,.2f}")

    print("\n" + "="*80)
    print("SAMPLE NODE DETAILS")
    print("="*80)
    # Get details of the first award
    sample_award = None
    for node, data in kgq.graph.nodes(data=True):
        if data.get('type') == 'Award':
            sample_award = node
            break

    if sample_award:
        details = kgq.get_node_details(sample_award)
        print(f"\nNode ID: {details['id']}")
        print(f"Type: {details['attributes'].get('type')}")
        print(f"Title: {details['attributes'].get('title', 'N/A')[:100]}...")
        print(f"\nIncoming connections: {details['total_incoming']}")
        for conn in details['incoming_connections'][:5]:
            print(f"  <- {conn['relationship']} from {conn['from'][:50]}... ({conn['type']})")
        print(f"\nOutgoing connections: {details['total_outgoing']}")
        for conn in details['outgoing_connections'][:5]:
            print(f"  -> {conn['relationship']} to {conn['to'][:50]}... ({conn['type']})")

    print("\n" + "="*80)
    print("Query Script Complete!")
    print("="*80)
