"""Mock MCP Server for Denodo Database Access - For Testing/Development.

This is a mock version that returns sample data without requiring a real Denodo database.
Perfect for testing the complete application flow.
"""
import asyncio
import logging
from typing import Any, List, Dict, Optional
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("denodo-mock-server")

# Mock data based on roles
MOCK_ACCOUNTS = {
    "Guest": [
        {
            "account_number": "GUEST-001",
            "client_name": "Demo User",
            "account_type": "Demo Account",
            "account_status": "Active",
            "balance": 0.00,
            "currency": "USD",
            "open_date": "2024-01-01",
            "branch_code": "DEMO",
            "last_updated": "2024-11-09",
            "access_level": "Read-Only",
            "entitlement_roles": ["Guest"]
        }
    ],
    "Admin": [
        {
            "account_number": "ACC-10001",
            "client_name": "John Doe",
            "account_type": "Checking",
            "account_status": "Active",
            "balance": 15000.50,
            "currency": "USD",
            "open_date": "2020-03-15",
            "branch_code": "NYC001",
            "last_updated": "2024-11-09",
            "access_level": "Full Access",
            "entitlement_roles": ["Admin"]
        },
        {
            "account_number": "ACC-10002",
            "client_name": "Jane Smith",
            "account_type": "Savings",
            "account_status": "Active",
            "balance": 45000.75,
            "currency": "USD",
            "open_date": "2019-07-22",
            "branch_code": "NYC001",
            "last_updated": "2024-11-09",
            "access_level": "Full Access",
            "entitlement_roles": ["Admin"]
        },
        {
            "account_number": "ACC-10003",
            "client_name": "Bob Johnson",
            "account_type": "Business",
            "account_status": "Active",
            "balance": 125000.00,
            "currency": "USD",
            "open_date": "2021-01-10",
            "branch_code": "NYC002",
            "last_updated": "2024-11-09",
            "access_level": "Full Access",
            "entitlement_roles": ["Admin"]
        }
    ],
    "Manager": [
        {
            "account_number": "ACC-20001",
            "client_name": "Alice Williams",
            "account_type": "Checking",
            "account_status": "Active",
            "balance": 8500.25,
            "currency": "USD",
            "open_date": "2022-05-18",
            "branch_code": "LA001",
            "last_updated": "2024-11-09",
            "access_level": "Manager Access",
            "entitlement_roles": ["Manager"]
        },
        {
            "account_number": "ACC-20002",
            "client_name": "Charlie Brown",
            "account_type": "Savings",
            "account_status": "Active",
            "balance": 22000.00,
            "currency": "USD",
            "open_date": "2021-11-03",
            "branch_code": "LA001",
            "last_updated": "2024-11-09",
            "access_level": "Manager Access",
            "entitlement_roles": ["Manager"]
        }
    ],
    "Analyst": [
        {
            "account_number": "ACC-30001",
            "client_name": "David Lee",
            "account_type": "Investment",
            "account_status": "Active",
            "balance": 75000.00,
            "currency": "USD",
            "open_date": "2020-09-12",
            "branch_code": "CHI001",
            "last_updated": "2024-11-09",
            "access_level": "Read-Only",
            "entitlement_roles": ["Analyst"]
        }
    ]
}


def get_accounts_for_roles(roles: List[str]) -> List[Dict[str, Any]]:
    """Get mock accounts based on user roles."""
    accounts = []
    
    for role in roles:
        if role in MOCK_ACCOUNTS:
            accounts.extend(MOCK_ACCOUNTS[role])
    
    # If no specific role matches, return guest data
    if not accounts and "Guest" in MOCK_ACCOUNTS:
        accounts.extend(MOCK_ACCOUNTS["Guest"])
    
    return accounts


