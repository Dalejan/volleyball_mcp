from mcp.server.fastmcp import FastMCP
from db_connection import run_query
from mcp.types import Context

# Crear instancia del servidor MCP
mcp = FastMCP("mcp-voleyball")

@mcp.tool()
def execute_query(query: str, ctx: Context) -> list:
    """
    Ejecuta una query SQL en la base de datos de voleibol.

    Args:
        query: La query SQL a ejecutar.

    Returns:
        Una lista de tuplas con los resultados de la query.
    """
    rows = run_query(query)
    return rows

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')