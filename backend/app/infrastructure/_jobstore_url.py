"""DEBT-047 fix · arma la URL del jobstore desde COMPONENTES con URL.create.

Causa probada (PASO 1): el password de la DATABASE_URL tiene `@` → el parse-string de create_engine
lo lee como separador user@host → host queda "@@aws-1..." → OperationalError → _persistent_jobstore_
or_none cae a in-memory. URL.create toma el password CRUDO y lo escapa internamente (resuelve el @
y cualquier otro carácter especial · más robusto que %40 a mano). Puro · testeable · sin I/O.
"""
import re
from typing import Union

from sqlalchemy.engine import URL

# user:password@host:port/db · password greedy hasta el ÚLTIMO @ (el host no lleva @).
_RE = re.compile(r"^postgres(?:ql)?(?:\+\w+)?://([^:]+):(.*)@([^:@/]+):(\d+)/(.+)$")


def build_jobstore_url(raw: str) -> Union[URL, str]:
    """URL.create desde componentes (escapa el password · @/# etc). Si no parsea → devuelve el raw
    tal cual (create_engine decide · la red try/except del caller cubre cualquier fallo)."""
    m = _RE.match((raw or "").strip())
    if not m:
        return raw
    user, password, host, port, database = m.groups()
    return URL.create("postgresql+psycopg2", username=user, password=password,
                      host=host, port=int(port), database=database)


def pick_jobstore_url(override: str, default: str) -> str:
    """JOBSTORE_DATABASE_URL (override · conexión DIRECTA seteada en Railway · DEBT-047) si está ·
    si no, default (DATABASE_URL · comportamiento actual). Permite apuntar SOLO el jobstore a la
    directa sin tocar la DATABASE_URL global ni el resto de la app. Ambos vacíos → "" → caller None."""
    o = (override or "").strip()
    return o if o else (default or "").strip()
