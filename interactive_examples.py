"""
Interactive Examples for NSF Knowledge Graph
Demonstrates various ways to query and visualize the knowledge graph
"""

import networkx as nx
from query_graph import KnowledgeGraphQuery
from knowledge_graph import NSFKnowledgeGraph
import pandas as pd


def example_1_find_organization_network():
    """Example 1: Visualize a specific organization's network"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Organization Network Visualization")
    print("="*80)

    kg = NSFKnowledgeGraph()
    kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')

    # Choose an organization
    org_name = "Massachusetts Institute of Technology"
    print(f"\nCreating network visualization for: {org_name}")

    kg.visualize_subgraph(
        org_name,
        depth=2,
        output_file="mit_network.html",
        title="MIT Research Ecosystem",
        description="Explore MIT's 65 NSF TIP awards, the researchers leading them, technology areas, and connections to programs and locations. This network shows MIT's research strengths and collaboration patterns."
    )
    print("[OK] Visualization saved to: mit_network.html")


def example_2_analyze_technology_areas():
    """Example 2: Analyze technology areas and their relationships"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Technology Area Analysis")
    print("="*80)

    kgq = KnowledgeGraphQuery()

    tech_stats, tech_funding = kgq.get_technology_statistics()

    # Create a pandas DataFrame for easy analysis
    tech_df = pd.DataFrame([
        {
            'Technology Area': tech,
            'Number of Awards': tech_stats[tech],
            'Total Funding': tech_funding[tech],
            'Avg Funding per Award': tech_funding[tech] / tech_stats[tech] if tech_stats[tech] > 0 else 0
        }
        for tech in tech_stats.keys()
    ])

    tech_df = tech_df.sort_values('Total Funding', ascending=False)

    print("\nTop 15 Technology Areas by Total Funding:")
    print(tech_df.head(15).to_string(index=False))

    # Export to CSV
    tech_df.to_csv('technology_analysis.csv', index=False)
    print("\n[OK] Full analysis exported to: technology_analysis.csv")


def example_3_state_comparison():
    """Example 3: Compare states by various metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 3: State-by-State Comparison")
    print("="*80)

    kgq = KnowledgeGraphQuery()
    state_stats = kgq.get_state_statistics()

    # Create DataFrame
    state_df = pd.DataFrame([
        {
            'State': state,
            'Organizations': stats['organizations'],
            'Awards': stats['awards'],
            'Total Funding': stats['total_funding'],
            'Avg Funding per Award': stats['total_funding'] / stats['awards'] if stats['awards'] > 0 else 0
        }
        for state, stats in state_stats.items()
    ])

    state_df = state_df.sort_values('Total Funding', ascending=False)

    print("\nTop 20 States by Total Funding:")
    print(state_df.head(20).to_string(index=False))

    # Export
    state_df.to_csv('state_analysis.csv', index=False)
    print("\n[OK] Full analysis exported to: state_analysis.csv")


def example_4_find_collaborations():
    """Example 4: Analyze collaboration networks"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Collaboration Network Analysis")
    print("="*80)

    kgq = KnowledgeGraphQuery()

    # Find people nodes
    print("\nFinding highly collaborative researchers...")

    people_degrees = []
    for node, data in kgq.graph.nodes(data=True):
        if data.get('type') == 'Person':
            degree = kgq.graph.out_degree(node)  # Number of awards they lead/co-lead
            if degree > 0:
                people_degrees.append((node, degree))

    # Sort by number of awards
    people_degrees.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 20 Most Active Researchers (by number of awards):")
    for i, (person, awards) in enumerate(people_degrees[:20], 1):
        print(f"{i:2d}. {person:60s} - {awards} awards")

    # Pick one and find their collaborators
    if people_degrees:
        top_person = people_degrees[0][0]
        print(f"\nFinding collaborators for: {top_person}")

        collaborators = kgq.find_collaborations(top_person)
        print(f"Found {len(collaborators)} collaborators:")
        for i, collab in enumerate(collaborators[:10], 1):
            print(f"  {i}. {collab}")


