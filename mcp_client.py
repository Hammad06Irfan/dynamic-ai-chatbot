import sys
import json
import asyncio
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientBridge:
    def __init__(self, server_script: str = "mcp_server.py"):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env=None
        )

    async def _async_list_tools(self) -> List[Dict[str, Any]]:
        """Connects over stdio, performs MCP handshake, and converts tools to OpenAI format."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_tools = await session.list_tools()

                openai_tools = []
                for tool in mcp_tools.tools:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema
                        }
                    })
                return openai_tools

    async def _async_call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Executes a tool on the MCP server and returns the deserialized payload."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                
                # Unpack TextContent from tool output
                for content in result.content:
                    if getattr(content, "type", "") == "text":
                        try:
                            return json.loads(content.text)
                        except json.JSONDecodeError:
                            return content.text
                return str(result)

    def get_openai_tools_schema(self) -> List[Dict[str, Any]]:
        """Synchronous wrapper for discovering tool schemas."""
        return asyncio.run(self._async_list_tools())

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Synchronous wrapper for invoking an MCP tool."""
        return asyncio.run(self._async_call_tool(tool_name, arguments))