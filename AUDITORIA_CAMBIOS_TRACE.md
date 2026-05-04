# Auditoría de cambios — Trace lee hallazgos y propone plan de mejora

Fecha: 2026-05-04

## Alcance
Auditoría enfocada en el trabajo realizado para que **Trace** pueda:
- Leer **múltiples hallazgos** (auditoría, alertas abiertas o texto pegado).
- Generar un **plan de mejora** con acciones correctivas/preventivas, **capacitaciones**, recursos, KPI y verificación.
- Permitir **guardar** automáticamente los planes generados en la base de datos del módulo (tabla `improvement_plans`).

## Archivos impactados
- `app.py` (cambio funcional)

> Nota: durante el desarrollo se generaron cambios locales (p. ej. `__pycache__` y modificación de la BD SQLite) que fueron revertidos para que la entrega quede limpia y reproducible.

## Resumen de lo implementado
### 1) Nuevo flujo “Plan desde hallazgos” dentro de Trace
En el módulo **📌 Plan de mejora**, dentro del expander **🤖 Trace**, se añadió una pestaña:
- **📑 Plan desde hallazgos**

Este flujo permite:
- Seleccionar fuente de hallazgos.
- Previsualizar hallazgos.
- Enviar el conjunto a Trace (OpenAI) para generación estructurada.
- Previsualizar el resultado en tabla.
- Guardar los planes como registros reales en `improvement_plans`.

### 2) Fuentes de hallazgos soportadas
En “📑 Plan desde hallazgos” se implementaron estas fuentes:
- **📄 Leer `AUDITORIA_PROFUNDA.md`**
  - Extrae ítems numerados y con viñetas desde secciones:
    - “Hallazgos críticos corregidos” → prefijo `Hallazgo:`
    - “Limitaciones que permanecen por alcance académico” → prefijo `Limitación:`
- **🔔 Usar alertas abiertas**
  - Convierte registros de `alerts` con `status='Abierta'` en hallazgos tipo:
    - `Alerta abierta: [Severidad] Tipo – Instrumento/Lote: descripción`
  - Permite filtrar por severidad (Todas/Alta/Media/Baja) y elegir cantidad.
- **📄 + 🔔 Auditoría + alertas abiertas**
  - Combina las dos fuentes anteriores y elimina duplicados manteniendo el orden.
- **✍️ Pegar hallazgos**
  - Recibe un hallazgo por línea.

### 3) Generación de plan con estructura JSON
Se añadió un prompt específico para generación en lote:
- `_TRACE_PLAN_SYSTEM`

Trace debe devolver **solo JSON** con el esquema:
- `{"planes": [ ... ]}`

Cada plan incluye:
- `hallazgo`, `tipo_riesgo`, `nivel_riesgo`, `causa_probable`, `accion_correctiva`, `accion_preventiva`,
  `capacitacion`, `recursos`, `indicador_kpi`, `responsable_rol`, `plazo_dias`, `verificacion`.

### 4) Persistencia en la base de datos
Al guardar los planes:
- Se insertan como filas en `improvement_plans`.
- Se evita duplicar por `finding` (si ya existe el mismo texto de hallazgo).
- Se calcula `follow_up_date` como `hoy + plazo_dias` (acotado a 1..365).
- Se guarda `responsable_rol` en el campo `responsible`.
- Se almacena en `evidence` un resumen con:
  - Fuente, capacitación, recursos, KPI, verificación, rol responsable.
- Se registra evento en `audit_log` indicando cuántos guardó y cuántos omitió.

## Cambios técnicos relevantes (alto nivel)
- Helpers nuevos:
  - Normalización de nivel de riesgo (maneja `Critico` vs `Crítico`).
  - Lectura de archivo con fallback de encoding (`utf-8` → `latin-1`).
  - Extracción robusta de listas numeradas (regex `^\d+\.\s+...`).
  - Extracción de hallazgos desde alertas abiertas en SQLite.
  - Formateo del campo `evidence` con elementos adicionales del plan.
- Manejo de fallos:
  - Si Trace no devuelve JSON parseable, se muestra `raw` para diagnóstico.

## Consideraciones y riesgos
- Requiere `OPENAI_API_KEY` configurada en secretos.
- El modelo usado en la integración actual es `gpt-4o-mini`.
- El plan generado es **apoyo académico**: requiere validación humana antes de aplicarse.
- Los hallazgos pegados o provenientes de alertas podrían contener información sensible; evitar datos de pacientes.

## Verificación mínima recomendada
1. Ejecutar la app:
   - `python -m streamlit run app.py`
2. Ir a **📌 Plan de mejora** → expander **🤖 Trace** → **📑 Plan desde hallazgos**.
3. Probar con:
   - “📄 Leer AUDITORIA_PROFUNDA.md” y generar + guardar.
   - Si existen alertas abiertas, probar “🔔 Usar alertas abiertas”.
4. Confirmar que aparecen registros nuevos en la tabla del módulo y que `audit_log` registra el evento.