def example_5_organization_rankings():
    """Example 5: Rank organizations by multiple metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Organization Rankings")
    print("="*80)

    kgq = KnowledgeGraphQuery()
    org_stats = kgq.get_organization_statistics()

    # Create DataFrame
    org_df = pd.DataFrame([
        {
            'Organization': org,
            'Number of Awards': stats['awards'],
            'Total Funding': stats['total_funding'],
            'Number of Researchers': stats['people'],
            'Avg Funding per Award': stats['total_funding'] / stats['awards'] if stats['awards'] > 0 else 0
        }
        for org, stats in org_stats.items()
        if stats['awards'] > 0
    ])

    print("\n--- Top 15 by Number of Awards ---")
    top_by_awards = org_df.sort_values('Number of Awards', ascending=False)
    print(top_by_awards.head(15)[['Organization', 'Number of Awards', 'Total Funding']].to_string(index=False))

    print("\n--- Top 15 by Total Funding ---")
    top_by_funding = org_df.sort_values('Total Funding', ascending=False)
    print(top_by_funding.head(15)[['Organization', 'Total Funding', 'Number of Awards']].to_string(index=False))

    print("\n--- Top 15 by Number of Researchers ---")
    top_by_people = org_df.sort_values('Number of Researchers', ascending=False)
    print(top_by_people.head(15)[['Organization', 'Number of Researchers', 'Number of Awards']].to_string(index=False))

    # Export
    org_df.to_csv('organization_analysis.csv', index=False)
    print("\n[OK] Full analysis exported to: organization_analysis.csv")


def example_6_custom_subgraph():
    """Example 6: Create custom subgraph visualizations"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Custom Subgraph Visualizations")
    print("="*80)

    kg = NSFKnowledgeGraph()
    kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')

    # Find and visualize an AI technology area
    print("\nCreating visualization for Artificial Intelligence technology area...")
    kg.visualize_subgraph(
        "Artificial Intelligence",
        depth=2,
        output_file="ai_tech_network.html",
        title="Artificial Intelligence Research Ecosystem",
        description="Network of 339 AI-related awards across the U.S. See which organizations lead AI research, how AI intersects with other technologies (Biotech, Robotics, etc.), and the key researchers driving innovation in artificial intelligence."
    )
    print("[OK] Saved to: ai_tech_network.html")

    # Visualize a state's ecosystem
    print("\nCreating visualization for California's research ecosystem...")
    kg.visualize_subgraph(
        "California",
        depth=2,
        output_file="california_network.html",
        title="California Research & Innovation Network",
        description="California's dominant research ecosystem with 818 awards totaling $507M across 520 organizations. Explore connections between Stanford, Berkeley, Caltech, and other institutions, their technology focus areas, and the researchers driving innovation."
    )
    print("[OK] Saved to: california_network.html")


def example_7_award_details():
    """Example 7: Deep dive into specific awards"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Award Details Deep Dive")
    print("="*80)

    kgq = KnowledgeGraphQuery()

    # Find awards with highest funding
    awards_list = []
    for node, data in kgq.graph.nodes(data=True):
        if data.get('type') == 'Award':
            amount = data.get('amount', '0')
            try:
                amount_float = float(amount) if amount else 0
                awards_list.append((node, amount_float, data))
            except (ValueError, TypeError):
                pass

    awards_list.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 10 Largest Awards:")
    for i, (award_id, amount, data) in enumerate(awards_list[:10], 1):
        details = kgq.get_node_details(award_id)
        print(f"\n{i}. Award ID: {award_id}")
        print(f"   Amount: ${amount:,.2f}")
        print(f"   Title: {data.get('title', 'N/A')[:100]}...")

        # Find the organization
        orgs = [conn['to'] for conn in details['outgoing_connections']
                if conn['relationship'] == 'AWARDED_TO']
        if orgs:
            print(f"   Organization: {orgs[0]}")

        # Find PIs
        pis = [conn['from'] for conn in details['incoming_connections']
               if conn['relationship'] == 'LEADS']
        if pis:
            print(f"   PI: {pis[0]}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("NSF KNOWLEDGE GRAPH - INTERACTIVE EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates various ways to query and analyze the knowledge graph.")
    print("Running all examples...\n")

    try:
        example_1_find_organization_network()
        example_2_analyze_technology_areas()
        example_3_state_comparison()
        example_4_find_collaborations()
        example_5_organization_rankings()
        example_6_custom_subgraph()
        example_7_award_details()

        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETE!")
        print("="*80)
        print("\nGenerated files:")
        print("  - mit_network.html")
        print("  - ai_tech_network.html")
        print("  - california_network.html")
        print("  - technology_analysis.csv")
        print("  - state_analysis.csv")
        print("  - organization_analysis.csv")
        print("\nOpen the HTML files in a browser to explore the interactive visualizations!")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
