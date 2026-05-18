# PROTOCOLO DE SEGURIDAD — OmegaRaisen
## CIA-Level adaptado al stack Vite + FastAPI + Supabase
### Versión 1.0 · 17 mayo 2026

> **Filosofía:** defensa en profundidad, asumir compromiso. Si un atacante
> obtiene una API key, RLS lo limita. Si pasa RLS, los logs lo detectan.
> Si los logs fallan, los hooks pre-commit detectan secretos. Múltiples
> capas independientes — el fallo de una NO compromete el sistema.
>
> **Objetivo:** OmegaRaisen es un sistema que opera presencias digitales
> de marcas de terceros. Una brecha aquí daña directamente la reputación
> de N clientes (no solo del owner). El blast radius justifica controles
> CIA-level adaptados a SaaS multi-tenant.

---

## CAPA 1 — SECRETOS Y CREDENCIALES

### 1.1 — Nunca en código

```
PROHIBIDO HARDCODED:
  · API keys (Anthropic, Google, Stripe, Brave, Resend)
  · DATABASE_URL con password
  · JWT_SECRET_KEY
  · OAuth client_secret de Meta/TikTok/etc.
  · Stripe webhook secret
  · Service role keys de Supabase

PERMITIDO:
  · Public anon key de Supabase (es PÚBLICA por diseño RLS)
  · URLs públicas (https://...)
  · Modelo names ('claude-sonnet-4-6')
```

### 1.2 — Detección automática pre-commit

`scripts/validate-before-push.sh` corre los patrones del Check 4/9 (G6).
Si detecta cualquiera de estos formatos, el push se bloquea:

```
sk-ant-[a-zA-Z0-9_-]{20,}      Anthropic
AIza[a-zA-Z0-9_-]{30,}         Google
sk_live_[a-zA-Z0-9]{20,}       Stripe live
whsec_[a-zA-Z0-9]{20,}         Stripe webhook
eyJ[a-zA-Z0-9_-]+\.[..]+\.     JWT format
postgres://[^"]+:[^"]+@        DB URLs con password
```

### 1.3 — Rotación obligatoria

Cuándo rotar todas las keys:
- ✓ Al migrar del repo viejo al nuevo (Fase 1 del MIGRATION_PLAN)
- ✓ Si un colaborador deja el proyecto
- ✓ Si hay sospecha de leak (key en logs, en screenshot público, etc.)
- ✓ Cada 6 meses (rotación preventiva)

### 1.4 — Almacenamiento

```
LOCAL DEV       .env (gitignored)
RAILWAY         Variables de entorno del servicio
VERCEL          Variables de entorno por env (Production/Preview)
SUPABASE        Vault de Supabase (para keys que el backend lee)
BACKUP          Password manager 1Password/Bitwarden con sharing al equipo
```

NUNCA: Slack DMs, email, Notion público, comentarios en código.

---

## CAPA 2 — AUTENTICACIÓN

### 2.1 — JWT con expiración corta

```python
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 10080   # 7 días (current)
# Considerar para producción: 60 min con refresh token
```

### 2.2 — Password policy

```python
MIN_PASSWORD_LENGTH = 8
REQUIRE_PASSWORD_UPPERCASE = True
REQUIRE_PASSWORD_LOWERCASE = True
REQUIRE_PASSWORD_NUMBER = True
REQUIRE_PASSWORD_SPECIAL = True
```

Hash: **bcrypt** (`passlib[bcrypt]==1.7.4`). NUNCA SHA o MD5 directo.

### 2.3 — Account lockout

```
3 intentos fallidos consecutivos    → block_until = now + 15 min
6 intentos en 1 hora                → block_until = now + 1 hora
12 intentos en 24 horas             → notify owner + block 24h
```

Implementación: tabla `login_attempts` con TTL via pg_cron cleanup.

### 2.4 — Session management

