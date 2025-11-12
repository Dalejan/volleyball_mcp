from mcp.server.fastmcp import FastMCP, Context
from db_connection import run_query
from mcp.server.session import ServerSession

# Crear instancia del servidor MCP
mcp = FastMCP("mcp-voleyball")

@mcp.tool()
async def execute_query(query: str, ctx: Context[ServerSession, None]) -> list:
    """
    Ejecuta una query SQL en la base de datos de voleibol.

    Args:
        query: La query SQL a ejecutar.

    Returns:
        Una lista de tuplas con los resultados de la query.
    """
    try:
        rows = run_query(query)
        return rows
    except Exception as e:
        await ctx.elicit(
            message=(f"Error executing query: {e}"),
            schema=None,
        )
        return None
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')