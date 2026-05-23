-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00019 · prompt_vault seed (Sprint 1 ① · 23 may 2026)    ║
-- ║                                                                    ║
-- ║  Insert 30 prompts production-tested desde CONTENT_LAB_OMEGA       ║
-- ║  _MASTER.md §5. Performance scores 7.2-9.2. Activa el vault para   ║
-- ║  _prompt_vault_selector (Sprint 1 ②).                              ║
-- ║                                                                    ║
-- ║  Constraint UNIQUE (00015 cambió de 'version' a 'slot_name'):      ║
-- ║   prompt_vault_slot_unique (category, vertical, platform, slot_name)║
-- ║   Cada prompt tiene slot_name descriptivo único · 4 captions con   ║
-- ║   mismo (cat+vert+plat) usan slot_name distinto.                   ║
-- ║                                                                    ║
-- ║  ON CONFLICT DO NOTHING → idempotente · re-aplicable sin error.    ║
-- ╚═══════════════════════════════════════════════════════════════════╝

INSERT INTO prompt_vault (category, vertical, platform, agent_code, performance_score, slot_name, prompt_text)
VALUES
('script', 'construction', 'instagram', 'RAFA', 9.2, 'time_lapse_project',
'Crea script para Reel time-lapse de proyecto completo (30-60s):
- OPENING (0-5s): Toma del "before" con texto overlay "Día 1"
- TIME-LAPSE (6-50s): Secuencia acelerada mostrando progreso día a día
- REVEAL (51-58s): Resultado final con música de impacto
- CTA (59-60s): Logo + texto "¿Tu proyecto? Escríbenos"
Datos del cliente: {client_name}, {niche}, {brand_voice}
Tono: {tone}. Audiencia: {target_audience}'),

('caption', 'restaurant', 'instagram', 'RAFA', 9.1, 'daily_special',
'Crea caption para plato del día/special del restaurante:
- HOOK VISUAL: Nombre del plato + emoji apetitoso
- DESCRIPCIÓN SENSORIAL: Describe sabores, texturas, aromas (2-3 líneas)
- HISTORIA: Origen del plato o qué lo hace especial (1-2 líneas)
- DISPONIBILIDAD: "Solo hoy" o "Esta semana"
- CTA: "Reserva ahora" o "Visítanos hoy"
- HASHTAGS: 5-8 relevantes al final
Cliente: {client_name}. Tono: {tone}. Audiencia: {target_audience}'),

('caption', 'real_estate', 'instagram', 'RAFA', 9.0, 'luxury_storytelling',
'Escribe caption de lujo para propiedad premium usando storytelling:
- HERO: El comprador ideal (ejecutivo, familia exitosa, inversor)
- SETTING: Describe la propiedad como escenario de vida ideal
- TRANSFORMATION: Cómo cambia la vida al vivir ahí
- PROOF: 1-2 características únicas y verificables
- CTA: "Agenda tu visita privada" + datos de contacto
Max 220 palabras. Tono: {tone}. Audiencia: {target_audience}'),

('script', 'restaurant', 'instagram', 'RAFA', 9.0, 'signature_dish_prep',
'Crea script para Reel mostrando preparación de plato signature (30s):
- HOOK (0-3s): Close-up del plato final + texto "Así hacemos nuestro [plato]"
- PREP (4-25s): Secuencia rápida del chef preparando, ingredientes frescos
- REVEAL (26-28s): Plato completo con cliente satisfecho
- CTA (29-30s): Nombre del restaurante + "Reserva ya"
Enfatizar: frescura, tradición, amor por la cocina
Cliente: {client_name}. Tono: {tone}'),

('caption', 'health', 'instagram', 'RAFA', 8.9, 'testimonial',
'Escribe caption compartiendo testimonio de paciente/cliente (con permiso):
- OPENING: "Historias como la de [Nombre] nos recuerdan por qué hacemos esto"
- SITUATION: Breve contexto del reto que tenía (sin detalles médicos privados)
- TRANSFORMATION: Resultado específico y mensurable
- EMOTION: Cómo impactó su vida (trabajo, familia, autoestima)
- CTA: "¿Tu historia podría ser la próxima?"
Tono empático, nunca exagerado. Cliente: {client_name}'),

('caption', 'construction', 'instagram', 'RAFA', 8.8, 'before_after',
'Crea caption para post Before/After de proyecto de construcción:
- HOOK: Frase impactante sobre transformación
- CONTEXT: Breve historia del proyecto (qué era antes, el reto)
- PROCESS: 1-2 decisiones técnicas que marcaron la diferencia
- RESULT: Metros cuadrados, tiempo, presupuesto (si el cliente autoriza)
- CTA: "¿Tu espacio tiene potencial? Hablemos"
Tono profesional pero accesible. Cliente: {client_name}'),

('script', 'restaurant', 'tiktok', 'RAFA', 8.8, 'client_reaction',
'Crea script para video estilo "reacción de cliente" al probar plato (15-20s):
- SETUP (0-3s): Cliente sentado, mesero trae el plato
- FIRST BITE (4-8s): Close-up de la cara + reacción auténtica
- QUOTE (9-14s): Frase del cliente sobre el plato (guion sugerido)
- LOGO (15-17s): Nombre del restaurante + dirección
Hook de TikTok: empezar con la reacción, no con la llegada del plato
Cliente: {client_name}. Tono: {tone}'),

('script', 'real_estate', 'instagram', 'RAFA', 8.7, 'property_tour',
'Crea script para Reel de property tour (15-30 segundos):
- HOOK (0-3s): Frase impactante + texto on-screen impactante
- TOUR (4-20s): 4-5 tomas rápidas de las mejores features
- PRICE/CTA (21-28s): Precio si aplica + "Link en bio para más info"
Mostrar: cocina, sala principal, el mejor ángulo exterior
Evitar: baños principales, closets vacíos, áreas sin terminar
Cliente: {client_name}. Tono: {tone}'),

('caption', 'restaurant', 'instagram', 'RAFA', 8.7, 'weekend_event',
'Escribe caption para evento especial de fin de semana:
- HEADLINE: Nombre del evento + fecha con urgencia
- QUÉ: Breve descripción (música, menú especial, tema)
- POR QUÉ IR: 2-3 razones específicas que creen FOMO
- DETALLES: Hora, reservas, precio si aplica
- CTA: "Reserva ahora · Solo X mesas disponibles"
Crear urgencia real, no inventada. Cliente: {client_name}'),

('script', 'health', 'instagram', 'RAFA', 8.6, 'quick_tip',
'Crea script para Reel de tip rápido de salud (15-30s):
- HOOK (0-3s): Pregunta o statement provocador
- TIP (4-20s): Explica el tip visualmente (máximo 1 concepto)
- RESULTADO (21-26s): Qué mejora al aplicarlo
- CTA (27-30s): "Síguenos para más tips" + nombre del profesional
Lenguaje: simple, nunca técnico. Evitar: diagnosis, garantías
Cliente: {client_name}. Especialidad: {niche}'),

('caption', 'real_estate', 'instagram', 'RAFA', 8.5, 'aida_framework',
'Crea caption usando framework AIDA:
- ATTENTION: Hook en 3 palabras máximo
- INTEREST: 2-3 características únicas que no tienen los competidores
- DESIRE: Imagina la vida ahí · escena específica del día a día ideal
- ACTION: CTA específico con baja fricción ("Escríbenos HOY")
Max 200 palabras. 5-8 hashtags al final.
Cliente: {client_name}. Tono: {tone}'),

('story', 'restaurant', 'instagram', 'RAFA', 8.5, 'new_menu_launch',
'Crea secuencia de 5 Stories para lanzar nuevo menú:
STORY 1: Teaser - texto misterioso + countdown sticker
STORY 2: Reveal - "Nuevo Menú Disponible AHORA" + imagen del menú
STORY 3-4: Showcase 2-3 platos estrella con descripción corta
STORY 5: CTA - "¿Cuál probás primero?" + poll sticker con 2 opciones
Cada story: max 7 palabras de texto visible. Fondo oscuro si posible.
Cliente: {client_name}'),

('caption', 'health', 'instagram', 'RAFA', 8.4, 'educational_tip',
'Crea caption educativo sobre tip de salud/wellness:
- HOOK: Dato sorprendente o mito común a romper
- EDUCACIÓN: Explica el concepto en lenguaje simple (no jerga médica)
- APLICACIÓN: Cómo el lector puede implementarlo HOY
- CREDIBILIDAD: Menciona la fuente o tu experiencia brevemente
- CTA: "¿Tenías esto claro?" + invita a comentar
Tono: experto pero accesible. Evitar: exageraciones, garantías
Cliente: {client_name}'),

('story', 'construction', 'instagram', 'RAFA', 8.3, 'project_progress',
'Crea secuencia de 4 Stories para actualizar progreso de obra:
STORY 1: Wide shot del proyecto con texto "Update: [Nombre Proyecto]"
STORY 2: Close-up de detalle interesante + explicación breve
STORY 3: Team en acción (humaniza la empresa)
STORY 4: "¿Cuándo lo terminamos?" + fecha estimada + CTA
Mostrar progreso real, no solo lo perfecto. Eso genera confianza.
Cliente: {client_name}'),

('ad', 'restaurant', 'facebook', 'RAFA', 8.3, 'promo_inauguration',
'Crea Facebook Ad para promoción o inauguración:
- HEADLINE: Oferta clara y urgente (max 40 chars)
- HOOK: Por qué es imperdible · experiencia única
- BODY: Detalles de la oferta + lo que incluye
- SOCIAL PROOF: "Más de X personas ya lo probaron" si aplica
- CTA button: "Reservar ahora" o "Ver menú"
Objetivo: clicks a link o mensaje directo
Cliente: {client_name}. Presupuesto ad: {ad_budget}'),

('ad', 'real_estate', 'facebook', 'RAFA', 8.2, 'first_time_buyers_pas',
'Crea Facebook Ad para compradores primerizos usando PAS:
- PROBLEM: Describe el dolor de rentar sin construir patrimonio
- AGITATE: Cuánto pierde cada mes que sigue rentando
- SOLUTION: Tu propiedad como la respuesta concreta
- PROOF: Precio, ubicación, facilidades de financiamiento
- CTA: "Ver propiedades disponibles"
Tono: empático y empoderador, nunca alarmista
Cliente: {client_name}'),

('story', 'health', 'instagram', 'RAFA', 8.1, 'faq_qa',
'Crea secuencia de Stories para FAQ de salud/wellness:
STORY 1: "Q&A Time" + Question sticker
STORY 2-5: Responde 3-4 preguntas populares de tus pacientes/clientes
Formato por pregunta: Texto de la pregunta (arriba) · Respuesta corta (abajo)
STORY final: "¿Más preguntas? DM directo o agenda aquí"
Las preguntas deben ser reales y frecuentes, no genéricas
Cliente: {client_name}. Especialidad: {niche}'),

('ad', 'construction', 'facebook', 'RAFA', 8.1, 'remodel_pas',
'Crea Facebook Ad para servicios de remodelación usando PAS:
- PROBLEM: El miedo al desorden, los sobrecostos y el tiempo
- AGITATE: Lo que cuesta esperar (valor de la propiedad, comodidad)
- SOLUTION: Cómo tu empresa elimina esos 3 miedos específicamente
- GUARANTEE: Si ofreces garantía de precio o tiempo, mencionarla
- CTA: "Cotización gratis en 24h"
Cliente: {client_name}'),

('story', 'real_estate', 'instagram', 'RAFA', 8.0, 'open_house',
'Crea secuencia de 3 Stories para promover open house:
STORY 1 (Teaser): Fachada o mejor feature + fecha y hora + countdown timer
STORY 2 (Details): 3 razones para venir · fotos interiores mejores
STORY 3 (CTA): "Confirma tu asistencia" + link o DM + "Cupos limitados"
Urgencia real, no inventada. Si hay cupos limitados, mencionarlo.
Cliente: {client_name}'),

('caption', 'construction', 'instagram', 'RAFA', 7.9, 'behind_the_scenes',
'Escribe caption para post Behind-The-Scenes del proceso constructivo:
- EDUCACIÓN: Explica brevemente qué etapa del proceso se muestra
- EXPERTISE: Menciona por qué se hace así y qué diferencia hace
- HUMANIZACIÓN: Nombra al equipo o al maestro de obra si es posible
- ORGULLO: "Así se construye en {client_name}"
- CTA: Pregunta que invite a comentar sobre el proceso
Tono: experto pero accesible, orgulloso del oficio'),

('email', 'health', 'email', 'RAFA', 7.9, 'nurturing_tips',
'Escribe email para serie de tips de salud (nurturing):
- SUBJECT: Curioso y específico (max 50 chars)
- PERSONAL OPENING: "Hola [Nombre]," + referencia a email anterior
- TIP PRINCIPAL: 1 tip concreto con evidencia breve
- APLICACIÓN: Cómo implementarlo esta semana
- BONUS: Recurso gratuito o próximo tip
- CTA: "Responde este email con tus dudas"
Tono cálido, no corporativo. Sin jerga médica.
Cliente: {client_name}'),

('email', 'real_estate', 'email', 'RAFA', 7.8, 'followup_visit',
'Escribe email de seguimiento para lead que visitó propiedad pero no decidió:
- SUBJECT: Personalizado y curioso (no pushy)
- OPENING: Agradece la visita + referencia específica a algo que le gustó
- VALUE ADD: Información nueva que no sabía en la visita
- OBJECTION HANDLER: Aborda la duda más común sin mencionarla directamente
- SOFT CTA: "¿Tienes 10 minutos esta semana para una llamada rápida?"
Tono: consultor amigo, nunca vendedor presionante
Cliente: {client_name}'),

('ad', 'health', 'facebook', 'RAFA', 7.8, 'wellness_benefits',
'Crea Facebook Ad para servicio de wellness usando beneficios:
- HEADLINE: Beneficio claro y measurable
- OPENING: Identificar el pain point sin dramatizar
- SOLUTION: Cómo tu servicio lo resuelve específicamente
- SOCIAL PROOF: Número de pacientes/clientes o resultado promedio
- CTA: "Agenda tu consulta gratuita"
Cumplir regulaciones de salud: evitar garantías de resultados
Cliente: {client_name}'),

('post', 'construction', 'linkedin', 'RAFA', 7.7, 'case_study',
'Escribe post LinkedIn mostrando proyecto como case study:
- HOOK: Resultado específico en 1 línea
- CHALLENGE: El desafío que tenía el cliente
- APPROACH: Las 2-3 decisiones clave que tomamos
- RESULT: Métricas reales (m², tiempo, presupuesto)
- LESSON: Qué aprendimos o confirmamos
- CTA: "¿Tienes un proyecto similar? Comentá o escríbeme"
Tono: experto reflexivo, no autopromocional. Max 500 palabras.
Cliente: {client_name}'),

('email', 'restaurant', 'email', 'RAFA', 7.7, 'thanks_post_visit',
'Escribe email de agradecimiento post-visita para fomentar retorno:
- SUBJECT: "Gracias por visitarnos, [Nombre]"
- APERTURA: Agradecimiento genuino y personalizado
- PERSONAL TOUCH: Si tienes data, menciona qué pidió o la ocasión
- VALUE: Razón específica para volver (nuevo plato, evento próximo)
- REWARD: Descuento o beneficio exclusivo por ser cliente recurrente
- CTA: "Reserva tu próxima visita con 10% de descuento"
Tono cálido y familiar, como si escribiera el dueño directamente
Cliente: {client_name}'),

('email', 'construction', 'email', 'RAFA', 7.6, 'quote_followup',
'Escribe email de seguimiento después de enviar cotización:
- SUBJECT: "[Nombre], ¿revisaste la propuesta para tu [proyecto]?"
- OPENING: Recap breve de lo que incluye la cotización
- VALUE REMINDER: El mayor beneficio que ofreces vs competencia
- URGENCY: Razón legítima para decidir pronto (disponibilidad, precios)
- FLEXIBILITY: Ofrece ajustar el alcance si el presupuesto es el freno
- CTA: "¿Podemos hablar 15 minutos esta semana?"
Tono: profesional y seguro, nunca desesperado
Cliente: {client_name}'),

('post', 'real_estate', 'linkedin', 'RAFA', 7.5, 'market_expert',
'Escribe post LinkedIn posicionando al agente como experto del mercado:
- HOOK: Dato sorprendente o contraintuitivo del mercado local
- CONTEXTO: Por qué ese dato importa para compradores/inversores
- ANÁLISIS: Tu perspectiva como experto (no como vendedor)
- PREDICCIÓN: Qué crees que va a pasar en los próximos 6-12 meses
- CTA: "¿Qué opinas? Me interesa tu perspectiva"
Posicionamiento: eres el experto, no el vendedor. Max 400 palabras
Cliente: {client_name}'),

('post', 'restaurant', 'google_business', 'RAFA', 7.5, 'gmb_alternating',
'Escribe post corto para Google My Business:
TIPOS (alternar según día):
1. SPECIAL: "Plato del Día: [Nombre] - [Precio]. Solo hoy. Reserva: [teléfono]"
2. EVENTO: "[Evento] este [día] · [Hora] · Reserva requerida: [contacto]"
3. TIP: "¿Sabías que [dato sobre el restaurante]?"
Max 300 palabras. Sin hashtags. Siempre incluir horario o teléfono.
Cliente: {client_name}. Horario: {business_hours}'),

('post', 'health', 'linkedin', 'RAFA', 7.4, 'health_authority',
'Escribe post LinkedIn posicionando al profesional de salud como autoridad:
- HOOK: Tendencia actual en salud que observas en tu práctica
- PERSPECTIVA EXPERTA: Tu análisis profesional (cita literatura si aplica)
- CASO REAL: Ejemplo anonimizado que ilustra el punto
- IMPLICACIÓN: Qué deberían hacer los lectores con esta información
- CTA: "¿Cuántos de ustedes han visto esto en sus pacientes?"
Tono: colega a colega, no maestro a alumno. Max 350 palabras
Cliente: {client_name}. Especialidad: {niche}'),

('hashtags', 'real_estate', 'instagram', 'RAFA', 7.2, 'strategic_set',
'Genera set estratégico de 25-30 hashtags para post de real estate:
CATEGORÍAS A INCLUIR:
- Brand/Location (5-7): Ciudad + tipo de propiedad + nombre de agencia
- Property Type (5-7): #CasaEnVenta #Apartamento etc según propiedad
- Lifestyle (5-7): El estilo de vida que representa la propiedad
- Trending Local (3-5): Hashtags de trending local de la ciudad/país
- Niche (3-4): Hashtags específicos del tipo de cliente objetivo
Mezclar tamaños: 30% grandes (1M+) · 50% medianos (100K-1M) · 20% pequeños (<100K)
Ciudad: {region}. Tipo: {property_type}')

ON CONFLICT (category, vertical, platform, slot_name) DO NOTHING;

-- Verificación: SELECT COUNT(*) FROM prompt_vault; → 30
