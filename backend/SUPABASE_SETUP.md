# SUPABASE SETUP - FASE 2 MULTI-TENANT

## 📋 PASO 1: CREAR PROYECTO EN SUPABASE

1. Ir a [https://supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. Anotar credenciales:
   - **Project URL** (SUPABASE_URL)
   - **Anon/Public Key** (SUPABASE_ANON_KEY)
   - **Service Role Key** (SUPABASE_SERVICE_ROLE_KEY) ⚠️ Secreto

---

## 📊 PASO 2: EJECUTAR MIGRACIÓN SQL

1. En Supabase Dashboard → SQL Editor
2. Copiar todo el contenido de `backend/supabase_migrations/002_resellers_multitenant.sql`
3. Ejecutar

Esto crea:
- ✅ Tabla `resellers` (agencias white-label)
- ✅ Tabla `reseller_branding` (configuración de marca)
- ✅ Tabla `reseller_agents` (agentes humanos)
- ✅ Modifica `clients` (agrega reseller_id)
- ✅ Modifica `leads` (agrega reseller_id)

---

## 🗄️ PASO 3: CONFIGURAR STORAGE BUCKET

1. En Supabase Dashboard → Storage
2. Crear nuevo bucket:
   - **Name**: `reseller-media`
   - **Public bucket**: ✅ Yes (para URLs públicas)
3. Configurar políticas:

```sql
-- Política para permitir uploads autenticados
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'reseller-media');

-- Política para permitir acceso público
CREATE POLICY "Allow public access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'reseller-media');

-- Política para permitir actualización autenticada
CREATE POLICY "Allow authenticated updates"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'reseller-media');
```

4. Configurar límites:
   - Max file size: **15MB**
   - Allowed MIME types: `video/mp4, video/webm, image/jpeg, image/png, image/webp`

---

## 🔐 PASO 4: VARIABLES DE ENTORNO

Agregar a `.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # ⚠️ SECRETO

# Database URL (mismo proyecto Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
```

---

## 📦 PASO 5: INSTALAR DEPENDENCIAS

```bash
cd backend
pip install supabase==2.3.0
# O ejecutar:
pip install -r requirements.txt
```

---

## ✅ PASO 6: VERIFICAR INSTALACIÓN

```bash
# Iniciar servidor
python -m uvicorn app.main:app --reload

# Probar endpoints (desde otra terminal)
curl http://localhost:8000/api/v1/resellers/all
```

Debería retornar:
```json
{
  "success": true,
  "data": {
    "resellers": [],
    "count": 0
  },
  "message": "Found 0 resellers"
}
```

---

## 🧪 PASO 7: CREAR PRIMER RESELLER DE PRUEBA

```bash
curl -X POST http://localhost:8000/api/v1/resellers/create \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "agenciatest",
    "agency_name": "Agencia Test",
    "owner_email": "test@agencia.com",
    "owner_name": "Juan Test"
  }'
```

---

## 🌐 ENDPOINTS DISPONIBLES

### Resellers Management
- `POST /api/v1/resellers/create` - Crear reseller
- `GET /api/v1/resellers/all` - Listar todos (admin)
- `GET /api/v1/resellers/{id}/dashboard` - Dashboard del reseller
- `PATCH /api/v1/resellers/{id}/status` - Actualizar status (admin)
- `GET /api/v1/resellers/slug/{slug}` - Obtener por slug (público)

### Branding Configuration
- `POST /api/v1/resellers/{id}/branding` - Actualizar branding
- `GET /api/v1/resellers/{id}/branding` - Obtener branding
- `POST /api/v1/resellers/{id}/upload-hero-media` - Subir video/imagen hero

### Client Management
- `GET /api/v1/resellers/{id}/clients` - Listar clientes
- `POST /api/v1/resellers/{id}/clients/add` - Asignar cliente

---

## 📝 MODELO DE DATOS

### Reseller
```typescript
{
  id: UUID
  slug: string                    // "agenciajuan"
  agency_name: string
  owner_email: string
  owner_name: string
  stripe_account_id?: string
  stripe_customer_id?: string
  white_label_active: boolean
  status: "active" | "warning" | "suspended" | "terminated"
  omega_commission_rate: number   // 0.30 = 30%
  monthly_revenue_reported: number
  payment_due_date?: Date
  days_overdue: number
  suspend_switch: boolean
  clients_migrated: boolean
}
```

### Reseller Branding
```typescript
{
  id: UUID
  reseller_id: UUID
  logo_url?: string
  hero_media_url?: string         // Video o imagen (max 15MB)
  hero_media_type?: "video" | "image"
  primary_color: string           // HSL: "38 85% 55%"
  secondary_color: string         // HSL: "225 12% 14%"
  agency_tagline?: string
  badge_text: string
  hero_cta_text: string
  pain_items: string[]
  solution_items: string[]
  services: Array<{icon, title, description}>
  metrics: Array<{value, label}>
  process_steps: Array<{step, title, description}>
  testimonials: Array<{name, role, text, image?}>
  footer_email?: string
  footer_phone?: string
  social_links: Array<{platform, url}>
  legal_pages: Array<{title, url}>
}
```

---

## 🚀 SIGUIENTE FASE

Una vez configurado:
1. ✅ Backend funcionando con Supabase
2. ✅ Endpoints multi-tenant operativos
3. ➡️ **FASE 3**: Frontend white-label (Vite + shadcn)

---

## ⚠️ SEGURIDAD

- **NUNCA** commits `.env` con `SUPABASE_SERVICE_ROLE_KEY`
- **SIEMPRE** usa variables de entorno en Railway/Render
- **Row Level Security (RLS)** se configura en FASE 3 para auth

---

## 📞 SOPORTE

Si hay errores:
1. Verificar variables de entorno
2. Verificar migración SQL ejecutada
3. Verificar bucket `reseller-media` creado
4. Ver logs: `tail -f logs/app.log`
