import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
from collections import defaultdict

class NSFKnowledgeGraph:
    """
    Knowledge Graph for NSF TIP Awards Data

    Entities:
    - Awards
    - People (PI/CoPI)
    - Organizations
    - States
    - Counties
    - Programs
    - Technology Areas

    Relationships:
    - Award -> FUNDED_BY -> Program
    - Award -> INVOLVES_TECH -> Technology Area
    - Person -> LEADS/CO_LEADS -> Award
    - Award -> AWARDED_TO -> Organization
    - Organization -> LOCATED_IN -> State
    - Organization -> LOCATED_IN_COUNTY -> County
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()  # Directed graph with multiple edges
        self.stats = defaultdict(int)

    def load_data(self, excel_file):
        """Load data from Excel file"""
        print(f"Loading data from {excel_file}...")
        self.df = pd.read_excel(excel_file)
        print(f"Loaded {len(self.df)} records")
        return self.df

    def build_graph(self):
        """Build the knowledge graph from the dataframe"""
        print("\nBuilding knowledge graph...")

        for idx, row in self.df.iterrows():
            if idx % 500 == 0:
                print(f"  Processing row {idx}/{len(self.df)}...")

            # Skip rows with missing critical data
            if pd.isna(row['Award ID']):
                continue

            award_id = str(row['Award ID'])

            # Add Award node
            self.add_node(
                award_id,
                node_type='Award',
                title=str(row['Award Title']) if pd.notna(row['Award Title']) else 'N/A',
                amount=row['Total Intended Amount (USD)'],
                award_date=str(row['Award Date']) if pd.notna(row['Award Date']) else 'N/A',
                start_date=str(row['Start Date']) if pd.notna(row['Start Date']) else 'N/A',
                end_date=str(row['End Date']) if pd.notna(row['End Date']) else 'N/A',
                active=str(row['Active']) if pd.notna(row['Active']) else 'N/A',
                url=str(row['Award URL']) if pd.notna(row['Award URL']) else ''
            )

            # Add and connect PI/CoPI
            if pd.notna(row['PI/CoPI']):
                pi_copi_text = str(row['PI/CoPI'])
                people = self._parse_people(pi_copi_text)

                for person, role in people:
                    self.add_node(person, node_type='Person', role=role)
                    self.add_edge(person, award_id, 'LEADS' if role == 'PI' else 'CO_LEADS')

            # Add and connect Organization
            if pd.notna(row['Award Organization']):
                org = str(row['Award Organization'])
                self.add_node(org, node_type='Organization')
                self.add_edge(award_id, org, 'AWARDED_TO')

                # Connect Organization to State
                if pd.notna(row['State']):
                    state = str(row['State'])
                    self.add_node(state, node_type='State')
                    self.add_edge(org, state, 'LOCATED_IN_STATE')

                # Connect Organization to County
                if pd.notna(row['County']):
                    county = str(row['County']) + ', ' + str(row['State']) if pd.notna(row['State']) else str(row['County'])
                    self.add_node(county, node_type='County', state=str(row['State']) if pd.notna(row['State']) else 'N/A')
                    self.add_edge(org, county, 'LOCATED_IN_COUNTY')

            # Add and connect Programs
            if pd.notna(row['TIP Programs']):
                programs = [p.strip() for p in str(row['TIP Programs']).split(';')]
                for program in programs:
                    if program:
                        self.add_node(program, node_type='Program')
                        self.add_edge(award_id, program, 'FUNDED_BY')

            # Add and connect Technology Areas
            if pd.notna(row['Key Technology Areas']):
                tech_areas = [t.strip() for t in str(row['Key Technology Areas']).split(';')]
                for tech in tech_areas:
                    if tech:
                        self.add_node(tech, node_type='Technology_Area')
                        self.add_edge(award_id, tech, 'INVOLVES_TECH')

        print(f"\nGraph construction complete!")
        self._calculate_stats()

    def _parse_people(self, pi_copi_text):
        """Parse PI/CoPI text to extract individuals and their roles"""
        people = []

        # Split by semicolon or common delimiters
        entries = pi_copi_text.split(';')

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Determine role
            role = 'PI'
            if '(CoPI)' in entry or '(Co-PI)' in entry:
                role = 'CoPI'
                entry = entry.replace('(CoPI)', '').replace('(Co-PI)', '').strip()
            elif '(PI)' in entry:
                entry = entry.replace('(PI)', '').strip()

            people.append((entry, role))

        return people

    def add_node(self, node_id, node_type, **attributes):
        """Add a node to the graph"""
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, type=node_type, **attributes)
            self.stats[f'{node_type}_nodes'] += 1

    def add_edge(self, source, target, relationship):
        """Add an edge to the graph (only if this specific relationship doesn't already exist)"""
        # Check if this specific relationship already exists between these nodes
        if self.graph.has_edge(source, target):
            # Check all edges between these nodes for this relationship
            for key, edge_data in self.graph[source][target].items():
                if edge_data.get('relationship') == relationship:
                    return  # Edge with this relationship already exists, skip

        # Add the edge since it doesn't exist
        self.graph.add_edge(source, target, relationship=relationship)
        self.stats[f'{relationship}_edges'] += 1

    def _calculate_stats(self):
        """Calculate and display graph statistics"""
        print("\n" + "="*80)
        print("KNOWLEDGE GRAPH STATISTICS")
        print("="*80)
        print(f"Total Nodes: {self.graph.number_of_nodes()}")
        print(f"Total Edges: {self.graph.number_of_edges()}")
        print("\nNode Counts by Type:")
        for key, value in sorted(self.stats.items()):
            if '_nodes' in key:
                print(f"  {key.replace('_nodes', '')}: {value}")
        print("\nEdge Counts by Relationship:")
        for key, value in sorted(self.stats.items()):
            if '_edges' in key:
                print(f"  {key.replace('_edges', '')}: {value}")
        print("="*80)

    def get_node_info(self, node_id):
        """Get information about a specific node"""
        if not self.graph.has_node(node_id):
            return None

        node_data = self.graph.nodes[node_id]
        neighbors_out = list(self.graph.successors(node_id))
        neighbors_in = list(self.graph.predecessors(node_id))

        return {
            'id': node_id,
            'data': node_data,
            'connections_out': len(neighbors_out),
            'connections_in': len(neighbors_in),
            'neighbors_out': neighbors_out[:10],  # First 10
            'neighbors_in': neighbors_in[:10]  # First 10
        }

    def query_by_type(self, node_type, limit=10):
        """Query nodes by type"""
        nodes = [(n, d) for n, d in self.graph.nodes(data=True) if d.get('type') == node_type]
        return nodes[:limit]

    def find_paths(self, source, target, max_length=3):
        """Find paths between two nodes"""
        try:
            paths = list(nx.all_simple_paths(self.graph, source, target, cutoff=max_length))
            return paths
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def get_subgraph(self, center_node, depth=1):
        """Extract a subgraph around a center node

        Note: State and County nodes are included in the visualization but we don't
        traverse through them. This prevents pulling in all organizations from the
        same state/county that have no meaningful connection to the center node.
        """
        if not self.graph.has_node(center_node):
            return None

        nodes = {center_node}
        current_level = {center_node}

        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Add neighbors (both successors and predecessors)
                neighbors = set(self.graph.successors(node)) | set(self.graph.predecessors(node))

                for neighbor in neighbors:
                    next_level.add(neighbor)

                    # If the neighbor is a State or County, include it but DON'T traverse through it
                    neighbor_type = self.graph.nodes[neighbor].get('type')
                    if neighbor_type in ['State', 'County']:
                        # Add to nodes but NOT to current_level for next iteration
                        nodes.add(neighbor)
                        next_level.discard(neighbor)  # Remove from next_level to prevent traversal

            nodes.update(next_level)
            current_level = next_level

        return self.graph.subgraph(nodes).copy()

    def save_graph(self, filename='nsf_knowledge_graph.graphml'):
        """Save graph to GraphML format"""
        print(f"\nSaving graph to {filename}...")
        nx.write_graphml(self.graph, filename)
        print(f"Graph saved successfully!")

    def export_statistics(self, filename='graph_statistics.json'):
        """Export graph statistics to JSON"""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_counts': {k.replace('_nodes', ''): v for k, v in self.stats.items() if '_nodes' in k},
            'edge_counts': {k.replace('_edges', ''): v for k, v in self.stats.items() if '_edges' in k},
            'density': nx.density(self.graph)
        }

        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\nStatistics exported to {filename}")
        return stats

    def visualize_subgraph(self, center_node, depth=1, output_file='subgraph.html', title=None, description=None):
        """Create an interactive visualization of a subgraph"""
        subgraph = self.get_subgraph(center_node, depth)

        if subgraph is None or subgraph.number_of_nodes() == 0:
            print(f"No subgraph found for node: {center_node}")
            return

        print(f"\nGenerating visualization for subgraph with {subgraph.number_of_nodes()} nodes...")

        # Count node types and edges in subgraph
        node_type_counts = defaultdict(int)
        edge_type_counts = defaultdict(int)
        for node, data in subgraph.nodes(data=True):
            node_type_counts[data.get('type', 'Unknown')] += 1
        for source, target, data in subgraph.edges(data=True):
            edge_type_counts[data.get('relationship', 'unknown')] += 1

        # Create pyvis network
        net = Network(height='750px', width='100%', directed=True, notebook=False)
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=100)

        # Set heading if provided
        if title:
            net.heading = title

        # Color mapping for node types
        color_map = {
            'Award': '#FF6B6B',
            'Person': '#4ECDC4',
            'Organization': '#45B7D1',
            'State': '#96CEB4',
            'County': '#FFEAA7',
            'Program': '#DFE6E9',
            'Technology_Area': '#A29BFE'
        }

        # Add nodes
        for node, data in subgraph.nodes(data=True):
            node_type = data.get('type', 'Unknown')
            color = color_map.get(node_type, '#95A5A6')

            # Create label and tooltip (not to be confused with the visualization title parameter)
            if node_type == 'Award':
                label = f"Award: {node[:15]}..."
                node_tooltip = f"<b>Award ID:</b> {node}<br><b>Title:</b> {data.get('title', 'N/A')[:100]}...<br><b>Amount:</b> ${data.get('amount', 0):,.2f}"
            else:
                label = node if len(node) < 30 else node[:27] + '...'
                node_tooltip = f"<b>{node_type}:</b> {node}"

            size = 30 if node == center_node else (20 if node_type == 'Award' else 15)
            net.add_node(node, label=label, title=node_tooltip, color=color, size=size)

        # Add edges
        for source, target, data in subgraph.edges(data=True):
            relationship = data.get('relationship', '')
            net.add_edge(source, target, title=relationship, label=relationship)

        # Save and add custom HTML header
        net.save_graph(output_file)

        # Add informative header to the HTML file
        self._add_info_header(output_file, center_node, subgraph, node_type_counts, edge_type_counts, title, description)

        print(f"Visualization saved to {output_file}")
        print(f"Open this file in a web browser to view the interactive graph!")

    def visualize_subgraph_with_progress(self, center_node, depth=1, output_file='subgraph.html', title=None, description=None, progress_callback=None):
        """Create an interactive visualization of a subgraph with progress updates"""

        # Stage 1: Extract subgraph
        if progress_callback:
            progress_callback('extract', 10, 'Extracting subgraph...', None)

        subgraph = self.get_subgraph(center_node, depth)

        if subgraph is None or subgraph.number_of_nodes() == 0:
            if progress_callback:
                progress_callback('error', 0, 'No subgraph found', None)
            return

        total_nodes = subgraph.number_of_nodes()

        if progress_callback:
            progress_callback('extract', 30, f'Extracted {total_nodes} nodes', total_nodes)

        # Stage 2: Count node types and edges
        if progress_callback:
            progress_callback('analyze', 40, 'Analyzing graph structure...', total_nodes)

        node_type_counts = defaultdict(int)
        edge_type_counts = defaultdict(int)
        for node, data in subgraph.nodes(data=True):
            node_type_counts[data.get('type', 'Unknown')] += 1
        for source, target, data in subgraph.edges(data=True):
            edge_type_counts[data.get('relationship', 'unknown')] += 1

        # Stage 3: Create network visualization
        if progress_callback:
            progress_callback('create', 50, 'Creating network visualization...', total_nodes)

        net = Network(height='750px', width='100%', directed=True, notebook=False)
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=100)

        if title:
            net.heading = title

        # Color mapping for node types
        color_map = {
            'Award': '#FF6B6B',
            'Person': '#4ECDC4',
            'Organization': '#45B7D1',
            'State': '#96CEB4',
            'County': '#FFEAA7',
            'Program': '#DFE6E9',
            'Technology_Area': '#A29BFE'
        }

        # Stage 4: Add nodes
        if progress_callback:
            progress_callback('nodes', 60, 'Adding nodes to visualization...', total_nodes)

        for i, (node, data) in enumerate(subgraph.nodes(data=True)):
            node_type = data.get('type', 'Unknown')
            color = color_map.get(node_type, '#95A5A6')

            if node_type == 'Award':
                label = f"Award: {node[:15]}..."
                node_tooltip = f"<b>Award ID:</b> {node}<br><b>Title:</b> {data.get('title', 'N/A')[:100]}...<br><b>Amount:</b> ${data.get('amount', 0):,.2f}"
            else:
                label = node if len(node) < 30 else node[:27] + '...'
                node_tooltip = f"<b>{node_type}:</b> {node}"

            size = 30 if node == center_node else (20 if node_type == 'Award' else 15)
            net.add_node(node, label=label, title=node_tooltip, color=color, size=size)

            # Update progress every 50 nodes
            if i % 50 == 0 and progress_callback:
                progress_percent = 60 + int((i / total_nodes) * 15)
                progress_callback('nodes', progress_percent, f'Adding nodes... ({i}/{total_nodes})', total_nodes)

        # Stage 5: Add edges
        if progress_callback:
            progress_callback('edges', 75, 'Adding connections...', total_nodes)

        total_edges = subgraph.number_of_edges()
        for i, (source, target, data) in enumerate(subgraph.edges(data=True)):
            relationship = data.get('relationship', '')
            net.add_edge(source, target, title=relationship, label=relationship)

            # Update progress every 100 edges
            if i % 100 == 0 and progress_callback:
                progress_percent = 75 + int((i / max(total_edges, 1)) * 15)
                progress_callback('edges', progress_percent, f'Adding edges... ({i}/{total_edges})', total_nodes)

        # Stage 6: Save graph
        if progress_callback:
            progress_callback('save', 90, 'Saving visualization...', total_nodes)

        net.save_graph(output_file)

        # Stage 7: Add header
        if progress_callback:
            progress_callback('finalize', 95, 'Finalizing...', total_nodes)

        self._add_info_header(output_file, center_node, subgraph, node_type_counts, edge_type_counts, title, description)

        if progress_callback:
            progress_callback('complete', 100, 'Complete!', total_nodes)

    def _add_info_header(self, html_file, center_node, subgraph, node_counts, edge_counts, title, description):
        """Add an informative header to the HTML visualization"""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Get center node type
        center_type = subgraph.nodes[center_node].get('type', 'Unknown') if center_node in subgraph.nodes else 'Unknown'

        # Default title and description if not provided
        if not title:
            title = f"Knowledge Graph: {center_node}"
        if not description:
            description = f"Interactive network visualization centered on {center_type}: <strong>{center_node}</strong>"

        # HTML escape the title and description to prevent injection
        import html
        title = html.escape(title)
        # Description can have HTML tags, but escape quotes
        description = description.replace('"', '&quot;')

        # Create info panel HTML
        info_html = f"""
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        margin: 0;
        padding: 0;
    }}
    #mynetwork {{
        margin-top: 0 !important;
    }}
    .info-panel {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .info-panel h1 {{
        margin: 0 0 10px 0;
        font-size: 28px;
        font-weight: 600;
    }}
    .info-panel p {{
        margin: 5px 0;
        font-size: 14px;
        opacity: 0.95;
        line-height: 1.5;
    }}
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.3);
    }}
    .stat-box {{
        background: rgba(255,255,255,0.15);
        padding: 12px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }}
    .stat-label {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.8;
        margin-bottom: 5px;
    }}
    .stat-value {{
        font-size: 20px;
        font-weight: 700;
    }}
    .legend {{
        background: #f8f9fa;
        padding: 15px 30px;
        border-bottom: 1px solid #dee2e6;
        font-size: 13px;
    }}
    .legend-title {{
        font-weight: 600;
        margin-bottom: 10px;
        color: #495057;
    }}
    .legend-items {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .legend-color {{
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid #dee2e6;
    }}
    .instructions {{
        background: #e7f3ff;
        padding: 12px 30px;
        border-left: 4px solid #0066cc;
        font-size: 13px;
        color: #004085;
    }}
    .instructions strong {{
        color: #002752;
    }}
</style>

<div class="info-panel">
    <h1>{title}</h1>
    <p>{description}</p>

    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-label">Total Nodes</div>
            <div class="stat-value">{subgraph.number_of_nodes()}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Total Connections</div>
            <div class="stat-value">{subgraph.number_of_edges()}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Center Node</div>
            <div class="stat-value" style="font-size: 14px; line-height: 1.3;">{center_node[:40]}{'...' if len(center_node) > 40 else ''}</div>
        </div>
    </div>
</div>

<div class="legend">
    <div class="legend-title">Node Types ({len(node_counts)} types, {subgraph.number_of_nodes()} total)</div>
    <div class="legend-items">
        <div class="legend-item">
            <div class="legend-color" style="background-color: #FF6B6B;"></div>
            <span><strong>Awards</strong> - NSF grant awards ({node_counts.get('Award', 0)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #4ECDC4;"></div>
            <span><strong>People</strong> - PIs and Co-PIs ({node_counts.get('Person', 0)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #45B7D1;"></div>
            <span><strong>Organizations</strong> - Institutions ({node_counts.get('Organization', 0)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #96CEB4;"></div>
            <span><strong>States</strong> - US States ({node_counts.get('State', 0)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #FFEAA7;"></div>
            <span><strong>Counties</strong> - Geographic regions ({node_counts.get('County', 0)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #DFE6E9;"></div>
            <span><strong>Programs</strong> - NSF funding programs ({node_counts.get('Program', 0)})</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #A29BFE;"></div>
            <span><strong>Technology Areas</strong> - Tech focus ({node_counts.get('Technology_Area', 0)})</span>
        </div>
    </div>
</div>

<div class="instructions">
    <strong>How to interact:</strong> Click and drag nodes to rearrange • Zoom with mouse wheel • Hover over nodes for details • Click to highlight connections • Drag background to pan
</div>
"""

        # Remove ALL PyVis-generated title elements (both in head and body sections)
        import re
        # Remove all <center><h1>...</h1></center> blocks (PyVis adds multiple of these)
        html_content = re.sub(r'<center>\s*<h1[^>]*>.*?</h1>\s*</center>\s*', '', html_content, flags=re.DOTALL)

        # Insert the info panel right after the body tag
        html_content = html_content.replace('<body>', '<body>\n' + info_html, 1)

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


