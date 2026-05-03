import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import io

DB_PATH = "reprotrace_basic_360.db"

STAGES = [
    "Recepción",
    "Limpieza y descontaminación",
    "Inspección funcional",
    "Empaque",
    "Esterilización",
    "Validación / liberación de carga",
    "Almacenamiento",
    "Distribución"
]

USERS = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "central": {"password": "central123", "role": "Personal de central"},
    "docente": {"password": "docente123", "role": "Docente/Tutor"}
}

STAGE_REQUIRED_PREVIOUS = {
    "Limpieza y descontaminación": "Recepción",
    "Inspección funcional": "Limpieza y descontaminación",
    "Empaque": "Inspección funcional",
    "Esterilización": "Empaque",
    "Validación / liberación de carga": "Esterilización",
    "Almacenamiento": "Validación / liberación de carga",
    "Distribución": "Almacenamiento"
}

RISK_MATRIX = [
    ["Registro incompleto", "Media", "Pérdida de trazabilidad", "Campos obligatorios y alertas"],
    ["Instrumental dañado no detectado", "Alta", "Riesgo para procedimiento quirúrgico", "Inspección funcional obligatoria"],
    ["Ciclo de esterilización rechazado", "Alta", "Material no liberable", "Bloqueo de liberación y reproceso"],
    ["Indicador químico no conforme", "Alta", "Carga no validada", "Registrar resultado y generar alerta"],
    ["Almacenamiento incorrecto", "Media", "Pérdida de esterilidad", "Registro de ubicación y estado de empaque"],
    ["Distribución sin lote", "Media", "Imposibilidad de rastrear el instrumental", "Lote/carga obligatorio"]
]


def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def execute(query, params=()):
    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


