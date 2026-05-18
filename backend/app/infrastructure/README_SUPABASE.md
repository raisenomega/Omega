# Supabase Service - OMEGA Platform

## 📋 Descripción

Servicio centralizado para interactuar con Supabase (PostgreSQL + Storage) en el backend de OMEGA.

## 🎯 Funcionalidades

### Resellers Management
- `create_reseller()` - Crear nuevo reseller
- `get_reseller(reseller_id)` - Obtener por ID
- `get_reseller_by_slug(slug)` - Obtener por slug (público)
- `get_all_resellers()` - Listar todos
- `update_reseller(reseller_id, data)` - Actualizar

### Branding Management
- `create_branding(data)` - Crear configuración de marca
- `get_branding(reseller_id)` - Obtener branding
- `update_branding(reseller_id, data)` - Actualizar (upsert automático)

### Reseller Agents (Humanos)
- `create_reseller_agent(data)` - Crear agente humano
- `get_reseller_agents(reseller_id)` - Listar agentes activos

### Client Management
- `get_reseller_clients(reseller_id)` - Clientes del reseller
- `assign_client_to_reseller(client_id, reseller_id)` - Asignar cliente

### Media Upload (Storage)
- `upload_media(bucket, file_path, file_data, content_type)` - Subir archivo
- `delete_media(bucket, file_path)` - Eliminar archivo

## 🔧 Uso

```python
from app.infrastructure.supabase_service import supabase_service

# Crear reseller
reseller = await supabase_service.create_reseller({
    "slug": "agencia-demo",
    "agency_name": "Agencia Demo",
    "owner_email": "demo@agencia.com",
    "owner_name": "Demo Owner"
})

# Obtener branding por slug
reseller = await supabase_service.get_reseller_by_slug("agencia-demo")
branding = await supabase_service.get_branding(reseller["id"])

# Upload media
public_url = await supabase_service.upload_media(
    bucket="reseller-media",
    file_path=f"{reseller['slug']}/hero.jpg",
    file_data=file_bytes,
    content_type="image/jpeg"
)
```

## 🔐 Autenticación

El servicio usa **Service Role Key** para tener acceso completo:
- Bypass de Row Level Security (RLS)
- Acceso a todas las tablas
- Operaciones de admin

**Variables requeridas:**
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📊 Estructura de Datos

### Reseller
```python
{
  "id": "uuid",
  "slug": "agenciajuan",
  "agency_name": "Agencia Juan",
  "owner_email": "juan@agencia.com",
  "owner_name": "Juan Pérez",
  "white_label_active": false,
  "status": "active",
  "omega_commission_rate": 0.30,
  "created_at": "2026-02-13T..."
}
```

### Reseller Branding
```python
{
  "id": "uuid",
  "reseller_id": "uuid",
  "logo_url": "https://...",
  "hero_media_url": "https://...",
  "hero_media_type": "video",
  "primary_color": "38 85% 55%",
  "secondary_color": "225 12% 14%",
  "agency_tagline": "Tu marca digital",
  "services": [...],
  "testimonials": [...]
}
```

## ⚠️ Errores Comunes

### Error: "Failed to initialize Supabase client"
**Solución:** Verificar variables de entorno

### Error: "relation does not exist"
**Solución:** Ejecutar migración SQL en Supabase

### Error: "bucket not found"
**Solución:** Crear bucket `reseller-media` en Supabase Storage

## 📚 Documentación

- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Storage API](https://supabase.com/docs/guides/storage)
- [PostgreSQL + Supabase](https://supabase.com/docs/guides/database)