```
Token revocation list (TRL):
  · Tabla `revoked_tokens` con jti + expires_at
  · Verificar JTI no esté revocado en cada request
  · Logout = INSERT en revoked_tokens

Concurrent sessions:
  · Permitido por defecto (UX)
  · Por cuenta `owner`: máximo 3 sesiones activas simultáneas
  · Notificación al owner si detecta login desde IP no-vista en 30 días
```

---

## CAPA 3 — AUTORIZACIÓN (RLS)

### 3.1 — RLS activo en TODAS las tablas con identificadores

Tablas que DEBEN tener RLS:
- Cualquiera con `user_id`, `client_id`, `reseller_id`, `org_id`
- Sin excepción

Verificación automática (migración 00003):
```sql
SELECT t.tablename
FROM pg_tables t
JOIN information_schema.columns c ON ...
WHERE t.rowsecurity = false
  AND c.column_name IN ('user_id','client_id','reseller_id','org_id');
-- Esperado: 0 filas
```

### 3.2 — Policies por rol

```
auth.role()='service_role'     → backend acceso completo (bypass RLS)
auth.role()='authenticated'    → solo a SUS datos
auth.role()='anon'             → solo lectura de catálogos públicos
```

### 3.3 — Service role NUNCA en cliente

```
SUPABASE_SERVICE_ROLE_KEY      → SOLO en backend (Railway env var)
SUPABASE_ANON_KEY              → frontend (Vercel env var) + backend para
                                  operaciones que respetan RLS
```

Verificación: `VITE_SUPABASE_*` nunca debe contener `service_role`.

---

## CAPA 4 — INPUT VALIDATION

### 4.1 — Pydantic estricto

Todo endpoint FastAPI usa Pydantic models con validación:

```python
from pydantic import BaseModel, EmailStr, constr, conint

class CreateClientRequest(BaseModel):
    name: constr(min_length=2, max_length=100)
    email: EmailStr
    business_type: str
    plan: str

    class Config:
        extra = "forbid"   # rechaza campos no declarados
```

### 4.2 — SQL injection — usar parámetros

```python
# ✓ CORRECTO
result = supabase.table("clients").select("*").eq("id", client_id).execute()

# ✗ NUNCA
result = supabase.rpc("query", {"sql": f"SELECT * FROM clients WHERE id='{client_id}'"})
```

### 4.3 — XSS — sanitización en frontend

```typescript
// Mostrar contenido del usuario:
import DOMPurify from 'isomorphic-dompurify'

<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />

// O preferible:
<div>{userContent}</div>   // React escapa por defecto
```

### 4.4 — CSRF

FastAPI + JWT en `Authorization` header (no cookies) → CSRF mitigated.

Si en algún momento se usan cookies HttpOnly: implementar SameSite=Lax + token CSRF.

---

## CAPA 5 — OAUTH DE REDES SOCIALES

### 5.1 — Tokens encriptados at rest

```sql
CREATE TABLE social_accounts (
  ...
  access_token  text,    -- Supabase encripta at rest por default
  refresh_token text,
  ...
);
```

**Adicionalmente**, aplicación-level encryption con Fernet:

```python
from cryptography.fernet import Fernet
f = Fernet(settings.ENCRYPTION_KEY)
encrypted = f.encrypt(access_token.encode())
# Guardar `encrypted` en DB
```

### 5.2 — Scopes mínimos

Solicitar solo los scopes que se usan. Documentar cada uno:

```
instagram_basic              ver perfil
instagram_content_publish    publicar (requiere review de Meta)
pages_show_list              listar páginas FB del usuario
NO solicitar: friends, messages, contacts (over-scope = rechazo de Meta)
```

### 5.3 — Refresh token rotation

Cuando uses refresh token: el server emite uno nuevo, el viejo se invalida.

### 5.4 — Revocación de OAuth

Si un cliente desconecta: llamar al endpoint `/oauth/revoke` de la plataforma
+ DELETE en `social_accounts`.

---

## CAPA 6 — RATE LIMITING

### 6.1 — Por endpoint y por IP

