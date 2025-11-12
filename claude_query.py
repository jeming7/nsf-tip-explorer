"""
Claude API Integration for Natural Language Queries
Handles communication between user queries and the knowledge graph via MCP
"""

import os
import json
from anthropic import Anthropic
from mcp_server import mcp_server


class ClaudeQueryHandler:
    """Handles natural language queries using Claude with MCP tools"""

    def __init__(self, api_key: str = None):
        """Initialize Claude client"""
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-haiku-4-20250923"
        self.conversation_history = []

        # System prompt that explains the knowledge graph
        self.system_prompt = """You are an AI assistant helping users explore the NSF TIP (Technology Innovation Partnership) Awards Knowledge Graph.

The knowledge graph contains:
- 5,515 NSF TIP awards with funding information
- 2,738 organizations receiving awards
- 7,701 researchers (PIs and Co-PIs)
- 55 US states and 497 counties
- 14 NSF programs
- 394 technology areas

Node Types:
- Award: NSF grant awards with amount, title, dates
- Organization: Institutions receiving awards
- Person: PIs and Co-PIs leading research
- State: US States
- County: Geographic regions
- Program: NSF funding programs
- Technology_Area: Tech focus areas

Relationships:
- LEADS / CO_LEADS: Person → Award
- AWARDED_TO: Award → Organization
- LOCATED_IN_STATE: Organization → State
- LOCATED_IN_COUNTY: Organization → County
- FUNDED_BY: Award → Program
- INVOLVES_TECH: Award → Technology_Area

You have access to tools that can query this graph. When users ask questions:
1. Use the appropriate tools to fetch data
2. Analyze the results
3. Provide clear, insightful answers
4. Suggest follow-up questions when relevant
5. Format numbers with proper units (e.g., $1.2M instead of 1200000)

Be conversational and helpful. If data is ambiguous, ask clarifying questions."""

    def query(self, user_message: str, conversation_id: str = None) -> dict:
        """
        Process a user query and return response

        Args:
            user_message: The user's natural language query
            conversation_id: Optional ID to maintain conversation context

        Returns:
            dict with 'response', 'tool_uses', and 'conversation_id'
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Initial API call
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.conversation_history,
            tools=mcp_server.get_tools()
        )

        tool_uses = []
        assistant_response = ""

        # Process response and handle tool use
        while response.stop_reason == "tool_use":
            # Extract assistant content and tool uses
            assistant_content = []
            current_tools = []

            for block in response.content:
                if block.type == "text":
                    assistant_response += block.text
                    assistant_content.append(block)
                elif block.type == "tool_use":
                    current_tools.append(block)
                    assistant_content.append(block)

            # Add assistant message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_content
            })

            # Execute tools and collect results
            tool_results = []
            for tool_use in current_tools:
                tool_name = tool_use.name
                tool_input = tool_use.input

                print(f"[MCP] Executing tool: {tool_name}")
                print(f"[MCP] Input: {json.dumps(tool_input, indent=2)}")

                # Execute tool via MCP server
                result = mcp_server.execute_tool(tool_name, tool_input)

                print(f"[MCP] Result: {json.dumps(result, indent=2)[:500]}...")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result)
                })

                tool_uses.append({
                    "name": tool_name,
                    "input": tool_input,
                    "result": result
                })

            # Add tool results to history
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            # Continue conversation with tool results
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.conversation_history,
                tools=mcp_server.get_tools()
            )

        # Extract final response
        for block in response.content:
            if block.type == "text":
                assistant_response += block.text

        # Add final assistant response to history
        if response.stop_reason == "end_turn":
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

        return {
            "response": assistant_response,
            "tool_uses": tool_uses,
            "stop_reason": response.stop_reason
        }

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


# Example usage
if __name__ == "__main__":
    # Test queries
    import sys

    if len(sys.argv) < 2:
        print("Usage: python claude_query.py <api_key>")
        sys.exit(1)

    handler = ClaudeQueryHandler(api_key=sys.argv[1])

    test_queries = [
        "What are the top 5 organizations by funding?",
        "Which states have the most NSF TIP awards?",
        "Tell me about MIT's research portfolio"
    ]

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)

        result = handler.query(query)

        print(f"\nResponse: {result['response']}")
        print(f"\nTools used: {len(result['tool_uses'])}")
        for tool in result['tool_uses']:
            print(f"  - {tool['name']}")
