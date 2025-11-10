"""
Simple HTTP server to view visualizations
Run this script and open http://localhost:8000 in your browser
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000

# Change to the TIP_KG directory
os.chdir(Path(__file__).parent)

Handler = http.server.SimpleHTTPRequestHandler

print("="*80)
print("NSF Knowledge Graph Visualization Server")
print("="*80)
print(f"\nStarting server on port {PORT}...")
print(f"Server running at: http://localhost:{PORT}")
print("\nAvailable visualizations:")
print(f"  - http://localhost:{PORT}/mit_network.html")
print(f"  - http://localhost:{PORT}/ai_tech_network.html")
print(f"  - http://localhost:{PORT}/california_network.html")
print(f"  - http://localhost:{PORT}/sample_organization_network.html")
print("\nPress Ctrl+C to stop the server")
print("="*80)

# Try to open browser automatically
try:
    webbrowser.open(f'http://localhost:{PORT}/mit_network.html')
    print("\n[OK] Opening MIT network visualization in your default browser...")
except:
    print("\nCouldn't open browser automatically. Please open the URL manually.")

# Start server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        print("="*80)
