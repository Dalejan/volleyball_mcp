import sqlite3
from pathlib import Path
from typing import Any, List, Tuple


def _get_db_path() -> Path:
    """Obtiene la ruta de la base de datos."""
    # Intentar usar __file__ primero
    try:
        db_path = Path(__file__).resolve().parent / "ETL" / "volleyball_data.db"
        if db_path.exists():
            return db_path
    except (NameError, AttributeError):
        pass
    
    # Fallback: usar directorio de trabajo actual
    return Path.cwd() / "ETL" / "volleyball_data.db"


def get_connection() -> sqlite3.Connection:
    """Obtiene una conexión a la base de datos."""
    db_path = _get_db_path()
    return sqlite3.connect(str(db_path))

def run_query(sql: str, params: Tuple[Any, ...] = ()) -> List[Tuple]:
    """Ejecuta una query SELECT y devuelve los resultados.
    
    Args:
        sql: La query SQL a ejecutar.
        params: Los parámetros para la query.

    Returns:
        Una lista de tuplas con los resultados de la query.
    """
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Solo se permiten queries SELECT. Intenta con una query SELECT.")
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()
