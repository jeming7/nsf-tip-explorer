"""
MCP Server for NSF Knowledge Graph
Exposes graph querying tools to Claude via Model Context Protocol
"""

import json
import networkx as nx
from typing import Any, Dict, List
from knowledge_graph import NSFKnowledgeGraph
from query_graph import KnowledgeGraphQuery


class KnowledgeGraphMCPServer:
    """MCP Server that exposes knowledge graph operations as tools"""

    def __init__(self):
        self.kg = NSFKnowledgeGraph()
        self.kg.graph = nx.read_graphml('nsf_knowledge_graph.graphml')
        self.kgq = KnowledgeGraphQuery()
        print("MCP Server initialized with knowledge graph")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools for Claude"""
        return [
            {
                "name": "search_nodes",
                "description": "Search for nodes in the knowledge graph by name or type. Returns matching nodes with their properties.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (partial match on node name)"
                        },
                        "node_type": {
                            "type": "string",
                            "enum": ["Award", "Organization", "Person", "State", "County", "Program", "Technology_Area", ""],
                            "description": "Filter by node type (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_node_details",
                "description": "Get detailed information about a specific node including all its connections and properties.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string",
                            "description": "The exact node ID/name"
                        }
                    },
                    "required": ["node_id"]
                }
            },
            {
                "name": "find_connections",
                "description": "Find all connections (edges) between nodes, optionally filtered by relationship type.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_node": {
                            "type": "string",
                            "description": "Source node ID"
                        },
                        "target_node": {
                            "type": "string",
                            "description": "Target node ID (optional - if not provided, shows all connections from source)"
                        },
                        "relationship_type": {
                            "type": "string",
                            "enum": ["LEADS", "CO_LEADS", "AWARDED_TO", "LOCATED_IN_STATE", "LOCATED_IN_COUNTY", "FUNDED_BY", "INVOLVES_TECH", ""],
                            "description": "Filter by relationship type (optional)"
                        }
                    },
                    "required": ["source_node"]
                }
            },
            {
                "name": "get_organization_stats",
                "description": "Get statistics for all organizations including awards, funding, and researchers. Can filter by minimum thresholds.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "min_awards": {
                            "type": "integer",
                            "description": "Minimum number of awards (optional)",
                            "default": 0
                        },
                        "min_funding": {
                            "type": "number",
                            "description": "Minimum total funding in USD (optional)",
                            "default": 0
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50
                        }
                    }
                }
            },
            {
                "name": "get_technology_stats",
                "description": "Get statistics for all technology areas including award counts and total funding.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "min_awards": {
                            "type": "integer",
                            "description": "Minimum number of awards",
                            "default": 0
                        }
                    }
                }
            },
            {
                "name": "get_state_stats",
                "description": "Get statistics for all states including organizations, awards, and funding.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 55
                        }
                    }
                }
            },
            {
                "name": "find_collaborations",
                "description": "Find people who collaborate with a specific person (share awards).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "person_name": {
                            "type": "string",
                            "description": "Name of the person"
                        }
                    },
                    "required": ["person_name"]
                }
            },
            {
                "name": "query_by_funding_range",
                "description": "Find awards within a specific funding range.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "min_amount": {
                            "type": "number",
                            "description": "Minimum funding amount in USD"
                        },
                        "max_amount": {
                            "type": "number",
                            "description": "Maximum funding amount in USD"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50
                        }
                    },
                    "required": ["min_amount", "max_amount"]
                }
            },
            {
                "name": "get_graph_summary",
                "description": "Get overall statistics about the knowledge graph.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results"""
        try:
            if tool_name == "search_nodes":
                return self._search_nodes(**arguments)
            elif tool_name == "get_node_details":
                return self._get_node_details(**arguments)
            elif tool_name == "find_connections":
                return self._find_connections(**arguments)
            elif tool_name == "get_organization_stats":
                return self._get_organization_stats(**arguments)
            elif tool_name == "get_technology_stats":
                return self._get_technology_stats(**arguments)
            elif tool_name == "get_state_stats":
                return self._get_state_stats(**arguments)
            elif tool_name == "find_collaborations":
                return self._find_collaborations(**arguments)
            elif tool_name == "query_by_funding_range":
                return self._query_by_funding_range(**arguments)
            elif tool_name == "get_graph_summary":
                return self._get_graph_summary()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def _search_nodes(self, query: str, node_type: str = "", limit: int = 20) -> Dict[str, Any]:
        """Search for nodes"""
        query_lower = query.lower()
        results = []

        for node, data in self.kg.graph.nodes(data=True):
            if query_lower in node.lower():
                if not node_type or data.get('type') == node_type:
                    results.append({
                        'id': node,
                        'name': node,
                        'type': data.get('type', 'Unknown'),
                        'properties': {k: v for k, v in data.items() if k != 'type'}
                    })
                    if len(results) >= limit:
                        break

        return {
            "count": len(results),
            "results": results
        }

    def _get_node_details(self, node_id: str) -> Dict[str, Any]:
        """Get detailed node information"""
        if not self.kg.graph.has_node(node_id):
            return {"error": f"Node '{node_id}' not found"}

        return self.kgq.get_node_details(node_id)

    def _find_connections(self, source_node: str, target_node: str = None, relationship_type: str = "") -> Dict[str, Any]:
        """Find connections"""
        if not self.kg.graph.has_node(source_node):
            return {"error": f"Source node '{source_node}' not found"}

        connections = []

        if target_node:
            # Check specific connection
            if self.kg.graph.has_edge(source_node, target_node):
                for key, data in self.kg.graph[source_node][target_node].items():
                    rel = data.get('relationship', 'unknown')
                    if not relationship_type or rel == relationship_type:
                        connections.append({
                            "from": source_node,
                            "to": target_node,
                            "relationship": rel
                        })
        else:
            # Get all outgoing connections
            for neighbor in self.kg.graph.successors(source_node):
                for key, data in self.kg.graph[source_node][neighbor].items():
                    rel = data.get('relationship', 'unknown')
                    if not relationship_type or rel == relationship_type:
                        connections.append({
                            "from": source_node,
                            "to": neighbor,
                            "relationship": rel,
                            "to_type": self.kg.graph.nodes[neighbor].get('type', 'Unknown')
                        })

        return {
            "count": len(connections),
            "connections": connections[:100]  # Limit to prevent overwhelming response
        }

    def _get_organization_stats(self, min_awards: int = 0, min_funding: float = 0, limit: int = 50) -> Dict[str, Any]:
        """Get organization statistics"""
        org_stats = self.kgq.get_organization_statistics()

        filtered = []
        for org, stats in org_stats.items():
            if stats['awards'] >= min_awards and stats['total_funding'] >= min_funding:
                filtered.append({
                    "name": org,
                    "awards": stats['awards'],
                    "total_funding": stats['total_funding'],
                    "researchers": stats['people']
                })

        # Sort by funding
        filtered.sort(key=lambda x: x['total_funding'], reverse=True)

        return {
            "count": len(filtered),
            "organizations": filtered[:limit]
        }

    def _get_technology_stats(self, min_awards: int = 0) -> Dict[str, Any]:
        """Get technology area statistics"""
        tech_stats, tech_funding = self.kgq.get_technology_statistics()

        results = []
        for tech in tech_stats.keys():
            if tech_stats[tech] >= min_awards:
                results.append({
                    "name": tech,
                    "awards": tech_stats[tech],
                    "total_funding": tech_funding[tech],
                    "avg_funding": tech_funding[tech] / tech_stats[tech] if tech_stats[tech] > 0 else 0
                })

        # Sort by awards
        results.sort(key=lambda x: x['awards'], reverse=True)

        return {
            "count": len(results),
            "technologies": results
        }

    def _get_state_stats(self, limit: int = 55) -> Dict[str, Any]:
        """Get state statistics"""
        state_stats = self.kgq.get_state_statistics()

        results = []
        for state, stats in state_stats.items():
            results.append({
                "name": state,
                "organizations": stats['organizations'],
                "awards": stats['awards'],
                "total_funding": stats['total_funding']
            })

        # Sort by funding
        results.sort(key=lambda x: x['total_funding'], reverse=True)

        return {
            "count": len(results),
            "states": results[:limit]
        }

    def _find_collaborations(self, person_name: str) -> Dict[str, Any]:
        """Find collaborators"""
        if not self.kg.graph.has_node(person_name):
            return {"error": f"Person '{person_name}' not found"}

        collaborators = self.kgq.find_collaborations(person_name)

        return {
            "person": person_name,
            "count": len(collaborators),
            "collaborators": collaborators
        }

    def _query_by_funding_range(self, min_amount: float, max_amount: float, limit: int = 50) -> Dict[str, Any]:
        """Find awards in funding range"""
        results = []

        for node, data in self.kg.graph.nodes(data=True):
            if data.get('type') == 'Award':
                try:
                    amount = float(data.get('amount', 0))
                    if min_amount <= amount <= max_amount:
                        results.append({
                            "award_id": node,
                            "amount": amount,
                            "title": data.get('title', 'N/A')
                        })
                except (ValueError, TypeError):
                    pass

        # Sort by amount descending
        results.sort(key=lambda x: x['amount'], reverse=True)

        return {
            "count": len(results),
            "awards": results[:limit]
        }

    def _get_graph_summary(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_counts = {}
        for node, data in self.kg.graph.nodes(data=True):
            node_type = data.get('type', 'Unknown')
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        edge_counts = {}
        for source, target, data in self.kg.graph.edges(data=True):
            rel = data.get('relationship', 'unknown')
            edge_counts[rel] = edge_counts.get(rel, 0) + 1

        return {
            "total_nodes": self.kg.graph.number_of_nodes(),
            "total_edges": self.kg.graph.number_of_edges(),
            "node_types": node_counts,
            "relationship_types": edge_counts
        }


# Global instance
mcp_server = KnowledgeGraphMCPServer()
