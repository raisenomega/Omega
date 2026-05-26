# backend/app/infrastructure/tools/tool_definitions.py
# MAX 200 LINES — R-LINES-001
# Tool Definitions — definiciones de tools para Claude API

# ── TOOL DEFINITIONS ─────────────────────────────────────────────────────────
TOOL_DEFINITIONS: dict[str, dict] = {
    "web_search": {
        "name": "web_search",
        "description": "Busca información actual en internet via Tavily. Retorna resultados verificados con fuentes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La búsqueda a realizar. Sé específico para mejores resultados."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número de resultados (1-5). Default: 3.",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    },
    "fetch_url": {
        "name": "fetch_url",
        "description": "Extrae el contenido de una URL específica. Útil para analizar páginas de competidores, artículos, o perfiles públicos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL completa a extraer (incluyendo https://)"
                },
                "extract_type": {
                    "type": "string",
                    "enum": ["text", "summary"],
                    "description": "text: contenido completo. summary: resumen del contenido.",
                    "default": "text"
                }
            },
            "required": ["url"]
        }
    },
    "supabase_read": {
        "name": "supabase_read",
        "description": "Lee datos de Supabase para el cliente actual. Solo puede leer tablas autorizadas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "Nombre de la tabla a consultar"
                },
                "filters": {
                    "type": "object",
                    "description": "Filtros en formato {campo: valor}. client_id se agrega automáticamente.",
                    "default": {}
                },
                "limit": {
                    "type": "integer",
                    "description": "Máximo de registros a retornar. Default: 10.",
                    "default": 10
                }
            },
            "required": ["table"]
        }
    },
    "supabase_write": {
        "name": "supabase_write",
        "description": "Guarda datos en Supabase. Solo en tablas autorizadas. client_id se agrega automáticamente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "Tabla donde guardar"
                },
                "data": {
                    "type": "object",
                    "description": "Datos a insertar o actualizar"
                },
                "operation": {
                    "type": "string",
                    "enum": ["insert", "upsert"],
                    "default": "insert"
                }
            },
            "required": ["table", "data"]
        }
    },
    "notification_send": {
        "name": "notification_send",
        "description": "Envía una notificación in-app al cliente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Título de la notificación"},
                "message": {"type": "string", "description": "Mensaje de la notificación"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent"],
                    "default": "normal"
                }
            },
            "required": ["title", "message"]
        }
    },
    "calendar_write": {
        "name": "calendar_write",
        "description": "Agrega un evento al calendario editorial del cliente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "scheduled_date": {"type": "string", "description": "ISO datetime"},
                "content_type": {"type": "string", "description": "post, story, reel, email"},
                "notes": {"type": "string", "default": ""}
            },
            "required": ["title", "scheduled_date", "content_type"]
        }
    },
}

# ── TABLAS AUTORIZADAS POR OPERACIÓN ─────────────────────────────────────────
READ_ALLOWED_TABLES = {
    "omega_agents", "omega_activity", "omega_approval_requests",
    "omega_worker_logs", "scheduled_posts", "brand_files",
    "clients", "social_accounts", "content_pieces",
    "sentinel_scans",
}

WRITE_ALLOWED_TABLES = {
    "omega_approval_requests", "omega_activity", "omega_worker_logs",
    "scheduled_posts", "content_pieces",
}