# Main execution
if __name__ == "__main__":
    # Create knowledge graph
    kg = NSFKnowledgeGraph()

    # Load data
    df = kg.load_data('nsf-awards-export-2025-11-07.xlsx')

    # Build graph
    kg.build_graph()

    # Save graph
    kg.save_graph()

    # Export statistics
    kg.export_statistics()

    # Example queries
    print("\n" + "="*80)
    print("SAMPLE QUERIES")
    print("="*80)

    # Query organizations
    print("\nTop 10 Organizations:")
    orgs = kg.query_by_type('Organization', limit=10)
    for i, (org, data) in enumerate(orgs, 1):
        print(f"  {i}. {org}")

    # Query technology areas
    print("\nTop 10 Technology Areas:")
    techs = kg.query_by_type('Technology_Area', limit=10)
    for i, (tech, data) in enumerate(techs, 1):
        print(f"  {i}. {tech}")

    # Create sample visualization
    if orgs:
        sample_org = orgs[0][0]
        print(f"\nCreating sample visualization for: {sample_org}")
        kg.visualize_subgraph(sample_org, depth=2, output_file='sample_organization_network.html')

    print("\n" + "="*80)
    print("Knowledge Graph Builder Complete!")
    print("="*80)
    print("\nGenerated files:")
    print("  - nsf_knowledge_graph.graphml (graph data)")
    print("  - graph_statistics.json (statistics)")
    print("  - sample_organization_network.html (interactive visualization)")
