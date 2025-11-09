"""MCP Server for Entitlement Profile Checks.

This MCP server provides tools for checking user entitlements
via the profile API.
"""
import asyncio
import logging
import urllib.parse
from typing import Any, Dict, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Profile API configuration
PROFILE_API_URL = "https://localhost:8080/services/security/profile"

# Initialize MCP server
app = Server("entitlement-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="check_user_entitlement",
            description="Check user entitlement and profile from the security API",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username to check (e.g., pe06003)",
                    }
                },
                "required": ["username"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "check_user_entitlement":
        username = arguments.get("username")
        
        if not username:
            logger.error("❌ BACKEND MCP: No username provided")
            return [
                TextContent(
                    type="text",
                    text='{"error": "Username is required"}',
                )
            ]
        
        logger.info(f"🔍 BACKEND MCP: Checking entitlement for username: {username}")
        
        try:
            # Call the profile API
            async with httpx.AsyncClient(verify=False) as client:
                # Prepare form data
                data = {"uuname": username}
                
                logger.info(f"📤 BACKEND MCP: Calling profile API: {PROFILE_API_URL}")
                logger.info(f"📤 BACKEND MCP: Request data: {data}")
                
                response = await client.post(
                    PROFILE_API_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0,
                )
                
                response.raise_for_status()
                profile_data = response.json()
                
                logger.info(f"✅ BACKEND MCP: Profile API Response Status: {response.status_code}")
                logger.info(f"✅ BACKEND MCP: Profile Data Received:")
                logger.info(f"   - Username: {profile_data.get('data', {}).get('profile', {}).get('username')}")
                logger.info(f"   - Email: {profile_data.get('data', {}).get('profile', {}).get('email')}")
                logger.info(f"   - Employee ID: {profile_data.get('data', {}).get('profile', {}).get('employeeId')}")
                logger.info(f"   - Name: {profile_data.get('data', {}).get('profile', {}).get('firstName')} {profile_data.get('data', {}).get('profile', {}).get('lastName')}")
                logger.info(f"   - Roles: {profile_data.get('data', {}).get('profile', {}).get('role')}")
                logger.info(f"   - Status: {profile_data.get('data', {}).get('profile', {}).get('status')}")
                
                return [
                    TextContent(
                        type="text",
                        text=response.text,
                    )
                ]
                
        except httpx.HTTPError as e:
            logger.error(f"❌ BACKEND MCP: HTTP Error calling profile API: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f'{{"error": "HTTP error: {str(e)}"}}',
                )
            ]
        except Exception as e:
            logger.error(f"❌ BACKEND MCP: Unexpected error: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f'{{"error": "Unexpected error: {str(e)}"}}',
                )
            ]
    
    logger.error(f"❌ BACKEND MCP: Unknown tool: {name}")
    return [
        TextContent(
            type="text",
            text=f'{{"error": "Unknown tool: {name}"}}',
        )
    ]


async def main():
    """Run the MCP server."""
    logger.info("🚀 Starting Entitlement MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

