"""MCP Server for Denodo Database Access with Role-Based Query Generation.

This MCP server connects to Denodo and executes dynamically generated
queries based on user entitlement roles.
"""
import asyncio
import logging
from typing import Any, List, Dict, Optional
import json

# For Denodo connection
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Denodo Configuration
DENODO_URL = "http://localhost:9090/denodo-restfulws"  # REST API endpoint
DENODO_DATABASE = "your_database"
DENODO_USERNAME = "admin"
DENODO_PASSWORD = "admin"

# Initialize MCP server
app = Server("denodo-server")


class QueryBuilder:
    """Dynamic SQL query builder for Denodo based on roles."""
    
    @staticmethod
    def build_accounts_query(
        roles: List[str],
        filters: Optional[Dict] = None,
        include_balance: bool = True,
        include_details: bool = True
    ) -> str:
        """
        Build dynamic SQL query based on entitlement roles.
        
        Args:
            roles: List of entitlement roles
            filters: Additional filters (account_number, date_range, etc.)
            include_balance: Include RPBT0200 balance data
            include_details: Include RPBT0100 detail data
            
        Returns:
            SQL query string
        """
        # Base query
        query_parts = []
        
        # SELECT clause
        select_fields = [
            "r1.account_number",
            "r1.entitlement_roles",
            "r1.account_status"
        ]
        
        if include_details:
            select_fields.extend([
                "r2.client_name",
                "r2.account_type",
                "r2.open_date",
                "r2.branch_code"
            ])
        
        if include_balance:
            select_fields.extend([
                "r3.balance",
                "r3.currency",
                "r3.last_updated"
            ])
        
        query_parts.append(f"SELECT {', '.join(select_fields)}")
        
        # FROM clause with JOINs
        query_parts.append("FROM RCAT0300 r1")
        
        if include_details:
            query_parts.append(
                "INNER JOIN RPBT0100 r2 ON r1.account_number = r2.account_number"
            )
        
        if include_balance:
            query_parts.append(
                "INNER JOIN RPBT0200 r3 ON r1.account_number = r3.account_number"
            )
        
        # WHERE clause for role-based filtering
        where_conditions = []
        
        # Role-based filtering
        if roles:
            # Match any of the user's roles with the entitlement_roles in table
            role_conditions = " OR ".join([
                f"r1.entitlement_roles LIKE '%{role}%'" 
                for role in roles
            ])
            where_conditions.append(f"({role_conditions})")
        
        # Additional filters
        if filters:
            if filters.get("account_number"):
                where_conditions.append(
                    f"r1.account_number = '{filters['account_number']}'"
                )
            
            if filters.get("account_status"):
                where_conditions.append(
                    f"r1.account_status = '{filters['account_status']}'"
                )
            
            if filters.get("min_balance"):
                if include_balance:
                    where_conditions.append(
                        f"r3.balance >= {filters['min_balance']}"
                    )
            
            if filters.get("account_type"):
                if include_details:
                    where_conditions.append(
                        f"r2.account_type = '{filters['account_type']}'"
                    )
        
        # Add WHERE clause if conditions exist
        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))
        
        # ORDER BY
        query_parts.append("ORDER BY r1.account_number")
        
        # LIMIT (optional)
        if filters and filters.get("limit"):
            query_parts.append(f"LIMIT {filters['limit']}")
        
        return " ".join(query_parts)
    
    @staticmethod
    def build_summary_query(roles: List[str]) -> str:
        """Build query for account summary by roles."""
        role_conditions = " OR ".join([
            f"entitlement_roles LIKE '%{role}%'" 
            for role in roles
        ])
        
        return f"""
        SELECT 
            COUNT(DISTINCT r1.account_number) as total_accounts,
            SUM(r3.balance) as total_balance,
            COUNT(DISTINCT r2.client_name) as total_clients,
            r1.entitlement_roles
        FROM RCAT0300 r1
        INNER JOIN RPBT0100 r2 ON r1.account_number = r2.account_number
        INNER JOIN RPBT0200 r3 ON r1.account_number = r3.account_number
        WHERE ({role_conditions})
        GROUP BY r1.entitlement_roles
        """
    
    @staticmethod
    def build_account_detail_query(account_number: str, roles: List[str]) -> str:
        """Build query for specific account detail (with role verification)."""
        role_conditions = " OR ".join([
            f"r1.entitlement_roles LIKE '%{role}%'" 
            for role in roles
        ])
        
        return f"""
        SELECT 
            r1.account_number,
            r1.entitlement_roles,
            r1.account_status,
            r2.client_name,
            r2.account_type,
            r2.open_date,
            r2.branch_code,
            r3.balance,
            r3.currency,
            r3.last_updated
        FROM RCAT0300 r1
        INNER JOIN RPBT0100 r2 ON r1.account_number = r2.account_number
        INNER JOIN RPBT0200 r3 ON r1.account_number = r3.account_number
        WHERE r1.account_number = '{account_number}'
        AND ({role_conditions})
        """