def apply_filters(
    accounts: List[Dict[str, Any]], 
    filters: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """Apply filters to account list."""
    if not filters:
        return accounts
    
    filtered = accounts.copy()
    
    # Filter by account number
    if "account_number" in filters:
        filtered = [a for a in filtered if a["account_number"] == filters["account_number"]]
    
    # Filter by account status
    if "account_status" in filters:
        filtered = [a for a in filtered if a["account_status"] == filters["account_status"]]
    
    # Filter by minimum balance
    if "min_balance" in filters:
        filtered = [a for a in filtered if a["balance"] >= filters["min_balance"]]
    
    # Limit results
    if "limit" in filters:
        filtered = filtered[:filters["limit"]]
    
    return filtered


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="query_accounts_by_roles",
            description="Query account data based on user entitlement roles. Returns mock data for testing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of user roles from entitlement check"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters (account_number, account_status, min_balance, limit)",
                        "properties": {
                            "account_number": {"type": "string"},
                            "account_status": {"type": "string"},
                            "min_balance": {"type": "number"},
                            "limit": {"type": "integer"}
                        }
                    },
                    "include_balance": {
                        "type": "boolean",
                        "description": "Whether to include balance information",
                        "default": True
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "Whether to include detailed account information",
                        "default": True
                    }
                },
                "required": ["roles"]
            }
        ),
        Tool(
            name="get_account_detail",
            description="Get detailed information for a specific account. Returns mock data for testing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Account number to retrieve details for"
                    },
                    "roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User roles for access validation"
                    }
                },
                "required": ["account_number", "roles"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"🔧 MOCK DENODO: Tool called: {name}")
    logger.info(f"📥 MOCK DENODO: Arguments: {json.dumps(arguments, indent=2)}")
    
    try:
        if name == "query_accounts_by_roles":
            roles = arguments.get("roles", [])
            filters = arguments.get("filters", {})
            include_balance = arguments.get("include_balance", True)
            include_details = arguments.get("include_details", True)
            
            logger.info(f"🔍 MOCK DENODO: Querying accounts for roles: {roles}")
            
            # Get accounts for roles
            accounts = get_accounts_for_roles(roles)
            
            # Apply filters
            accounts = apply_filters(accounts, filters)
            
            # Remove fields if not requested
            if not include_balance:
                for account in accounts:
                    account.pop("balance", None)
                    account.pop("currency", None)
                    account.pop("last_updated", None)
            
            if not include_details:
                for account in accounts:
                    account.pop("client_name", None)
                    account.pop("account_type", None)
                    account.pop("open_date", None)
                    account.pop("branch_code", None)
            
            result = {
                "accounts": accounts,
                "total_count": len(accounts),
                "roles_used": roles,
                "data_source": "mock"
            }
            
            logger.info(f"✅ MOCK DENODO: Returning {len(accounts)} accounts")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_account_detail":
            account_number = arguments.get("account_number")
            roles = arguments.get("roles", [])
            
            logger.info(f"🔍 MOCK DENODO: Getting details for account: {account_number}")
            
            # Get all accounts for roles
            all_accounts = get_accounts_for_roles(roles)
            
            # Find specific account
            account = next(
                (a for a in all_accounts if a["account_number"] == account_number),
                None
            )
            
            if not account:
                result = {
                    "error": f"Account {account_number} not found or not accessible with roles: {roles}",
                    "access_granted": False
                }
            else:
                result = {
                    "account": account,
                    "access_granted": True,
                    "data_source": "mock"
                }
            
            logger.info(f"✅ MOCK DENODO: Account detail retrieved")
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(f"❌ MOCK DENODO: {error_msg}")
            return [TextContent(
                type="text",
                text=json.dumps({"error": error_msg})
            )]
    
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(f"❌ MOCK DENODO: {error_msg}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": error_msg})
        )]


async def main():
    """Run the MCP server."""
    logger.info("🚀 Starting Mock Denodo MCP Server...")
    logger.info("📊 Mock data available for roles: Guest, Admin, Manager, Analyst")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