```python
# Endpoint sensible (auth)
@router.post("/auth/login")
@rate_limit(per_ip=10, per_minute=True)
async def login(...): ...

# API general
@router.get("/clients/{id}")
@rate_limit(per_user=120, per_minute=True)
```

### 6.2 — Circuit breaker para API externas

```python
# Si Anthropic responde >30s o falla 5 veces seguidas:
#   → pausar 60s, retry con backoff exponencial
#   → si sigue: alerta SENTINEL crítica
```

### 6.3 — Cost guardrail

```python
# Por cliente, por día:
if current_day_cost_usd > LIMITS_OMEGA["MAX_USD_DIARIO_API_POR_CLIENTE"]:
    # Degradar routing: Sonnet → Haiku
    # Notificar owner via NOVA
    # Si excede 3x: pausar generación automática del cliente
```

---

## CAPA 7 — OBSERVABILIDAD

### 7.1 — Logs estructurados

```python
import structlog
logger = structlog.get_logger()

logger.info(
    "agent_decision",
    agent_code="content_creator",
    client_id=str(client_id),
    confidence=8,
    decision="approve_draft",
)
```

NUNCA loggear: passwords, JWT tokens, API keys, contenido completo de prompts
con PII del cliente final.

### 7.2 — agent_log para auditoría

Toda llamada a Anthropic / Nano Banana / Veo 3.1 va a tabla `agent_log`:
- agent_code · model_used · input/output tokens · cost · latency · status

### 7.3 — SENTINEL pulse_monitor

Cada 5 min, SENTINEL verifica:
- Tests passing en CI
- Health de Railway (response time, error rate)
- Cost por cliente bajo límites
- Cero secretos en logs recientes
- RLS sigue activo en todas las tablas

Score < 95 → email + NOVA alert al owner.

### 7.4 — Langfuse para LLM tracing

```python
@observe(name="claude_messages_create")
async def generate(...):
    response = await client.messages.create(...)
    return response
```

Permite:
- Replay de cualquier conversación
- Análisis de prompt drift en el tiempo
- Cost attribution per cliente/agente
- Detección de regresiones de calidad

---

## CAPA 8 — DEPLOYMENT

### 8.1 — Pre-deploy checks (X1 OmegaRaisen)

```bash
# Antes de cada deploy a producción:
[ ] bash scripts/validate-before-push.sh             → 9/9
[ ] SENTINEL full_scan: security_score >= 95
[ ] Crons activos: 8/8
[ ] Migrations aplicadas exitosamente
[ ] Smoke test en staging pasa
[ ] Rollback plan documentado
```

### 8.2 — Headers HTTP

`vercel.json` define:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### 8.3 — CORS preciso

```python
BACKEND_CORS_ORIGINS = [
    "https://r-omega.agency",
    "https://www.r-omega.agency",
    # NUNCA "*" en producción
]
```

### 8.4 — TLS only

```python
SECURE_SSL_REDIRECT = True   # en production
```

Railway termina TLS por nosotros. Verificar que no exposes el puerto plano.

---

## CAPA 9 — DATOS DEL CLIENTE

### 9.1 — Cifrado at-rest

- Supabase: encripta DB at rest por default (AES-256)
- Storage: archivos encriptados, URLs firmadas con expiración corta
- Backups: encriptados también

### 9.2 — Retention policy

```
Logs de auth                    90 días
agent_log                       1 año (luego archivar)
agent_memory                    Indefinido (es el activo del proyecto)
Posts publicados                Indefinido
Posts no publicados             6 meses
Stripe events                   7 años (regulatorio)
Soft-deleted clients            30 días → hard delete
```

### 9.3 — GDPR/LGPD compliance

Implementar:
- Right to access: endpoint `/api/v1/me/data-export` (devuelve todos los datos del usuario)
- Right to deletion: endpoint `/api/v1/me/delete-account` (anonimización + hard delete con período de gracia 30d)
- Consent tracking: tabla `consent_log` con cada consentimiento del cliente
- Data Processing Agreement con clientes/resellers