async def execute_denodo_query(query: str) -> Dict:
    """
    Execute query against Denodo using REST API.
    
    Args:
        query: SQL query to execute
        
    Returns:
        Query results as dictionary
    """
    try:
        logger.info(f"📤 DENODO MCP: Executing query")
        logger.info(f"📝 DENODO MCP: Query: {query[:200]}...")
        
        # Using Denodo REST API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{DENODO_URL}/{DENODO_DATABASE}/views",
                auth=(DENODO_USERNAME, DENODO_PASSWORD),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "sql": query,
                    "$format": "json"
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ DENODO MCP: Query executed successfully")
            logger.info(f"📊 DENODO MCP: Returned {len(result.get('elements', []))} rows")
            
            return result
            
    except Exception as e:
        logger.error(f"❌ DENODO MCP: Query execution failed: {str(e)}")
        raise


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Denodo tools."""
    return [
        Tool(
            name="query_accounts_by_roles",
            description="Query account data from Denodo based on entitlement roles. Dynamically joins RCAT0300, RPBT0100, and RPBT0200 tables.",
            inputSchema={
                "type": "object",
                "properties": {
                    "roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of entitlement roles from entitlement_mcp"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Additional filters",
                        "properties": {
                            "account_number": {"type": "string"},
                            "account_status": {"type": "string"},
                            "account_type": {"type": "string"},
                            "min_balance": {"type": "number"},
                            "limit": {"type": "integer"}
                        }
                    },
                    "include_balance": {
                        "type": "boolean",
                        "description": "Include balance data from RPBT0200",
                        "default": True
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "Include account details from RPBT0100",
                        "default": True
                    }
                },
                "required": ["roles"]
            }
        ),
        Tool(
            name="get_account_summary",
            description="Get summary statistics of accounts accessible by roles",
            inputSchema={
                "type": "object",
                "properties": {
                    "roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of entitlement roles"
                    }
                },
                "required": ["roles"]
            }
        ),
        Tool(
            name="get_account_detail",
            description="Get detailed information for a specific account (with role verification)",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Account number to query"
                    },
                    "roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User's entitlement roles"
                    }
                },
                "required": ["account_number", "roles"]
            }
        ),
        Tool(
            name="execute_custom_query",
            description="Execute a custom SQL query (advanced users only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Custom SQL query"
                    },
                    "roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User roles for validation"
                    }
                },
                "required": ["query", "roles"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle Denodo MCP tool calls."""
    
    try:
        if name == "query_accounts_by_roles":
            roles = arguments.get("roles", [])
            filters = arguments.get("filters", {})
            include_balance = arguments.get("include_balance", True)
            include_details = arguments.get("include_details", True)
            
            if not roles:
                return [TextContent(
                    type="text",
                    text='{"error": "Roles are required"}'
                )]
            
            logger.info(f"🔍 DENODO MCP: Querying accounts for roles: {roles}")
            
            # Build dynamic query
            query = QueryBuilder.build_accounts_query(
                roles=roles,
                filters=filters,
                include_balance=include_balance,
                include_details=include_details
            )
            
            # Execute query
            result = await execute_denodo_query(query)
            
            # Format response
            response_data = {
                "accounts": result.get("elements", []),
                "total_count": len(result.get("elements", [])),
                "query_metadata": {
                    "roles_used": roles,
                    "filters_applied": filters,
                    "query": query[:500]  # First 500 chars for debugging
                }
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(response_data)
            )]
        
        elif name == "get_account_summary":
            roles = arguments.get("roles", [])
            
            logger.info(f"📊 DENODO MCP: Getting summary for roles: {roles}")
            
            query = QueryBuilder.build_summary_query(roles)
            result = await execute_denodo_query(query)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "summary": result.get("elements", []),
                    "roles": roles
                })
            )]
        
        elif name == "get_account_detail":
            account_number = arguments.get("account_number")
            roles = arguments.get("roles", [])
            
            logger.info(f"🔍 DENODO MCP: Getting detail for account: {account_number}")
            
            query = QueryBuilder.build_account_detail_query(account_number, roles)
            result = await execute_denodo_query(query)
            
            accounts = result.get("elements", [])
            if not accounts:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Account not found or access denied based on roles"
                    })
                )]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "account": accounts[0],
                    "access_granted": True
                })
            )]
        
        elif name == "execute_custom_query":
            query = arguments.get("query")
            roles = arguments.get("roles", [])
            
            logger.info(f"⚠️ DENODO MCP: Executing custom query")
            
            # Add role-based WHERE clause to custom query for security
            # This ensures users can only see data for their roles
            if "WHERE" in query.upper():
                role_filter = " AND (" + " OR ".join([
                    f"entitlement_roles LIKE '%{role}%'" for role in roles
                ]) + ")"
                query = query.replace("WHERE", f"WHERE {role_filter} AND", 1)
            
            result = await execute_denodo_query(query)
            
            return [TextContent(
                type="text",
                text=json.dumps(result)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f'{{"error": "Unknown tool: {name}"}}'
            )]
            
    except Exception as e:
        logger.error(f"❌ DENODO MCP: Error in {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the Denodo MCP server."""
    logger.info("🚀 Starting Denodo MCP Server...")
    logger.info(f"📡 Connected to Denodo: {DENODO_URL}")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