def query_df(query, params=()):
    conn = connect()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS instruments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        spaulding_classification TEXT,
        service_origin TEXT,
        quantity INTEGER DEFAULT 1,
        status TEXT DEFAULT 'Activo',
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS process_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT NOT NULL,
        batch_code TEXT NOT NULL,
        stage TEXT NOT NULL,
        responsible TEXT NOT NULL,
        start_datetime TEXT,
        end_datetime TEXT,
        duration_minutes REAL,
        complies TEXT,
        result TEXT,
        cleaning_method TEXT,
        inspection_status TEXT,
        package_type TEXT,
        chemical_indicator TEXT,
        biological_indicator TEXT,
        sterilizer_id TEXT,
        cycle_type TEXT,
        temperature REAL,
        pressure REAL,
        storage_location TEXT,
        expiration_date TEXT,
        destination_service TEXT,
        observations TEXT,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT,
        batch_code TEXT,
        alert_type TEXT,
        severity TEXT,
        description TEXT,
        status TEXT DEFAULT 'Abierta',
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS staff_survey (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        experience_years REAL,
        q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
        q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()


def seed_demo_data():
    demo = [
        ("IQ-001", "Pinza Kelly", "Prensión", "Crítico", "Cirugía general", 4, "Activo"),
        ("IQ-002", "Tijera Mayo", "Corte", "Crítico", "Ginecología", 2, "Activo"),
        ("IQ-003", "Porta agujas", "Sutura", "Crítico", "Ortopedia", 3, "Activo"),
        ("IQ-004", "Separador Farabeuf", "Separación", "Crítico", "Urgencias", 2, "Activo"),
    ]
    for row in demo:
        try:
            execute('''INSERT INTO instruments (code, name, category, spaulding_classification, service_origin, quantity, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (*row, datetime.now().isoformat()))
        except sqlite3.IntegrityError:
            pass


def add_alert(code, batch, alert_type, severity, description):
    execute('''INSERT INTO alerts (instrument_code, batch_code, alert_type, severity, description, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'Abierta', ?)''',
            (code, batch, alert_type, severity, description, datetime.now().isoformat()))


def completed_stages(code, batch):
    df = query_df("SELECT stage FROM process_records WHERE instrument_code=? AND batch_code=?", (code, batch))
    return df['stage'].tolist() if not df.empty else []


def validate_stage_order(code, batch, stage):
    prev = STAGE_REQUIRED_PREVIOUS.get(stage)
    if not prev:
        return True, ""
    stages = completed_stages(code, batch)
    if prev not in stages:
        return False, f"Antes de registrar '{stage}' debe existir la etapa previa: '{prev}'."
    return True, ""


def login_screen():
    st.title("ReproTrace Basic 360°")
    st.subheader("Sistema académico de monitoreo y trazabilidad para central de reprocesamiento")
    st.info("Usuarios de prueba: admin/admin123 | central/central123 | docente/docente123")
    with st.sidebar:
        st.title("Acceso")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if u in USERS and USERS[u]['password'] == p:
                st.session_state['login'] = True
                st.session_state['user'] = u
                st.session_state['role'] = USERS[u]['role']
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")


def header():
    st.title("ReproTrace Basic 360°")
    st.caption("Prototipo académico. No reemplaza sistemas hospitalarios reales ni valida clínicamente la esterilización.")
    st.sidebar.success(f"{st.session_state['user']} | {st.session_state['role']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()


def dashboard():
    st.header("Panel principal")
    ins = query_df("SELECT * FROM instruments")
    rec = query_df("SELECT * FROM process_records")
    alerts = query_df("SELECT * FROM alerts WHERE status='Abierta'")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Instrumentales", len(ins))
    c2.metric("Registros de proceso", len(rec))
    c3.metric("Alertas abiertas", len(alerts))
    comp = ((rec['complies'] == 'Sí').mean() * 100) if not rec.empty else 0
    c4.metric("Cumplimiento global", f"{comp:.1f}%")
    st.subheader("Ruta esperada del reprocesamiento")
    st.write(" → ".join(STAGES))
    st.subheader("Últimos registros")
    st.dataframe(rec.sort_values('created_at', ascending=False).head(15) if not rec.empty else rec, use_container_width=True)
    st.subheader("Alertas abiertas")
    st.dataframe(alerts, use_container_width=True)


def instruments_module():
    st.header("1. Registro maestro de instrumental")
    with st.form("instrument_form"):
        c1, c2 = st.columns(2)
        code = c1.text_input("Código único", placeholder="IQ-005")
        name = c2.text_input("Nombre", placeholder="Pinza Allis")
        category = c1.text_input("Categoría", placeholder="Prensión, corte, separación...")
        spaulding = c2.selectbox("Clasificación de Spaulding", ["Crítico", "Semicrítico", "No crítico"])
        service = c1.text_input("Servicio de origen")
        qty = c2.number_input("Cantidad", min_value=1, value=1)
        status = c2.selectbox("Estado", ["Activo", "Dañado", "Retirado", "En mantenimiento"])
        if st.form_submit_button("Guardar"):
            if not code or not name:
                st.error("Código y nombre son obligatorios.")
            else:
                try:
                    execute('''INSERT INTO instruments (code, name, category, spaulding_classification, service_origin, quantity, status, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (code, name, category, spaulding, service, qty, status, datetime.now().isoformat()))
                    st.success("Instrumental guardado.")
                except sqlite3.IntegrityError:
                    st.error("Ya existe ese código.")
    st.dataframe(query_df("SELECT * FROM instruments ORDER BY created_at DESC"), use_container_width=True)


def process_module():
    st.header("2. Registro de etapas del reprocesamiento")
    instruments = query_df("SELECT code, name FROM instruments WHERE status='Activo'")
    if instruments.empty:
        st.warning("Primero registre un instrumental activo.")
        return
    options = [f"{r.code} - {r.name}" for _, r in instruments.iterrows()]
    with st.form("process_form"):
        selected = st.selectbox("Instrumental", options)
        code = selected.split(" - ")[0]
        batch = st.text_input("Lote / carga", placeholder="LOTE-2026-001")
        stage = st.selectbox("Etapa", STAGES)
        responsible = st.text_input("Responsable")
        c1, c2, c3, c4 = st.columns(4)
        sd = c1.date_input("Fecha inicio", value=date.today())
        stime = c2.time_input("Hora inicio")
        ed = c3.date_input("Fecha fin", value=date.today())
        etime = c4.time_input("Hora fin")
        complies = st.radio("¿Cumple protocolo?", ["Sí", "No"], horizontal=True)
        result = st.selectbox("Resultado", ["Aprobado", "Rechazado", "Pendiente", "No aplica"])
        st.divider()
        st.markdown("**Campos específicos por etapa**")
        cleaning_method = inspection_status = package_type = chemical_indicator = biological_indicator = ""
        sterilizer_id = cycle_type = storage_location = destination_service = ""
        temperature = pressure = None
        expiration_date = ""
        if stage == "Limpieza y descontaminación":
            cleaning_method = st.selectbox("Método de limpieza", ["Manual", "Ultrasónica", "Automatizada", "Mixta"])
        if stage == "Inspección funcional":
            inspection_status = st.selectbox("Estado del instrumental", ["Completo y funcional", "Incompleto", "Dañado", "Oxidado", "Requiere mantenimiento"])
        if stage == "Empaque":
            package_type = st.selectbox("Tipo de empaque", ["Papel grado médico", "Tela", "Contenedor", "Bolsa mixta", "Otro"])
            chemical_indicator = st.selectbox("Indicador químico externo/interno", ["Conforme", "No conforme", "No aplica"])
        if stage == "Esterilización":
            sterilizer_id = st.text_input("Equipo esterilizador")
            cycle_type = st.selectbox("Tipo de ciclo", ["Vapor", "Baja temperatura", "Óxido de etileno", "Peróxido de hidrógeno", "Otro"])
            temperature = st.number_input("Temperatura registrada °C", min_value=0.0, max_value=200.0, value=121.0)
            pressure = st.number_input("Presión registrada", min_value=0.0, value=1.0)
        if stage == "Validación / liberación de carga":
            chemical_indicator = st.selectbox("Indicador químico", ["Conforme", "No conforme", "No aplica"])
            biological_indicator = st.selectbox("Indicador biológico", ["Conforme", "No conforme", "Pendiente", "No aplica"])
        if stage == "Almacenamiento":
            storage_location = st.text_input("Ubicación de almacenamiento", placeholder="Estante A - Nivel 2")
            expiration_date = st.date_input("Fecha de vencimiento / vida útil", value=date.today() + timedelta(days=30)).isoformat()
        if stage == "Distribución":
            destination_service = st.text_input("Servicio destino", placeholder="Quirófano 1 / Cirugía general")
        observations = st.text_area("Observaciones")
        submit = st.form_submit_button("Guardar etapa")
        if submit:
            if not batch or not responsible:
                st.error("Lote/carga y responsable son obligatorios.")
            else:
                ok_order, msg = validate_stage_order(code, batch, stage)
                if not ok_order:
                    st.warning(msg + " Se guardará como desviación académica si continúa.")
                start_dt = datetime.combine(sd, stime)
                end_dt = datetime.combine(ed, etime)
                if end_dt < start_dt:
                    st.error("La hora final no puede ser anterior a la hora inicial.")
                    return
                duration = (end_dt - start_dt).total_seconds() / 60
                execute('''INSERT INTO process_records (
                    instrument_code, batch_code, stage, responsible, start_datetime, end_datetime, duration_minutes, complies, result,
                    cleaning_method, inspection_status, package_type, chemical_indicator, biological_indicator, sterilizer_id, cycle_type,
                    temperature, pressure, storage_location, expiration_date, destination_service, observations, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (code, batch, stage, responsible, start_dt.isoformat(), end_dt.isoformat(), duration, complies, result,
                     cleaning_method, inspection_status, package_type, chemical_indicator, biological_indicator, sterilizer_id, cycle_type,
                     temperature, pressure, storage_location, expiration_date, destination_service, observations, datetime.now().isoformat()))
                if not ok_order:
                    add_alert(code, batch, "Secuencia incompleta", "Media", msg)
                if complies == "No":
                    add_alert(code, batch, "Incumplimiento de protocolo", "Alta", f"No cumple en {stage}. {observations}")
                if result == "Rechazado":
                    add_alert(code, batch, "Resultado rechazado", "Alta", f"Resultado rechazado en {stage}. Requiere revisión o reproceso.")
                if inspection_status in ["Incompleto", "Dañado", "Oxidado", "Requiere mantenimiento"]:
                    add_alert(code, batch, "Novedad del instrumental", "Alta", inspection_status)
                if chemical_indicator == "No conforme" or biological_indicator == "No conforme":
                    add_alert(code, batch, "Indicador no conforme", "Alta", f"Indicador no conforme en {stage}.")
                st.success("Etapa registrada.")
    st.dataframe(query_df("SELECT * FROM process_records ORDER BY created_at DESC LIMIT 30"), use_container_width=True)


def traceability_module():
    st.header("3. Consulta de trazabilidad")
    rec = query_df("SELECT DISTINCT instrument_code, batch_code FROM process_records ORDER BY batch_code")
    if rec.empty:
        st.warning("No hay registros.")
        return
    key = st.selectbox("Seleccione instrumental/lote", [f"{r.instrument_code} | {r.batch_code}" for _, r in rec.iterrows()])
    code, batch = [x.strip() for x in key.split('|')]
    df = query_df("SELECT * FROM process_records WHERE instrument_code=? AND batch_code=? ORDER BY start_datetime", (code, batch))
    st.subheader("Historial completo")
    st.dataframe(df, use_container_width=True)
    stages_done = df['stage'].tolist()
    missing = [s for s in STAGES if s not in stages_done]
    if missing:
        st.warning("Ruta incompleta. Faltan: " + ", ".join(missing))
    else:
        st.success("Ruta completa de trazabilidad.")
    st.subheader("Línea de tiempo")
    for _, r in df.iterrows():
        st.markdown(f"**{r['stage']}** | {r['start_datetime']} → {r['end_datetime']} | {r['duration_minutes']:.1f} min | Responsable: {r['responsible']} | Cumple: {r['complies']} | Resultado: {r['result']}")
    alerts = query_df("SELECT * FROM alerts WHERE instrument_code=? AND batch_code=?", (code, batch))
    st.subheader("Alertas asociadas")
    st.dataframe(alerts, use_container_width=True)


def alerts_module():
    st.header("4. Alertas y novedades")
    alerts = query_df("SELECT * FROM alerts ORDER BY created_at DESC")
    st.dataframe(alerts, use_container_width=True)
    open_alerts = query_df("SELECT id, alert_type, instrument_code, batch_code FROM alerts WHERE status='Abierta'")
    if not open_alerts.empty:
        selected = st.selectbox("Cerrar alerta", [f"{r.id} | {r.alert_type} | {r.instrument_code} | {r.batch_code}" for _, r in open_alerts.iterrows()])
        if st.button("Marcar como cerrada"):
            aid = int(selected.split('|')[0].strip())
            execute("UPDATE alerts SET status='Cerrada' WHERE id=?", (aid,))
            st.success("Alerta cerrada.")
            st.rerun()


def reports_module():
    st.header("5. Reportes e indicadores")
    rec = query_df("SELECT * FROM process_records")
    alerts = query_df("SELECT * FROM alerts")
    survey = query_df("SELECT * FROM staff_survey")
    if rec.empty:
        st.warning("No hay registros para reportar.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", len(rec))
    c2.metric("Cumplimiento", f"{(rec['complies'] == 'Sí').mean() * 100:.1f}%")
    c3.metric("Tiempo promedio", f"{rec['duration_minutes'].mean():.1f} min")
    c4.metric("Alertas", len(alerts))
    st.subheader("Cumplimiento por etapa")
    comp = rec.groupby('stage')['complies'].apply(lambda x: (x == 'Sí').mean() * 100).reset_index(name='Cumplimiento %')
    st.dataframe(comp, use_container_width=True)
    st.bar_chart(comp.set_index('stage'))
    st.subheader("Tiempo promedio por etapa")
    tm = rec.groupby('stage')['duration_minutes'].mean().reset_index(name='Minutos promedio')
    st.dataframe(tm, use_container_width=True)
    st.bar_chart(tm.set_index('stage'))
    st.subheader("Alertas por tipo")
    if not alerts.empty:
        st.dataframe(alerts.groupby(['alert_type', 'severity', 'status']).size().reset_index(name='Cantidad'), use_container_width=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        rec.to_excel(writer, sheet_name='Registros', index=False)
        alerts.to_excel(writer, sheet_name='Alertas', index=False)
        comp.to_excel(writer, sheet_name='Cumplimiento', index=False)
        tm.to_excel(writer, sheet_name='Tiempos', index=False)
        survey.to_excel(writer, sheet_name='Encuestas', index=False)
    st.download_button("Descargar reporte Excel", output.getvalue(), "reporte_reprotrace_basic_360.xlsx")


def survey_module():
    st.header("6. Encuesta de percepción")
    questions = [
        "El software es fácil de usar.",
        "Facilita el registro de los procesos.",
        "Reduce errores de registro.",
        "Mejora la trazabilidad del instrumental.",
        "Permite mejor control de las etapas.",
        "Optimiza el tiempo de los procesos.",
        "Me siento cómodo(a) usando el software.",
        "Contribuye indirectamente a la seguridad del paciente.",
        "Mejora la organización del trabajo.",
        "Recomendaría su uso académico/institucional."
    ]
    with st.form("survey"):
        role = st.text_input("Cargo")
        exp = st.number_input("Años de experiencia", min_value=0.0, step=0.5)
        ans = [st.slider(f"{i+1}. {q}", 1, 5, 3) for i, q in enumerate(questions)]
        if st.form_submit_button("Guardar encuesta"):
            execute('''INSERT INTO staff_survey (role, experience_years, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (role, exp, *ans, datetime.now().isoformat()))
            st.success("Encuesta guardada.")
    df = query_df("SELECT * FROM staff_survey")
    if not df.empty:
        means = df[[f'q{i}' for i in range(1, 11)]].mean().reset_index(name='Promedio')
        st.dataframe(means, use_container_width=True)
        st.bar_chart(means.set_index('index'))


def risk_module():
    st.header("7. Matriz de riesgos y plan de mejora")
    df = pd.DataFrame(RISK_MATRIX, columns=['Riesgo', 'Prioridad', 'Impacto', 'Mitigación en el software'])
    st.dataframe(df, use_container_width=True)
    st.markdown("**Uso en la sustentación:** esta matriz permite explicar que el software no solo registra datos, sino que ayuda a identificar riesgos operativos y oportunidades de mejora en la central de reprocesamiento.")


def tests_module():
    st.header("8. Plan de pruebas básicas")
    tests = pd.DataFrame([
        ["Funcionamiento", "Registrar las ocho etapas", "Todas las etapas quedan guardadas"],
        ["Secuencia", "Intentar registrar empaque sin inspección", "El sistema advierte secuencia incompleta"],
        ["Trazabilidad", "Consultar por instrumental/lote", "Se reconstruye la línea de tiempo"],
        ["Alertas", "Registrar no cumple, rechazado o indicador no conforme", "Se genera alerta"],
        ["Tiempos", "Registrar inicio y fin", "Calcula duración en minutos"],
        ["Reporte", "Exportar Excel", "Archivo con registros, alertas e indicadores"],
        ["Percepción", "Aplicar encuesta Likert", "Promedios por pregunta"]
    ], columns=['Prueba', 'Procedimiento', 'Criterio de aprobación'])
    st.dataframe(tests, use_container_width=True)


def main():
    st.set_page_config(page_title='ReproTrace Basic 360°', page_icon='🏥', layout='wide')
    init_db()
    seed_demo_data()
    if 'login' not in st.session_state:
        st.session_state['login'] = False
    if not st.session_state['login']:
        login_screen()
        return
    header()
    menu = st.sidebar.radio('Menú', [
        'Panel principal', 'Registro de instrumental', 'Registro del proceso', 'Consulta de trazabilidad',
        'Alertas y novedades', 'Reportes e indicadores', 'Encuesta de percepción', 'Matriz de riesgos', 'Plan de pruebas'
    ])
    if menu == 'Panel principal':
        dashboard()
    elif menu == 'Registro de instrumental':
        instruments_module()
    elif menu == 'Registro del proceso':
        process_module()
    elif menu == 'Consulta de trazabilidad':
        traceability_module()
    elif menu == 'Alertas y novedades':
        alerts_module()
    elif menu == 'Reportes e indicadores':
        reports_module()
    elif menu == 'Encuesta de percepción':
        survey_module()
    elif menu == 'Matriz de riesgos':
        risk_module()
    elif menu == 'Plan de pruebas':
        tests_module()


if __name__ == '__main__':
    main()