### 9.4 — PII en logs

Sanitizar antes de loggear:
```python
def sanitize_pii(text: str) -> str:
    # Sustituir emails: alguien@dominio.com → ******@dominio.com
    # Sustituir teléfonos: +1-787-XXX-XXXX → +1-787-***-****
    # Sustituir números de tarjeta de crédito si aparecen
    return text
```

---

## CAPA 10 — RESPUESTA A INCIDENTES

### 10.1 — Roles definidos

```
INCIDENT_COMMANDER         Owner (Jorge Ibrain)
TECH_LEAD                  Engineer on-call (rotating)
COMMUNICATIONS             Owner (notifica clientes/resellers)
LEGAL                      Asesor externo si data breach
```

### 10.2 — Severidad

```
SEV-1   Producción caída · data breach · clientes afectados activamente
SEV-2   Degradación parcial · funcionalidad importante rota
SEV-3   Bug menor · workaround disponible
SEV-4   Mejora cosmética
```

### 10.3 — Playbook SEV-1

```
1. 0-5 min:   Confirmar y reproducir
2. 5-15 min:  Estabilizar (rollback inmediato si feasible)
3. 15-30 min: Comunicar a clientes/resellers (incident comm template)
4. 30-60 min: Mitigation activa
5. 1-4 horas: Resolution + verificación
6. 24 horas:  Post-mortem público + acciones preventivas
```

### 10.4 — Data breach

Si se confirma data breach:
- Notificación a usuarios afectados ≤ 72 horas (GDPR)
- Reset de credenciales obligatorio para usuarios afectados
- Rotación de TODAS las API keys
- Asesoría legal antes de comunicación pública
- Reporte a autoridades si aplica jurisdicción

---

## CAPA 11 — ACCESO ADMIN

### 11.1 — MFA obligatorio

Toda cuenta con rol `owner` o `admin` debe tener:
- MFA en GitHub
- MFA en Anthropic Console
- MFA en Google Cloud (para Nano Banana / Veo keys)
- MFA en Stripe
- MFA en Supabase
- MFA en Vercel + Railway

Sin excepciones.

### 11.2 — Principle of least privilege

```
GitHub
  raisenomega@org/Omega:   admin (1 persona)
  collaborators:           write (sin admin)

Supabase
  service_role:            backend only (Railway)
  anon_key:                frontend + backend

Stripe
  secret_key:              restricted-key con scopes mínimos
  webhook_secret:          inmutable

Anthropic / Google
  API keys:                separadas por env (dev/staging/prod)
  spend limits:            configurados en console
```

---

## VERIFICACIÓN PERIÓDICA

Mensualmente, owner ejecuta:

```bash
# 1. SENTINEL full_scan
curl https://omega-backend.up.railway.app/api/v1/sentinel/scan/full

# 2. Audit de RLS (debe retornar 0 filas)
psql $DATABASE_URL -c "
SELECT t.tablename FROM pg_tables t
JOIN information_schema.columns c ON ...
WHERE t.rowsecurity = false AND c.column_name IN ('user_id','client_id');
"

# 3. Audit de últimos 30 commits con identidad
cd "D:/Omega Master redes" && git log --since='30 days ago' --pretty=format:'%an <%ae>' | sort -u
# Esperado: solo raisenomega <raisenomega@...>

# 4. Audit de secretos en logs (Railway)
railway logs --service backend | grep -E 'sk-|password|secret'
# Esperado: 0 matches

# 5. Audit de costo Anthropic vs límite
# Console Anthropic: spend del mes vs presupuesto
```

---

```
PROTOCOLO_SEGURIDAD_OMEGA.md
Versión 1.0 · 17 mayo 2026
Próxima revisión: Q3 2026 (post-Phase 4 + audit externo)
Compatible con: SOURCE_OF_TRUTH.md + DDD_REGLAS_OMEGA.md
```
