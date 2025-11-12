"""
Flask Web Application for NSF Knowledge Graph Explorer
Interactive UI to explore and visualize the knowledge graph
"""

from flask import Flask, render_template, request, jsonify, send_file, session, Response, stream_with_context
import networkx as nx
from knowledge_graph import NSFKnowledgeGraph
from query_graph import KnowledgeGraphQuery
import os
import uuid
import time
import json
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure static directory exists for generated visualizations
os.makedirs('static', exist_ok=True)

# Load the knowledge graph once at startup
print("Loading knowledge graph...")
kg = NSFKnowledgeGraph()
kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')
kgq = KnowledgeGraphQuery()
print("Knowledge graph loaded!")

# Initialize Claude query handler (lazy load)
claude_handler = None
conversation_handlers = {}

# Global progress tracker for visualizations
visualization_progress = {}

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get overall graph statistics"""
    stats = {
        'total_nodes': kg.graph.number_of_nodes(),
        'total_edges': kg.graph.number_of_edges(),
        'node_types': {},
        'edge_types': {}
    }

    # Count node types
    for node, data in kg.graph.nodes(data=True):
        node_type = data.get('type', 'Unknown')
        stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1

    # Count edge types
    for source, target, data in kg.graph.edges(data=True):
        rel = data.get('relationship', 'unknown')
        stats['edge_types'][rel] = stats['edge_types'].get(rel, 0) + 1

    return jsonify(stats)

@app.route('/api/search')
def search():
    """Search for nodes by name"""
    query = request.args.get('q', '').lower()
    node_type = request.args.get('type', None)
    limit = int(request.args.get('limit', 20))

    results = []
    for node, data in kg.graph.nodes(data=True):
        if query in node.lower():
            if node_type is None or data.get('type') == node_type:
                results.append({
                    'id': node,
                    'name': node,
                    'type': data.get('type', 'Unknown')
                })
                if len(results) >= limit:
                    break

    return jsonify(results)

@app.route('/api/node/<path:node_id>')
def get_node_details(node_id):
    """Get detailed information about a specific node"""
    if not kg.graph.has_node(node_id):
        return jsonify({'error': 'Node not found'}), 404

    details = kgq.get_node_details(node_id)
    return jsonify(details)

@app.route('/api/visualize/progress/<job_id>')
def visualization_progress_stream(job_id):
    """Server-sent events endpoint for visualization progress"""
    def generate():
        while True:
            if job_id in visualization_progress:
                progress_data = visualization_progress[job_id]
                yield f"data: {json.dumps(progress_data)}\n\n"

                if progress_data.get('status') in ['complete', 'error']:
                    break
            time.sleep(0.1)

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/visualize', methods=['POST'])
def create_visualization():
    """Create a visualization for a specific node"""
    data = request.json
    center_node = data.get('node')
    depth = int(data.get('depth', 1))

    if not kg.graph.has_node(center_node):
        return jsonify({'error': 'Node not found'}), 404

    # Generate unique job ID and filename
    job_id = str(uuid.uuid4())
    safe_name = center_node.replace('/', '_').replace('\\', '_').replace(' ', '_').replace(',', '')[:50]
    output_file = f"static/viz_{safe_name}_{depth}.html"

    # Initialize progress tracker
    visualization_progress[job_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing...',
        'total_nodes': 0,
        'url': f'/{output_file}'
    }

    # Get node type for better description
    node_type = kg.graph.nodes[center_node].get('type', 'Unknown')

    # Run visualization in background thread
    def run_visualization():
        try:
            # Create visualization with progress callback
            def progress_callback(stage, progress, message, total=None):
                visualization_progress[job_id] = {
                    'status': 'in_progress',
                    'stage': stage,
                    'progress': progress,
                    'message': message,
                    'total_nodes': total or visualization_progress[job_id].get('total_nodes', 0),
                    'url': f'/{output_file}'
                }

            kg.visualize_subgraph_with_progress(
                center_node,
                depth=depth,
                output_file=output_file,
                title=f"{node_type}: {center_node}",
                description=f"Interactive network visualization showing connections at depth {depth}",
                progress_callback=progress_callback
            )

            visualization_progress[job_id] = {
                'status': 'complete',
                'progress': 100,
                'message': 'Visualization complete!',
                'url': f'/{output_file}'
            }
        except Exception as e:
            visualization_progress[job_id] = {
                'status': 'error',
                'progress': 0,
                'message': str(e),
                'url': f'/{output_file}'
            }

    # Start background thread
    thread = threading.Thread(target=run_visualization)
    thread.daemon = True
    thread.start()

    # Return immediately with job ID
    return jsonify({
        'success': True,
        'job_id': job_id,
        'url': f'/{output_file}'
    })

@app.route('/api/organizations')
def get_organizations():
    """Get list of all organizations with statistics"""
    org_stats = kgq.get_organization_statistics()

    orgs = []
    for org, stats in org_stats.items():
        if stats['awards'] > 0:
            orgs.append({
                'name': org,
                'awards': stats['awards'],
                'funding': stats['total_funding'],
                'people': stats['people']
            })

    # Sort by funding
    orgs.sort(key=lambda x: x['funding'], reverse=True)

    return jsonify(orgs[:100])  # Top 100

@app.route('/api/technologies')
def get_technologies():
    """Get list of technology areas with statistics"""
    tech_stats, tech_funding = kgq.get_technology_statistics()

    techs = []
    for tech in tech_stats.keys():
        techs.append({
            'name': tech,
            'awards': tech_stats[tech],
            'funding': tech_funding[tech]
        })

    # Sort by number of awards
    techs.sort(key=lambda x: x['awards'], reverse=True)

    return jsonify(techs)

@app.route('/api/states')
def get_states():
    """Get list of states with statistics"""
    state_stats = kgq.get_state_statistics()

    states = []
    for state, stats in state_stats.items():
        states.append({
            'name': state,
            'organizations': stats['organizations'],
            'awards': stats['awards'],
            'funding': stats['total_funding']
        })

    # Sort by funding
    states.sort(key=lambda x: x['funding'], reverse=True)

    return jsonify(states)

@app.route('/explore')
def explore():
    """Exploration page"""
    return render_template('explore.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    return render_template('analytics.html')

@app.route('/chat')
def chat():
    """AI Chat interface page"""
    return render_template('chat.html')

@app.route('/api/chat/query', methods=['POST'])
def chat_query():
    """Handle natural language queries via Claude"""
    global claude_handler, conversation_handlers

    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400

        user_message = data.get('message', '')
        api_key = data.get('api_key', os.environ.get('ANTHROPIC_API_KEY'))
        conversation_id = data.get('conversation_id')

        if not user_message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required. Please set ANTHROPIC_API_KEY environment variable.'}), 401

        # Create or get conversation handler
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        if conversation_id not in conversation_handlers:
            from claude_query import ClaudeQueryHandler
            conversation_handlers[conversation_id] = ClaudeQueryHandler(api_key=api_key)

        handler = conversation_handlers[conversation_id]

        # Process query
        result = handler.query(user_message)

        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'response': result['response'],
            'tool_uses': result['tool_uses']
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/reset', methods=['POST'])
def chat_reset():
    """Reset conversation history"""
    data = request.json
    conversation_id = data.get('conversation_id')

    if conversation_id and conversation_id in conversation_handlers:
        conversation_handlers[conversation_id].reset_conversation()
        return jsonify({'success': True})

    return jsonify({'error': 'Conversation not found'}), 404

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)

    print("\n" + "="*80)
    print("NSF KNOWLEDGE GRAPH EXPLORER")
    print("="*80)
    print("\nStarting web server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
