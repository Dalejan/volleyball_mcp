# MCP VoleyBall

Servidor MCP (Model Context Protocol) que proporciona acceso a datos de voleibol mediante consultas SQL. El proyecto incluye un proceso ETL para obtener datos de la API de VolleyballWorld y almacenarlos en una base de datos SQLite.

<a href="https://glama.ai/mcp/servers/@Dalejan/volleyball_mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@Dalejan/volleyball_mcp/badge" alt="Volleyball Server MCP server" />
</a>

## Descripción

Este proyecto permite consultar datos de partidos, equipos y torneos de voleibol a través de un servidor MCP. Los datos se obtienen desde la API de VolleyballWorld mediante un scraper, se convierten a formato SQLite y se exponen mediante un servidor MCP que permite ejecutar queries SQL.

## Requisitos

- Python 3.11 o superior
- `uv` (gestor de paquetes) - [Instalar uv](https://github.com/astral-sh/uv)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd MCP-VoleyBall
```

2. Instalar dependencias:
```bash
uv sync
```

## Uso

### 1. Proceso ETL (Extracción y carga de datos)

Primero necesitas obtener los datos de la API y convertirlos a base de datos SQLite:

1. **Extraer datos de un torneo:**
```bash
cd ETL
python scrapper.py
```

Por defecto, el scraper obtiene datos del torneo 1520 del año 2025. Puedes modificar los parámetros en `scrapper.py` según necesites.

2. **Convertir JSON a SQLite:**
```bash
python database_converter.py
```

Esto creará/actualizará el archivo `volleyball_data.db` en el directorio `ETL/` con todos los datos estructurados.

### 2. Servidor MCP

Una vez que tengas la base de datos creada, puedes ejecutar el servidor MCP:

```bash
python main.py
```

Para desarrollo y pruebas del servidor MCP:

```bash
mcp dev main.py
```

O usando npx:

```bash
npx @modelcontextprotocol/inspector uv run main.py
```

El servidor MCP expone una herramienta `execute_query` que permite ejecutar queries SELECT en la base de datos de voleibol.

### 3. Visualización con Datasette

Para visualizar y explorar los datos de manera interactiva usando Datasette, ejecuta:

```bash
cd ETL
datasette serve volleyball_data.db
```

Esto iniciará un servidor web local (por defecto en `http://127.0.0.1:8001`) donde podrás explorar las tablas, ejecutar queries SQL y visualizar los datos de manera interactiva.

## Configuración del MCP Server en Claude Desktop

Para usar este servidor MCP con Claude Desktop, agrega la siguiente configuración en tu archivo de configuración MCP (normalmente  `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-voleyball": {
      "command": "python",
      "args": ["/ruta/completa/a/MCP-VoleyBall/main.py"]
    }
  }
}
```

Asegúrate de usar la ruta absoluta al archivo `main.py`.

## Estructura del Proyecto

```
MCP-VoleyBall/
├── main.py                 # Servidor MCP
├── db_connection.py        # Conexión a la base de datos
├── ETL/
│   ├── scrapper.py         # Extracción de datos de la API
│   ├── database_converter.py  # Conversión JSON a SQLite
│   └── volleyball_data.db  # Base de datos (se genera con el ETL)
└── pyproject.toml          # Dependencias del proyecto
```

## Ejemplo de Queries

Una vez configurado el servidor MCP, puedes hacer consultas como:

```
'Que equipo gano mas partidos en el ano 2025'
```