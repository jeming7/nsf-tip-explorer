# NSF Knowledge Graph Explorer - Web Application

A full-featured web interface to explore and visualize the NSF TIP awards knowledge graph.

## 🚀 Quick Start

### 1. Configure API Key

Create or edit the `.env` file and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

Get your API key from: https://console.anthropic.com/

### 2. Run the Application

```bash
cd TIP_KG
python app.py
```

Then open your browser to: **http://localhost:5000**

## 📋 Features

### 1. Home Page (`/`)
- **Overview Statistics**: Total nodes, edges, organizations, and awards
- **Smart Search**: Search across all node types with real-time filtering
- **Quick Actions**: Navigate to different sections of the app
- **Pre-made Visualizations**: Access curated network views

### 2. Explore Page (`/explore`)
- **Browse by Category**:
  - Organizations (sorted by funding)
  - Technology Areas (sorted by # of awards)
  - States (sorted by funding)
- **Live Filtering**: Filter lists in real-time
- **Node Details**: Click any item to see:
  - Node properties
  - Incoming and outgoing connections
  - Related entities
- **Interactive Visualization**: Generate network graphs at depth 1 or 2
- **Embedded Viewer**: View visualizations directly in the browser

### 3. Analytics Dashboard (`/analytics`)
- **Top Organizations Rankings**:
  - By funding amount
  - By number of awards
  - By number of researchers
- **Technology Area Statistics**:
  - Award counts
  - Funding totals
  - Average award sizes
- **State-by-State Comparison**:
  - Organization counts
  - Award totals
  - Funding distribution
- **Interactive Charts**: Bar charts showing top 10 in each category

### 4. AI Chat Assistant (`/chat`) 🤖
- **Natural Language Queries**: Ask questions in plain English
- **Powered by Claude AI**: Uses Model Context Protocol (MCP) for intelligent responses
- **9 Knowledge Graph Tools**:
  - Search nodes by name or type
  - Get detailed node information
  - Find connections between entities
  - Organization, technology, and state statistics
  - Find collaborations between researchers
  - Query by funding range
  - Get graph summary
- **Conversational Interface**: Multi-turn conversations with context
- **Example Queries**:
  - "What are the top 10 organizations by funding?"
  - "Which states have the most AI research?"
  - "Tell me about MIT's research portfolio"
  - "Find collaborations between researchers in quantum computing"

## 🔌 API Endpoints

The application provides a REST API for programmatic access:

### GET `/api/stats`
Returns overall graph statistics.

```json
{
  "total_nodes": 16912,
  "total_edges": 31538,
  "node_types": {...},
  "edge_types": {...}
}
```

### GET `/api/search?q=<query>&type=<node_type>&limit=<n>`
Search for nodes by name.

**Parameters:**
- `q`: Search query (required)
- `type`: Filter by node type (optional)
- `limit`: Max results (default: 20)

### GET `/api/node/<node_id>`
Get detailed information about a specific node.

Returns:
- Node properties
- Incoming connections
- Outgoing connections

### POST `/api/visualize`
Create a new visualization.

**Body:**
```json
{
  "node": "Massachusetts Institute of Technology",
  "depth": 2
}
```

**Returns:**
```json
{
  "success": true,
  "url": "/static/viz_Massachusetts_Institute_of_Techno_2.html"
}
```

### GET `/api/organizations`
Get top 100 organizations with statistics.

### GET `/api/technologies`
Get all technology areas with award counts and funding.

### GET `/api/states`
Get all states with organization counts, awards, and funding.

## 🎨 Key Features

### Smart Graph Traversal
- Stops at State/County nodes to prevent irrelevant organization inclusion
- Depth 1: Immediate neighbors only (fast)
- Depth 2: Extended network (detailed)

### Real-time Visualization Generation
- Generates custom visualizations on demand
- Includes interactive legends and statistics
- Color-coded by node type
- Physics-based layout

### Responsive Design
- Mobile-friendly interface
- Smooth animations and transitions
- Modern gradient design

## 📁 Project Structure

```
TIP_KG/
├── app.py                      # Flask application
├── templates/
│   ├── index.html             # Home page
│   ├── explore.html           # Exploration interface
│   └── analytics.html         # Analytics dashboard
├── static/                    # Generated visualizations
├── knowledge_graph.py         # Graph building logic
├── query_graph.py             # Query utilities
└── nsf_knowledge_graph.graphml # Graph data
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Graph Library**: NetworkX
- **Visualization**: PyVis
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Charts**: Chart.js
- **Data Format**: GraphML

## 💡 Usage Examples

### Example 1: Find MIT's Research Network
1. Go to http://localhost:5000/explore
2. In the Organizations tab, search for "MIT" or scroll to find it
3. Click on "Massachusetts Institute of Technology"
4. Click "Depth 2 (Detailed)" to see the full research ecosystem
5. Explore the interactive visualization

### Example 2: Compare Technology Areas
1. Go to http://localhost:5000/analytics
2. View the "Top Technology Areas" table
3. See which technologies receive the most funding
4. Check the bar chart for visual comparison

### Example 3: Search for Specific Award
1. Go to http://localhost:5000
2. Type an award ID or keyword in the search box
3. Select "Awards" from the type filter
4. Click on a result to view details

## 🔧 Configuration

Edit `app.py` to customize:

- **Port**: Change `port=5000` in `app.run()`
- **Host**: Change `host='0.0.0.0'` to restrict access
- **Debug Mode**: Set `debug=False` for production

## 📊 Performance Tips

1. **Use Depth 1 for large nodes**: California, AI, etc.
2. **Pre-generated visualizations**: Access via Home → Pre-made Visualizations
3. **Filter before exploring**: Use the filter box to narrow results
4. **API for batch operations**: Use REST API for programmatic access

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Kill the existing process or change the port in app.py
```

**Visualizations not loading:**
- Check that the `static/` directory exists
- Ensure the knowledge graph file is present
- Check browser console for errors

**Slow performance:**
- Use depth=1 for initial exploration
- Close unused visualizations
- Restart the server to free memory

## 🎯 Future Enhancements

Potential additions:
- Export data to CSV/JSON
- Collaboration network analysis
- Time-series funding trends
- Geographic heatmaps
- Advanced filtering (funding range, date range)
- User accounts and saved queries
- Graph comparison tools

## 📝 License

Built for NSF TIP awards analysis. Data sourced from NSF public records.
