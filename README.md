# ReproTrace Basic 360° — v2.0

**Prototipo académico** para monitoreo y trazabilidad completa del instrumental quirúrgico en centrales de reprocesamiento hospitalario.

> **Advertencia académica:** Este sistema no constituye un dispositivo médico, no reemplaza sistemas clínicos institucionales (HIS/LIS) y no valida clínicamente ningún proceso de esterilización. Su finalidad es exclusivamente **formativa, investigativa y demostrativa**.

---

## Institución y autoría
- **Universidad Libre Seccional Barranquilla**
- Programa de Instrumentación Quirúrgica
- **Autor:** Anderson Diaz Perez
- **Apoyo académico:** Ligia Elena Cabana Cabana · Cesar Augusto Vásquez Hurtado

---

## Módulos (v2.0 — 12 módulos)
| # | Módulo | Descripción |
|---|--------|-------------|
| 1 | Panel principal | KPIs globales, gráficas e histograma de alertas activas |
| 2 | Instrumental | Registro maestro con clasificación de Spaulding |
| 3 | Reprocesamiento | Registro de 8 etapas con campos específicos por fase |
| 4 | Trazabilidad | Consulta por código/lote con línea de tiempo y mapa de estado |
| 5 | Alertas 🔴 | Sistema de alertas rojas con severidad y estado de cierre |
| 6 | Plan de mejora | Auto-recomendaciones basadas en alertas; gestión de acciones correctivas |
| 7 | Reportes | Exportación Excel (7 hojas) y PDF académico con gráficas |
| 8 | Encuesta | Percepción del personal + gráfica de resultados |
| 9 | Auditoría | Trazabilidad de acciones del sistema (audit log) |
| 10 | Configuración | Carga de datos demo; reset controlado; descarga de backup ZIP |
| 11 | Plan de pruebas | Checklist de 14 puntos con estado de ejecución |
| 12 | Limitaciones | Tabla detallada de limitaciones del prototipo académico |

### Las 8 etapas del reprocesamiento monitoreadas
Recepción → Limpieza y descontaminación → Inspección funcional → Empaque → Esterilización → Validación / liberación de carga → Almacenamiento → Distribución

---

## Roles de acceso
| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Administrador (acceso completo) |
| `central` | `central123` | Operario de central |
| `docente` | `docente123` | Docente / investigador |

---

## Instalación local
```bash
git clone <url-del-repo>
cd reprotrace-basic-360
pip install -r requirements.txt
python -m streamlit run app.py
```

> **Nota:** use `python -m streamlit` si `streamlit` no está en el PATH del sistema.

## Dependencias
```
pandas==2.2.2
xlsxwriter==3.2.0
matplotlib>=3.8.0
fpdf2>=2.7.9
openai>=1.30.0
pypdf>=4.2.0
python-docx>=1.1.2
```
`streamlit` es gestionado por Streamlit Cloud y **no se incluye** en `requirements.txt`.

---

## Trace 🤖 — Adjuntar y analizar documentos
Dentro del módulo **Plan de mejora** → expander **🤖 Trace – Asistente IA de Reprocesamiento**, hay una pestaña **📎 Documentos** que permite:
- Adjuntar uno o varios archivos **PDF/DOCX/TXT/MD/CSV**.
- Extraer texto y enviarlo como contexto a Trace para análisis (resumen, hallazgos, recomendaciones, etc.).

> **Privacidad:** al analizar, el contenido del documento se envía a OpenAI. Evite información sensible.

### Configurar la API Key
- En Streamlit Cloud: Settings → Secrets → añadir `OPENAI_API_KEY`.
- En local: crear `.streamlit/secrets.toml` con:
	```toml
	OPENAI_API_KEY = "tu_clave"
	```

---

## Despliegue en Streamlit Cloud
1. Hacer fork/push del repositorio a GitHub.
2. Crear una nueva app en [share.streamlit.io](https://share.streamlit.io) apuntando a `app.py`.
3. No incluir `streamlit` en `requirements.txt` (Streamlit Cloud lo gestiona automáticamente).

> **Persistencia:** En Streamlit Cloud el archivo SQLite (`reprotrace_basic_360.db`) se recrea en cada reinicio. Use la función **"Cargar datos demo"** del módulo Configuración para repoblar la base de datos.

---

## Base de datos
SQLite con WAL mode (`PRAGMA journal_mode=WAL`) y timeout de 20 s. Tablas:
- `instruments` — Registro maestro de instrumental
- `process_records` — Registros de etapas del reprocesamiento
- `alerts` — Alertas y novedades del proceso
- `improvement_plans` — Planes de mejora con acciones correctivas
- `staff_survey` — Respuestas de encuesta de percepción
- `audit_log` — Log de auditoría de todas las acciones
- `login_sessions` — Registro de sesiones de inicio/cierre de sesión

---

## Cambios v2.0 respecto a v1
- Campos específicos por etapa (indicador químico, biológico, temperatura, presión, etc.)
- Gráficas con matplotlib: cumplimiento, tiempos, alertas, encuesta
- Exportación PDF académico con portada institucional y gráficas embebidas
- Exportación Excel con 7 hojas (incluye hoja de Indicadores y Trazabilidad)
- Sistema de alertas rojas con auto-recomendaciones de mejora
- Validación de secuencia lógica de etapas (bloquea saltarse etapas previas)
- Audit log completo de todas las acciones del sistema
- Módulo de configuración con backup ZIP descargable
- Módulo de limitaciones académicas detallado
