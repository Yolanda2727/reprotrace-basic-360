# =============================================================================
# ReproTrace Basic 360°  |  v2.0 – 2026
# Prototipo académico – Universidad Libre Seccional Barranquilla
# Autor principal: Anderson Diaz Perez
# Apoyo académico: Ligia Elena Cabana Cabana · Cesar Augusto Vásquez Hurtado
# Facultad de Ciencias de la Salud, Exactas y Naturales
# Programa de Instrumentación Quirúrgica – Barranquilla, Colombia
# =============================================================================

import streamlit as st
import pandas as pd
import sqlite3
import io, zipfile, os
from datetime import datetime, date, timedelta
from textwrap import wrap

@st.cache_resource
def _get_plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as _plt
    return _plt

# ─── Constantes ──────────────────────────────────────────────────────────────
DB_PATH   = "reprotrace_basic_360.db"
APP_NAME  = "ReproTrace Basic 360°"
VERSION   = "v2.0 – 2026"
NOTA_ACAD = (
    "ReproTrace Basic 360° es un prototipo académico y demostrativo. "
    "No constituye un dispositivo médico, no reemplaza sistemas hospitalarios "
    "certificados y no ha sido validado para uso clínico asistencial."
)

STAGES = [
    "Recepción", "Limpieza y descontaminación", "Inspección funcional",
    "Empaque", "Esterilización", "Validación / liberación de carga",
    "Almacenamiento", "Distribución",
]

STAGE_REQUIRED = {
    "Limpieza y descontaminación":    "Recepción",
    "Inspección funcional":           "Limpieza y descontaminación",
    "Empaque":                        "Inspección funcional",
    "Esterilización":                 "Empaque",
    "Validación / liberación de carga": "Esterilización",
    "Almacenamiento":                 "Validación / liberación de carga",
    "Distribución":                   "Almacenamiento",
}

USERS = {
    "admin":   {"password": "admin123",   "role": "Administrador"},
    "central": {"password": "central123", "role": "Personal de central"},
    "docente": {"password": "docente123", "role": "Docente/Tutor"},
}

SEV_ICON  = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}

AUTO_REC = {
    "Indicador biológico no conforme": "Rechazar la carga, inmovilizar el material, repetir el ciclo y notificar al coordinador.",
    "Instrumental dañado":             "Retirar del circuito, reportar novedad, verificar el set y documentar mantenimiento.",
    "Validación pendiente":            "No distribuir hasta completar la liberación de carga.",
    "Trazabilidad incompleta":         "Revisar registros por etapa, responsables, lote y fechas antes de liberar.",
    "Ciclo rechazado":                 "Reprocesar la carga, documentar causa y verificar parámetros del equipo.",
    "Limpieza no conforme":            "Rechazar etapa, identificar fallo, repetir con método adecuado y documentar.",
}

# ─── Base de datos ───────────────────────────────────────────────────────────
def connect():
    c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=20)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c

def execute(q, p=()):
    c = connect()
    try:
        c.cursor().execute(q, p); c.commit()
    finally:
        c.close()

def query_df(q, p=()):
    c = connect()
    try:
        df = pd.read_sql_query(q, c, params=p)
    finally:
        c.close()
    return df

@st.cache_resource
def init_db():
    c = connect(); cur = c.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS instruments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, category TEXT,
        spaulding TEXT, service_origin TEXT, quantity INTEGER DEFAULT 1,
        status TEXT DEFAULT 'Activo', observations TEXT,
        registered_by TEXT, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS process_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT NOT NULL, batch_code TEXT NOT NULL,
        stage TEXT NOT NULL, responsible TEXT NOT NULL,
        start_datetime TEXT, end_datetime TEXT, duration_minutes REAL,
        complies TEXT, result TEXT,
        reception_origin TEXT, reception_initial_state TEXT, reception_quantity INTEGER,
        cleaning_method TEXT, cleaning_complies TEXT, cleaning_novelties TEXT,
        inspection_status TEXT,
        package_type TEXT, chem_indicator_ext TEXT, chem_indicator_int TEXT,
        sterilizer_id TEXT, cycle_type TEXT, temperature REAL, pressure REAL,
        exposure_time REAL, load_number TEXT,
        physical_indicator TEXT, chemical_indicator TEXT,
        biological_indicator TEXT, release_result TEXT,
        storage_location TEXT, storage_date TEXT, package_condition TEXT,
        expiration_date TEXT,
        destination_service TEXT, delivery_responsible TEXT,
        reception_responsible TEXT, package_state_delivery TEXT,
        observations TEXT, registered_by TEXT, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT, batch_code TEXT,
        alert_type TEXT, severity TEXT, description TEXT,
        status TEXT DEFAULT 'Abierta',
        closed_by TEXT, closed_at TEXT, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS staff_survey (
        id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, experience_years REAL,
        q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
        q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
        comments TEXT, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS improvement_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding TEXT NOT NULL, risk_type TEXT, risk_level TEXT,
        probable_cause TEXT, corrective_action TEXT, preventive_action TEXT,
        responsible TEXT, follow_up_date TEXT,
        state TEXT DEFAULT 'Pendiente', evidence TEXT,
        registered_by TEXT, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, action TEXT, module TEXT,
        description TEXT, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS login_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL, role TEXT NOT NULL,
        event TEXT NOT NULL, timestamp TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        role TEXT NOT NULL DEFAULT 'Personal de central',
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT)""")
    c.commit(); c.close()

def seed_demo_data():
    demo = [
        ("IQ-001","Pinza Kelly",       "Prensión",  "Crítico","Cirugía general",4,"Activo"),
        ("IQ-002","Tijera Mayo",        "Corte",     "Crítico","Ginecología",    2,"Activo"),
        ("IQ-003","Porta agujas",       "Sutura",    "Crítico","Ortopedia",      3,"Activo"),
        ("IQ-004","Separador Farabeuf","Separación", "Crítico","Urgencias",      2,"Activo"),
    ]
    for r in demo:
        try:
            execute("""INSERT INTO instruments
                (code,name,category,spaulding,service_origin,quantity,status,registered_by,created_at)
                VALUES(?,?,?,?,?,?,?,'sistema',?)""", (*r, datetime.now().isoformat()))
        except sqlite3.IntegrityError:
            pass

# ─── Helpers ─────────────────────────────────────────────────────────────────
def audit(user, action, module, desc=""):
    execute("INSERT INTO audit_log(username,action,module,description,created_at) VALUES(?,?,?,?,?)",
            (user, action, module, desc, datetime.now().isoformat()))

def _check_password(plain, stored):
    """Compara contraseña plana con hash bcrypt o texto plano (usuarios hardcoded)."""
    try:
        import bcrypt
        if stored.startswith("$2b$") or stored.startswith("$2a$"):
            return bcrypt.checkpw(plain.encode(), stored.encode())
    except ImportError:
        pass
    return plain == stored

def _hash_password(plain):
    """Genera hash bcrypt si disponible, sino devuelve texto plano."""
    try:
        import bcrypt
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        return plain

def get_user(username):
    """Busca usuario en tabla BD. Retorna dict con password y role, o None."""
    df = query_df("SELECT * FROM users WHERE username=? AND active=1", (username,))
    if not df.empty:
        row = df.iloc[0]
        return {"password": row["password"], "role": row["role"], "full_name": row.get("full_name","")}
    return None

def register_user(username, password, full_name, role):
    """Registra nuevo usuario. Retorna (True,'') o (False, msg_error)."""
    if username in USERS:
        return False, "Ese nombre de usuario está reservado."
    existing = query_df("SELECT id FROM users WHERE username=?", (username,))
    if not existing.empty:
        return False, "El usuario ya existe."
    if len(username) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
    hashed = _hash_password(password)
    execute("""INSERT INTO users(username,password,full_name,role,active,created_at)
               VALUES(?,?,?,?,1,?)""",
            (username.strip().lower(), hashed, full_name.strip(), role, datetime.now().isoformat()))
    return True, ""

def add_alert(code, batch, atype, sev, desc):
    execute("""INSERT INTO alerts(instrument_code,batch_code,alert_type,severity,description,status,created_at)
               VALUES(?,?,?,?,?,'Abierta',?)""",
            (code, batch, atype, sev, desc, datetime.now().isoformat()))

def completed_stages(code, batch):
    df = query_df("SELECT stage FROM process_records WHERE instrument_code=? AND batch_code=?",(code,batch))
    return df["stage"].tolist() if not df.empty else []

def validate_stage_order(code, batch, stage):
    prev = STAGE_REQUIRED.get(stage)
    if not prev: return True,""
    if prev not in completed_stages(code, batch):
        return False, f"Debe registrar primero: '{prev}'."
    return True,""

def check_and_recommend():
    alerts = query_df("SELECT * FROM alerts WHERE status='Abierta' AND severity='Alta'")
    exist  = set(query_df("SELECT finding FROM improvement_plans")["finding"].tolist()) if not query_df("SELECT finding FROM improvement_plans").empty else set()
    for _, row in alerts.iterrows():
        finding = f"Alerta: {row['alert_type']} – {row['instrument_code']} / {row['batch_code']}"
        if finding in exist: continue
        rec = next((v for k,v in AUTO_REC.items() if k.lower() in row["alert_type"].lower()), "Revisar proceso y documentar causa raíz.")
        execute("""INSERT INTO improvement_plans(finding,risk_type,risk_level,corrective_action,state,registered_by,created_at)
                   VALUES(?,?,?,?,'Pendiente','sistema',?)""",
                (finding, row["alert_type"], "Alta", rec, datetime.now().isoformat()))

# ─── Gráficas ─────────────────────────────────────────────────────────────────
def fig_bytes(fig):
    buf=io.BytesIO(); fig.savefig(buf,format="png",bbox_inches="tight",dpi=150); buf.seek(0); return buf.read()

def chart_complies(rec):
    plt=_get_plt()
    data=rec.groupby("stage")["complies"].apply(lambda x:(x=="Sí").mean()*100)
    fig,ax=plt.subplots(figsize=(8,4)); data.plot(kind="bar",ax=ax,color="steelblue",edgecolor="white")
    ax.set_title("Cumplimiento por etapa (%)"); ax.set_ylabel("%"); ax.set_ylim(0,110)
    ax.set_xticklabels(["\n".join(wrap(l,12)) for l in data.index],rotation=0,fontsize=8)
    ax.grid(axis="y",alpha=0.4); plt.tight_layout(); return fig

def chart_time(rec):
    plt=_get_plt()
    data=rec.groupby("stage")["duration_minutes"].mean()
    fig,ax=plt.subplots(figsize=(8,4)); data.plot(kind="bar",ax=ax,color="darkorange",edgecolor="white")
    ax.set_title("Tiempo promedio por etapa (min)"); ax.set_ylabel("Minutos")
    ax.set_xticklabels(["\n".join(wrap(l,12)) for l in data.index],rotation=0,fontsize=8)
    ax.grid(axis="y",alpha=0.4); plt.tight_layout(); return fig

def chart_alerts(alerts):
    plt=_get_plt()
    data=alerts["severity"].value_counts()
    clrs={"Alta":"#d9534f","Media":"#f0ad4e","Baja":"#5cb85c"}
    fig,ax=plt.subplots(figsize=(5,5))
    ax.pie(data.values,labels=data.index,colors=[clrs.get(s,"gray") for s in data.index],autopct="%1.0f%%",startangle=90)
    ax.set_title("Alertas por severidad"); plt.tight_layout(); return fig

def chart_survey(df):
    plt=_get_plt()
    means=df[[f"q{i}" for i in range(1,11)]].mean().values
    fig,ax=plt.subplots(figsize=(8,4))
    ax.bar([f"P{i}" for i in range(1,11)],means,color="teal",edgecolor="white")
    ax.set_ylim(0,5); ax.set_title("Percepción del personal (escala 1–5)")
    ax.grid(axis="y",alpha=0.4); plt.tight_layout(); return fig

# ─── Excel ───────────────────────────────────────────────────────────────────
def generate_excel():
    rec=query_df("SELECT * FROM process_records")
    ins=query_df("SELECT * FROM instruments")
    alerts=query_df("SELECT * FROM alerts")
    survey=query_df("SELECT * FROM staff_survey")
    plans=query_df("SELECT * FROM improvement_plans")
    now=datetime.now().strftime("%Y-%m-%d %H:%M")
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine="xlsxwriter") as w:
        wb=w.book
        hf=wb.add_format({"bold":True,"bg_color":"#1F4E79","font_color":"white","border":1})
        tf=wb.add_format({"bold":True,"font_size":13})
        nf=wb.add_format({"italic":True,"font_color":"gray"})
        def ws(df,name,sr=2):
            df.to_excel(w,sheet_name=name,index=False,startrow=sr)
            s=w.sheets[name]
            s.write(0,0,f"{APP_NAME} – {name} – {now}",tf)
            s.write(1,0,NOTA_ACAD,nf)
            for i,col in enumerate(df.columns):
                s.write(sr,i,col,hf)
                cw=max(len(str(col))+4, df[col].astype(str).str.len().max()+2 if not df.empty else 10)
                s.set_column(i,i,min(cw,50))
            s.autofilter(sr,0,sr+len(df),len(df.columns)-1)
        ws(ins,"Instrumental"); ws(rec,"Registros"); ws(alerts,"Alertas")
        ws(survey,"Encuestas"); ws(plans,"Plan_Mejora")
        if not rec.empty:
            t=rec.groupby(["instrument_code","batch_code"])["stage"].apply(list).reset_index()
            t["completadas"]=t["stage"].apply(len)
            t["estado"]=t["stage"].apply(lambda s:"Completa" if set(STAGES).issubset(set(s)) else "Incompleta")
            t.drop(columns=["stage"],inplace=True); ws(t,"Trazabilidad")
        si=wb.add_worksheet("Indicadores")
        si.write(0,0,f"{APP_NAME} – Indicadores – {now}",tf)
        si.write(2,0,"Indicador",hf); si.write(2,1,"Valor",hf)
        r=3
        if not rec.empty:
            for k,v in [
                ("Total registros",len(rec)),
                ("Cumplimiento global %",f"{(rec['complies']=='Sí').mean()*100:.1f}"),
                ("Tiempo promedio (min)",f"{rec['duration_minutes'].mean():.1f}"),
                ("Total alertas",len(alerts)),
                ("Alertas abiertas",len(alerts[alerts['status']=='Abierta']) if not alerts.empty else 0),
                ("Alertas riesgo Alto",len(alerts[alerts['severity']=='Alta']) if not alerts.empty else 0),
            ]:
                si.write(r,0,k); si.write(r,1,v); r+=1
        si.set_column(0,0,40); si.set_column(1,1,20)
    out.seek(0); return out.read()

# ─── PDF ─────────────────────────────────────────────────────────────────────
def generate_pdf():
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        _NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}
    except ImportError:
        return None
    rec=query_df("SELECT * FROM process_records")
    ins=query_df("SELECT * FROM instruments")
    alerts=query_df("SELECT * FROM alerts")
    plans=query_df("SELECT * FROM improvement_plans")
    survey=query_df("SELECT * FROM staff_survey")
    now=datetime.now().strftime("%Y-%m-%d %H:%M")

    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica","B",10)
            self.cell(0,8,f"{APP_NAME} – Informe de Trazabilidad",**_NL,align="C")
            self.set_draw_color(30,80,130); self.set_line_width(0.5)
            self.line(10,self.get_y(),200,self.get_y()); self.ln(3)
        def footer(self):
            self.set_y(-15); self.set_font("Helvetica","I",8)
            self.cell(0,8,f"Generado: {now}  –  Pág. {self.page_no()}",align="C")
        def titulo(self,t):
            self.set_font("Helvetica","B",12)
            self.set_fill_color(31,78,121); self.set_text_color(255,255,255)
            self.cell(0,8,f"  {t}",**_NL,fill=True)
            self.set_text_color(0,0,0); self.ln(2)
        def parrafo(self,t):
            self.set_font("Helvetica","",10)
            self.multi_cell(0,6,t,align="J"); self.ln(1)
        def tabla(self,df,maxr=25):
            if df.empty: self.parrafo("(Sin datos)"); return
            cw=min(170/len(df.columns),48)
            self.set_font("Helvetica","B",8)
            for col in df.columns: self.cell(cw,6,str(col)[:18],border=1,align="C")
            self.ln(); self.set_font("Helvetica","",8)
            for _,row in df.head(maxr).iterrows():
                for v in row: self.cell(cw,5,str(v)[:18],border=1)
                self.ln()
            if len(df)>maxr:
                self.set_font("Helvetica","I",8)
                self.cell(0,5,f"... y {len(df)-maxr} registros más.",**_NL)
        def img_bytes(self,b,w=165):
            tmp="/tmp/_ch.png"
            with open(tmp,"wb") as f: f.write(b)
            self.image(tmp,x=None,w=w); self.ln(4)

    pdf=PDF(orientation="P",unit="mm",format="Letter")
    pdf.set_margins(20,20,20); pdf.set_auto_page_break(True,20)
    pdf.add_page()
    pdf.ln(15); pdf.set_font("Helvetica","B",18)
    pdf.cell(0,12,APP_NAME,**_NL,align="C")
    pdf.set_font("Helvetica","B",13)
    pdf.cell(0,10,"Informe de Trazabilidad y Reprocesamiento",**_NL,align="C")
    pdf.ln(4); pdf.set_font("Helvetica","",10)
    for line in ["Universidad Libre Seccional Barranquilla",
                 "Programa de Instrumentación Quirúrgica",
                 f"Barranquilla – Colombia  |  {now}",
                 "Autor: Anderson Diaz Perez",
                 "Apoyo: Ligia Elena Cabana Cabana  ·  Cesar Augusto Vásquez Hurtado"]:
        pdf.cell(0,7,line,**_NL,align="C")
    pdf.ln(10); pdf.set_font("Helvetica","I",9)
    for line in wrap(NOTA_ACAD,90): pdf.cell(0,5,line,**_NL,align="C")

    pdf.add_page()
    pdf.titulo("1. Resumen ejecutivo")
    comp=f"{(rec['complies']=='Sí').mean()*100:.1f}%" if not rec.empty else "N/A"
    pdf.parrafo(f"Se evaluaron {len(ins)} instrumentales con {len(rec)} registros de proceso. "
                f"Cumplimiento global: {comp}. Alertas totales: {len(alerts)}.")
    pdf.titulo("2. Objetivo del informe")
    pdf.parrafo("Documentar la trazabilidad completa del instrumental quirúrgico en las 8 etapas del reprocesamiento, "
                "identificando alertas y oportunidades de mejora.")
    pdf.titulo("3. Instrumental evaluado")
    pdf.tabla(ins[["code","name","spaulding","service_origin","status"]])
    pdf.titulo("4. Registros de proceso")
    if not rec.empty:
        pdf.tabla(rec[["instrument_code","batch_code","stage","responsible","complies","result"]])
    pdf.titulo("5. Gráficas e indicadores")
    if not rec.empty:
        for fn in [chart_complies, chart_time]:
            fig=fn(rec); pdf.img_bytes(fig_bytes(fig)); _get_plt().close(fig)
    pdf.titulo("6. Alertas críticas")
    if not alerts.empty:
        pdf.tabla(alerts[["instrument_code","batch_code","alert_type","severity","status","created_at"]])
        fig=chart_alerts(alerts); pdf.img_bytes(fig_bytes(fig)); _get_plt().close(fig)
    else:
        pdf.parrafo("No se registraron alertas.")
    pdf.titulo("7. Plan de mejora")
    if not plans.empty:
        pdf.tabla(plans[["finding","risk_level","corrective_action","state"]])
    pdf.titulo("8. Percepción del personal")
    if not survey.empty:
        fig=chart_survey(survey); pdf.img_bytes(fig_bytes(fig)); _get_plt().close(fig)
    pdf.titulo("9. Conclusión técnica")
    pdf.parrafo("El prototipo ReproTrace Basic 360° demostró viabilidad para registrar, monitorear y trazar "
                "instrumental quirúrgico. Las alertas permiten identificar desviaciones en tiempo real.")
    pdf.titulo("10. Alcance y limitaciones")
    pdf.parrafo(NOTA_ACAD)
    return bytes(pdf.output())

# ─── Footer institución ───────────────────────────────────────────────────────
def inst_footer():
    return """
---
**Universidad Libre Seccional Barranquilla** | Prog. Instrumentación Quirúrgica  
**Autor:** Anderson Diaz Perez | **Apoyo:** Ligia Elena Cabana Cabana · Cesar Augusto Vásquez Hurtado
"""

# ─── Pantalla de login ────────────────────────────────────────────────────────
def login_screen():
    st.title(APP_NAME)
    st.subheader("Sistema académico de monitoreo y trazabilidad del instrumental quirúrgico")
    st.warning(NOTA_ACAD)
    st.markdown(inst_footer())
    with st.sidebar:
        st.title("Acceso al sistema")
        tab_login, tab_reg = st.tabs(["🔑 Ingresar", "📝 Registrarse"])

        with tab_login:
            st.info("Usuarios de prueba: admin / admin123 · central / central123 · docente / docente123")
            u = st.text_input("Usuario", key="li_user")
            p = st.text_input("Contraseña", type="password", key="li_pass")
            if st.button("Ingresar", use_container_width=True, key="btn_login"):
                # Buscar primero en tabla BD, luego en USERS hardcoded
                db_user = get_user(u)
                if db_user and _check_password(p, db_user["password"]):
                    role = db_user["role"]
                    st.session_state.update({"login": True, "user": u, "role": role})
                    execute("INSERT INTO login_sessions(username,role,event,timestamp) VALUES(?,?,?,?)",
                            (u, role, "Inicio de sesión", datetime.now().isoformat()))
                    audit(u, "Inicio de sesión", "Login")
                    st.rerun()
                elif u in USERS and USERS[u]["password"] == p:
                    role = USERS[u]["role"]
                    st.session_state.update({"login": True, "user": u, "role": role})
                    execute("INSERT INTO login_sessions(username,role,event,timestamp) VALUES(?,?,?,?)",
                            (u, role, "Inicio de sesión", datetime.now().isoformat()))
                    audit(u, "Inicio de sesión", "Login")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        with tab_reg:
            st.write("Cree su cuenta para acceder al sistema.")
            rn = st.text_input("Nombre completo", key="rg_name")
            ru = st.text_input("Usuario (sin espacios)", key="rg_user")
            rp = st.text_input("Contraseña", type="password", key="rg_pass")
            rp2 = st.text_input("Confirmar contraseña", type="password", key="rg_pass2")
            rr = st.selectbox("Rol", ["Personal de central", "Docente/Tutor"], key="rg_role")
            if st.button("Crear cuenta", use_container_width=True, key="btn_register"):
                if not ru or not rp or not rn:
                    st.error("Complete todos los campos.")
                elif rp != rp2:
                    st.error("Las contraseñas no coinciden.")
                elif " " in ru:
                    st.error("El usuario no puede tener espacios.")
                else:
                    ok, msg = register_user(ru, rp, rn, rr)
                    if ok:
                        st.success(f"✅ Cuenta creada. Ya puede ingresar con el usuario '{ru}'.")
                        audit("sistema", "Registro de usuario", "Login", f"Nuevo usuario: {ru} / Rol: {rr}")
                    else:
                        st.error(msg)

def header():
    st.title(APP_NAME); st.caption(NOTA_ACAD)
    st.sidebar.success(f"👤 {st.session_state['user']}  |  {st.session_state['role']}")
    if st.sidebar.button("🚪 Cerrar sesión",use_container_width=True):
        execute("INSERT INTO login_sessions(username,role,event,timestamp) VALUES(?,?,?,?)",
                (st.session_state["user"],st.session_state["role"],"Cierre de sesión",datetime.now().isoformat()))
        audit(st.session_state["user"],"Cierre de sesión","Login")
        st.session_state.clear(); st.rerun()
    st.sidebar.markdown(inst_footer())

# ─── Panel principal ──────────────────────────────────────────────────────────
def dashboard():
    st.header("🏠 Panel principal")
    ins=query_df("SELECT * FROM instruments")
    rec=query_df("SELECT * FROM process_records")
    al=query_df("SELECT * FROM alerts WHERE status='Abierta'")
    pl=query_df("SELECT * FROM improvement_plans WHERE state='Pendiente'")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("🔧 Instrumentales",len(ins))
    c2.metric("📋 Registros",len(rec))
    c3.metric("🔔 Alertas abiertas",len(al))
    c4.metric("✅ Cumplimiento",f"{(rec['complies']=='Sí').mean()*100:.1f}%" if not rec.empty else "N/A")
    c5.metric("📌 Planes pendientes",len(pl))
    red=len(al[al["severity"]=="Alta"]) if not al.empty else 0
    if red:   st.error(f"🔴 {red} ALERTA(S) DE RIESGO ALTO ABIERTAS. Revise el módulo de Alertas.")
    elif len(al): st.warning("🟡 Hay alertas abiertas de nivel medio.")
    else:     st.success("🟢 Sin alertas abiertas. Situación controlada.")
    st.subheader("Ruta de reprocesamiento")
    st.write("  →  ".join(STAGES))
    if not rec.empty:
        st.subheader("Cumplimiento por etapa")
        fig=chart_complies(rec); st.pyplot(fig); _get_plt().close(fig)
    st.subheader("Últimas alertas abiertas")
    if not al.empty:
        for _,row in al.iterrows():
            sev=row["severity"]; msg=f"**[{sev}]** {row['alert_type']} – {row['instrument_code']}/{row['batch_code']}: {row['description']}"
            if sev=="Alta": st.error(f"🔴 {msg}")
            elif sev=="Media": st.warning(f"🟡 {msg}")
            else: st.info(f"🟢 {msg}")
    else:
        st.success("Sin alertas abiertas.")

# ─── Registro de instrumental ─────────────────────────────────────────────────
def instruments_module():
    st.header("1. Registro maestro de instrumental")
    st.info("💡 Registre cada instrumento con su código único. La clasificación de Spaulding determina el nivel de reprocesamiento requerido.")
    with st.expander("➕ Nuevo instrumental",expanded=True):
        with st.form("ins_form"):
            c1,c2=st.columns(2)
            code=c1.text_input("Código único *",placeholder="IQ-005")
            name=c2.text_input("Nombre *",placeholder="Pinza Allis")
            cat =c1.text_input("Categoría",placeholder="Prensión, corte...")
            spa =c2.selectbox("Clasificación Spaulding",["Crítico","Semicrítico","No crítico"])
            srv =c1.text_input("Servicio de origen")
            qty =c2.number_input("Cantidad",min_value=1,value=1)
            sta =c1.selectbox("Estado",["Activo","Dañado","Retirado","En mantenimiento"])
            obs =st.text_area("Observaciones")
            if st.form_submit_button("💾 Guardar"):
                if not code.strip() or not name.strip():
                    st.error("Código y nombre son obligatorios.")
                else:
                    try:
                        execute("""INSERT INTO instruments(code,name,category,spaulding,service_origin,quantity,status,observations,registered_by,created_at)
                                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                                (code.strip(),name.strip(),cat,spa,srv,qty,sta,obs,st.session_state["user"],datetime.now().isoformat()))
                        audit(st.session_state["user"],"Registro","Instrumental",f"Código:{code}")
                        st.success(f"Instrumental {code} guardado."); st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Ya existe ese código.")
    df=query_df("SELECT * FROM instruments ORDER BY created_at DESC")
    fc1,fc2=st.columns(2)
    q=fc1.text_input("🔍 Buscar por código o nombre")
    fs=fc2.selectbox("Estado",["Todos","Activo","Dañado","Retirado","En mantenimiento"])
    if q: df=df[df["code"].str.contains(q,case=False,na=False)|df["name"].str.contains(q,case=False,na=False)]
    if fs!="Todos": df=df[df["status"]==fs]
    st.dataframe(df,use_container_width=True)

# ─── Registro del proceso ─────────────────────────────────────────────────────
def process_module():
    st.header("2. Registro del proceso de reprocesamiento")
    st.info("💡 Registre cada etapa en orden. El sistema valida la secuencia y genera alertas automáticas.")
    ins=query_df("SELECT code,name FROM instruments WHERE status='Activo' ORDER BY code")
    if ins.empty:
        st.warning("Registre primero un instrumental activo."); return
    opts=[f"{r.code} – {r.name}" for _,r in ins.iterrows()]
    with st.form("proc_form",clear_on_submit=True):
        sel=st.selectbox("Instrumental *",opts)
        code=sel.split("–")[0].strip()
        batch=st.text_input("Lote / carga *",placeholder="LOTE-2026-001")
        stage=st.selectbox("Etapa *",STAGES)
        resp=st.text_input("Responsable *",value=st.session_state.get("user",""))
        complies=st.radio("¿Cumple protocolo?",["Sí","No"],horizontal=True)
        result=st.selectbox("Resultado",["Aprobado","Rechazado","Pendiente","No aplica"])
        c1,c2,c3,c4=st.columns(4)
        sd=c1.date_input("Fecha inicio",value=date.today())
        st_=c2.time_input("Hora inicio")
        ed=c3.date_input("Fecha fin",value=date.today())
        et=c4.time_input("Hora fin")
        st.markdown("---"); st.markdown("**Campos específicos por etapa**")
        # Variables por etapa
        r_ori=r_sta=""
        r_qty=1
        cl_m=cl_c=cl_n=""
        ins_s=""
        pk_t=ce_e=ce_i=""
        st_e=cy_t=ld_n=""
        temp=pres=exp_t=0.0
        ph_i=ch_i=bi_i=rel=""
        sl=s_d=p_c=ex_d=""
        ds=dr=rr=ps=""

        if stage=="Recepción":
            r_ori=st.text_input("Servicio de origen")
            r_sta=st.selectbox("Estado inicial",["Completo","Incompleto","Dañado","Contaminado"])
            r_qty=st.number_input("Cantidad recibida",min_value=1,value=1)
        elif stage=="Limpieza y descontaminación":
            cl_m=st.selectbox("Método",["Manual","Ultrasónica","Automatizada","Mixta"])
            cl_c=st.selectbox("Cumplimiento",["Conforme","No conforme"])
            cl_n=st.text_area("Novedades")
        elif stage=="Inspección funcional":
            ins_s=st.selectbox("Estado funcional",["Completo y funcional","Incompleto","Dañado","Oxidado","Requiere mantenimiento"])
        elif stage=="Empaque":
            pk_t=st.selectbox("Tipo de empaque",["Papel grado médico","Tela","Contenedor rígido","Bolsa mixta","Otro"])
            a,b=st.columns(2)
            ce_e=a.selectbox("Indicador químico externo",["Conforme","No conforme","No aplica"])
            ce_i=b.selectbox("Indicador químico interno",["Conforme","No conforme","No aplica"])
        elif stage=="Esterilización":
            a,b=st.columns(2)
            st_e=a.text_input("Equipo esterilizador",placeholder="EST-01")
            cy_t=b.selectbox("Tipo de ciclo",["Vapor 134°C","Vapor 121°C","Baja temperatura","Peróxido de hidrógeno","Otro"])
            a2,b2,c2_,d2=st.columns(4)
            temp=a2.number_input("Temp °C",0.0,250.0,134.0)
            pres=b2.number_input("Presión",0.0,10.0,2.1)
            exp_t=c2_.number_input("Exposición (min)",0.0,60.0,4.0)
            ld_n=d2.text_input("N° carga",placeholder="C-001")
        elif stage=="Validación / liberación de carga":
            a,b,c_=st.columns(3)
            ph_i=a.selectbox("Indicador físico",["Conforme","No conforme","No aplica"])
            ch_i=b.selectbox("Indicador químico",["Conforme","No conforme","No aplica"])
            bi_i=c_.selectbox("Indicador biológico",["Conforme","No conforme","Pendiente","No aplica"])
            rel=st.selectbox("Resultado de liberación",["Aprobado","Rechazado","Pendiente"])
        elif stage=="Almacenamiento":
            a,b=st.columns(2)
            sl=a.text_input("Ubicación",placeholder="Estante A – Nivel 2")
            s_d=b.date_input("Fecha almacenamiento",value=date.today()).isoformat()
            p_c=st.selectbox("Condición del paquete",["Íntegro","Dañado","Vencido"])
            ex_d=st.date_input("Fecha vencimiento",value=date.today()+timedelta(days=30)).isoformat()
        elif stage=="Distribución":
            a,b=st.columns(2)
            ds=a.text_input("Servicio destino",placeholder="Quirófano 1")
            dr=b.text_input("Responsable de entrega")
            rr=a.text_input("Responsable de recepción")
            ps=b.selectbox("Estado del paquete al entregar",["Íntegro","Dañado"])

        obs=st.text_area("Observaciones generales")
        submit=st.form_submit_button("💾 Guardar etapa")

    if submit:
        if not batch.strip() or not resp.strip():
            st.error("Lote/carga y responsable son obligatorios."); return
        ok,msg=validate_stage_order(code,batch.strip(),stage)
        if not ok: st.warning(f"⚠️ {msg} Se guarda como desviación académica.")
        s_dt=datetime.combine(sd,st_); e_dt=datetime.combine(ed,et)
        if e_dt<s_dt: st.error("Hora final no puede ser anterior a la inicial."); return
        dur=(e_dt-s_dt).total_seconds()/60
        execute("""INSERT INTO process_records(
            instrument_code,batch_code,stage,responsible,start_datetime,end_datetime,duration_minutes,complies,result,
            reception_origin,reception_initial_state,reception_quantity,
            cleaning_method,cleaning_complies,cleaning_novelties,
            inspection_status,
            package_type,chem_indicator_ext,chem_indicator_int,
            sterilizer_id,cycle_type,temperature,pressure,exposure_time,load_number,
            physical_indicator,chemical_indicator,biological_indicator,release_result,
            storage_location,storage_date,package_condition,expiration_date,
            destination_service,delivery_responsible,reception_responsible,package_state_delivery,
            observations,registered_by,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code,batch.strip(),stage,resp,s_dt.isoformat(),e_dt.isoformat(),dur,complies,result,
             r_ori,r_sta,r_qty,cl_m,cl_c,cl_n,ins_s,pk_t,ce_e,ce_i,
             st_e,cy_t,temp,pres,exp_t,ld_n,ph_i,ch_i,bi_i,rel,
             sl,s_d,p_c,ex_d,ds,dr,rr,ps,obs,st.session_state["user"],datetime.now().isoformat()))
        audit(st.session_state["user"],"Registro etapa","Proceso",f"{code}/{batch}/{stage}")
        if not ok: add_alert(code,batch.strip(),"Secuencia incompleta","Media",msg)
        if complies=="No": add_alert(code,batch.strip(),"Incumplimiento de protocolo","Alta",f"No cumple en {stage}. {obs}")
        if result=="Rechazado": add_alert(code,batch.strip(),"Ciclo rechazado","Alta",f"Rechazado en {stage}.")
        if ins_s in ["Incompleto","Dañado","Oxidado"]: add_alert(code,batch.strip(),"Instrumental dañado","Alta",f"Estado: {ins_s}.")
        if ce_e=="No conforme" or ce_i=="No conforme": add_alert(code,batch.strip(),"Indicador no conforme","Alta","Indicador químico no conforme en empaque.")
        if bi_i=="No conforme": add_alert(code,batch.strip(),"Indicador biológico no conforme","Alta","Indicador biológico no conforme. Rechazar carga.")
        if ch_i=="No conforme": add_alert(code,batch.strip(),"Indicador no conforme","Alta","Indicador químico no conforme en validación.")
        if cl_c=="No conforme": add_alert(code,batch.strip(),"Limpieza no conforme","Alta",f"Limpieza no conforme. {cl_n}")
        if stage=="Distribución" and rel and rel!="Aprobado": add_alert(code,batch.strip(),"Validación pendiente","Alta","Distribución sin liberación aprobada.")
        check_and_recommend()
        st.success(f"✅ Etapa '{stage}' registrada.")
    st.dataframe(query_df("SELECT * FROM process_records ORDER BY created_at DESC LIMIT 30"),use_container_width=True)

# ─── Trazabilidad ─────────────────────────────────────────────────────────────
def traceability_module():
    st.header("3. Consulta de trazabilidad")
    st.info("💡 Seleccione un par instrumental/lote para ver el historial completo.")
    rec=query_df("SELECT DISTINCT instrument_code,batch_code FROM process_records ORDER BY batch_code")
    if rec.empty: st.warning("No hay registros de proceso."); return
    fc1,fc2=st.columns(2)
    fc=fc1.text_input("Filtrar por código"); fb=fc2.text_input("Filtrar por lote")
    if fc: rec=rec[rec["instrument_code"].str.contains(fc,case=False,na=False)]
    if fb: rec=rec[rec["batch_code"].str.contains(fb,case=False,na=False)]
    if rec.empty: st.warning("Sin resultados con ese filtro."); return
    key=st.selectbox("Instrumental / Lote",[f"{r.instrument_code}  |  {r.batch_code}" for _,r in rec.iterrows()])
    code,batch=[x.strip() for x in key.split("|")]
    df=query_df("SELECT * FROM process_records WHERE instrument_code=? AND batch_code=? ORDER BY start_datetime",(code,batch))
    missing=[s for s in STAGES if s not in df["stage"].tolist()]
    if missing: st.error(f"🔴 Trazabilidad INCOMPLETA. Faltan: {', '.join(missing)}")
    else: st.success("🟢 Trazabilidad COMPLETA.")
    st.subheader("Línea de tiempo")
    for _,r in df.iterrows():
        ic="✅" if r["complies"]=="Sí" else "❌"
        st.markdown(f"**{r['stage']}** {ic} | {r['start_datetime']} → {r['end_datetime']} | {r['duration_minutes']:.1f} min | Resp: {r['responsible']} | {r['result']}")
    st.subheader("Datos completos"); st.dataframe(df,use_container_width=True)
    al=query_df("SELECT * FROM alerts WHERE instrument_code=? AND batch_code=?",(code,batch))
    st.subheader("Alertas asociadas")
    if not al.empty:
        for _,row in al.iterrows():
            sev=row["severity"]; msg=f"[{sev}] {row['alert_type']}: {row['description']}"
            if sev=="Alta": st.error(f"🔴 {msg}")
            elif sev=="Media": st.warning(f"🟡 {msg}")
            else: st.info(f"🟢 {msg}")
    else: st.success("Sin alertas para este lote.")

# ─── Alertas ──────────────────────────────────────────────────────────────────
def alerts_module():
    st.header("4. Alertas y novedades")
    st.info("💡 Alertas rojas = riesgo crítico. Requieren acción inmediata y documentación en el plan de mejora.")
    all_al=query_df("SELECT * FROM alerts ORDER BY created_at DESC")
    fc1,fc2,fc3=st.columns(3)
    fs=fc1.selectbox("Severidad",["Todas","Alta","Media","Baja"])
    fst=fc2.selectbox("Estado",["Todas","Abierta","Cerrada"])
    fcd=fc3.text_input("Código instrumental")
    df=all_al.copy()
    if fs!="Todas": df=df[df["severity"]==fs]
    if fst!="Todas": df=df[df["status"]==fst]
    if fcd: df=df[df["instrument_code"].str.contains(fcd,case=False,na=False)]
    for _,row in df.iterrows():
        sev=row["severity"]; msg=f"**[{sev}]** {row['alert_type']} – {row['instrument_code']}/{row['batch_code']}: {row['description']}"
        if sev=="Alta": st.error(f"🔴 {msg}")
        elif sev=="Media": st.warning(f"🟡 {msg}")
        else: st.info(f"🟢 {msg}")
    st.subheader("Tabla"); st.dataframe(df,use_container_width=True)
    op=query_df("SELECT id,alert_type,instrument_code,batch_code FROM alerts WHERE status='Abierta'")
    if not op.empty:
        st.subheader("Cerrar alerta")
        sel=st.selectbox("Alerta a cerrar",[f"{r.id} | {r.alert_type} | {r.instrument_code}/{r.batch_code}" for _,r in op.iterrows()])
        if st.button("✅ Marcar como cerrada"):
            aid=int(sel.split("|")[0].strip())
            execute("UPDATE alerts SET status='Cerrada',closed_by=?,closed_at=? WHERE id=?",
                    (st.session_state["user"],datetime.now().isoformat(),aid))
            audit(st.session_state["user"],"Cerrar alerta","Alertas",f"ID:{aid}")
            st.success("Alerta cerrada."); st.rerun()

# ─── Plan de mejora ───────────────────────────────────────────────────────────
def improvement_module():
    st.header("5. Plan de mejora")
    st.info("💡 El sistema genera recomendaciones automáticas ante alertas críticas. También puede registrar hallazgos manualmente.")
    check_and_recommend()
    with st.expander("➕ Registrar nuevo plan",expanded=False):
        with st.form("imp_form"):
            finding=st.text_area("Hallazgo identificado *")
            c1,c2=st.columns(2)
            rtyp=c1.text_input("Riesgo asociado")
            rlev=c2.selectbox("Nivel de riesgo",["Bajo","Medio","Alto","Crítico"])
            cause=st.text_area("Causa probable")
            corr=st.text_area("Acción correctiva")
            prev=st.text_area("Acción preventiva")
            c3,c4=st.columns(2)
            resp=c3.text_input("Responsable")
            fdate=c4.date_input("Fecha de seguimiento",value=date.today()+timedelta(days=15))
            state=c3.selectbox("Estado",["Pendiente","En proceso","Cumplido"])
            evid=st.text_area("Evidencia / comentario")
            if st.form_submit_button("💾 Guardar"):
                if not finding.strip(): st.error("El hallazgo es obligatorio.")
                else:
                    execute("""INSERT INTO improvement_plans(finding,risk_type,risk_level,probable_cause,corrective_action,
                               preventive_action,responsible,follow_up_date,state,evidence,registered_by,created_at)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (finding,rtyp,rlev,cause,corr,prev,resp,fdate.isoformat(),state,evid,
                             st.session_state["user"],datetime.now().isoformat()))
                    audit(st.session_state["user"],"Registro","Plan de mejora",finding[:60])
                    st.success("Plan registrado."); st.rerun()
    df=query_df("SELECT * FROM improvement_plans ORDER BY created_at DESC")
    filt=st.selectbox("Filtrar nivel",["Todos","Bajo","Medio","Alto","Crítico"])
    if filt!="Todos": df=df[df["risk_level"]==filt]
    st.dataframe(df,use_container_width=True)
    if not df.empty:
        st.subheader("Actualizar estado")
        pid=st.selectbox("Plan (ID)",df["id"].tolist())
        ns=st.selectbox("Nuevo estado",["Pendiente","En proceso","Cumplido"])
        ev=st.text_input("Evidencia")
        if st.button("Actualizar"):
            execute("UPDATE improvement_plans SET state=?,evidence=? WHERE id=?",(ns,ev,pid))
            audit(st.session_state["user"],"Actualizar","Plan de mejora",f"ID:{pid}→{ns}")
            st.success("Actualizado."); st.rerun()

# ─── Reportes ─────────────────────────────────────────────────────────────────
def reports_module():
    st.header("6. Reportes e indicadores")
    rec=query_df("SELECT * FROM process_records")
    alerts=query_df("SELECT * FROM alerts")
    survey=query_df("SELECT * FROM staff_survey")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Registros",len(rec))
    c2.metric("Cumplimiento",f"{(rec['complies']=='Sí').mean()*100:.1f}%" if not rec.empty else "N/A")
    c3.metric("Tiempo promedio",f"{rec['duration_minutes'].mean():.1f} min" if not rec.empty else "N/A")
    c4.metric("Alertas abiertas",len(alerts[alerts["status"]=="Abierta"]) if not alerts.empty else 0)
    st.subheader("Filtros")
    fc1,fc2,fc3=st.columns(3)
    fstage=fc1.selectbox("Etapa",["Todas"]+STAGES)
    ffrom=fc2.date_input("Desde",value=date.today()-timedelta(days=30))
    fto=fc3.date_input("Hasta",value=date.today())
    if not rec.empty:
        df=rec.copy(); df["created_at"]=pd.to_datetime(df["created_at"])
        df=df[(df["created_at"].dt.date>=ffrom)&(df["created_at"].dt.date<=fto)]
        if fstage!="Todas": df=df[df["stage"]==fstage]
        if not df.empty:
            st.subheader("Cumplimiento por etapa")
            fig=chart_complies(df); st.pyplot(fig); _get_plt().close(fig)
            st.subheader("Tiempo promedio por etapa")
            fig=chart_time(df); st.pyplot(fig); _get_plt().close(fig)
    if not alerts.empty:
        st.subheader("Distribución de alertas")
        fig=chart_alerts(alerts); st.pyplot(fig); _get_plt().close(fig)
    if not survey.empty:
        st.subheader("Percepción del personal")
        fig=chart_survey(survey); st.pyplot(fig); _get_plt().close(fig)
    st.subheader("Descargar reportes")
    col1,col2=st.columns(2)
    with col1:
        st.download_button("📥 Excel completo",generate_excel(),
                           file_name=f"reprotrace_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        pdf=generate_pdf()
        if pdf:
            st.download_button("📄 Informe PDF",pdf,file_name=f"reprotrace_{date.today()}.pdf",mime="application/pdf")
        else:
            st.warning("Instale fpdf2 para PDF: `pip install fpdf2`")

# ─── Encuesta ─────────────────────────────────────────────────────────────────
def survey_module():
    st.header("7. Encuesta de percepción del personal")
    st.info("💡 Escala Likert: 1=Muy en desacuerdo, 5=Muy de acuerdo")
    QUESTIONS=[
        "El software es fácil de usar.",
        "Facilita el registro de los procesos.",
        "Reduce errores de registro.",
        "Mejora la trazabilidad del instrumental.",
        "Permite mejor control de las etapas.",
        "Optimiza el tiempo de los procesos.",
        "Me siento cómodo(a) usando el software.",
        "Contribuye indirectamente a la seguridad del paciente.",
        "Mejora la organización del trabajo.",
        "Recomendaría su uso académico/institucional.",
    ]
    with st.form("surv_form"):
        role=st.text_input("Cargo / rol"); exp=st.number_input("Años de experiencia",0.0,step=0.5)
        ans=[st.slider(f"{i+1}. {q}",1,5,3) for i,q in enumerate(QUESTIONS)]
        comm=st.text_area("Comentarios")
        if st.form_submit_button("💾 Guardar"):
            execute("""INSERT INTO staff_survey(role,experience_years,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,comments,created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(role,exp,*ans,comm,datetime.now().isoformat()))
            audit(st.session_state["user"],"Encuesta","Encuesta",f"Cargo:{role}")
            st.success("¡Encuesta guardada!")
    df=query_df("SELECT * FROM staff_survey ORDER BY created_at DESC")
    if not df.empty:
        fig=chart_survey(df); st.pyplot(fig); _get_plt().close(fig)

# ─── Auditoría ────────────────────────────────────────────────────────────────
def audit_module():
    st.header("8. Auditoría de cambios")
    st.info("💡 Registro automático de todas las acciones del sistema.")
    df=query_df("SELECT * FROM audit_log ORDER BY created_at DESC")
    fc1,fc2=st.columns(2)
    fu=fc1.text_input("Filtrar usuario"); fm=fc2.text_input("Filtrar módulo")
    if fu: df=df[df["username"].str.contains(fu,case=False,na=False)]
    if fm: df=df[df["module"].str.contains(fm,case=False,na=False)]
    st.dataframe(df,use_container_width=True)

# ─── Configuración y respaldo ─────────────────────────────────────────────────
def config_module():
    st.header("9. Configuración y respaldo")
    st.subheader("Respaldar base de datos")
    if st.button("📦 Descargar BD (.db)"):
        if os.path.exists(DB_PATH):
            with open(DB_PATH,"rb") as f:
                st.download_button("⬇️ Descargar",f.read(),file_name="reprotrace_backup.db")
    st.subheader("Descargar todos los datos en ZIP")
    if st.button("🗜️ Generar ZIP"):
        zb=io.BytesIO()
        with zipfile.ZipFile(zb,"w") as zf:
            if os.path.exists(DB_PATH): zf.write(DB_PATH,"reprotrace_basic_360.db")
            zf.writestr("reporte.xlsx",generate_excel())
        zb.seek(0)
        st.download_button("⬇️ Descargar ZIP",zb.read(),file_name="reprotrace_datos.zip")
    st.subheader("Sesiones registradas")
    st.dataframe(query_df("SELECT * FROM login_sessions ORDER BY id DESC LIMIT 50"),use_container_width=True)
    if st.session_state.get("role")=="Administrador":
        st.subheader("👥 Gestión de usuarios registrados")
        users_df = query_df("SELECT id, username, full_name, role, active, created_at FROM users ORDER BY id DESC")
        if users_df.empty:
            st.info("No hay usuarios registrados aún.")
        else:
            st.dataframe(users_df, use_container_width=True)
            st.write("**Activar / Desactivar usuario:**")
            sel = st.selectbox("Seleccionar usuario", users_df["username"].tolist(), key="cfg_usr_sel")
            col1, col2 = st.columns(2)
            if col1.button("✅ Activar", use_container_width=True):
                execute("UPDATE users SET active=1 WHERE username=?", (sel,))
                audit(st.session_state["user"], "Activar usuario", "Config", f"Usuario activado: {sel}")
                st.success(f"Usuario '{sel}' activado."); st.rerun()
            if col2.button("🚫 Desactivar", use_container_width=True):
                execute("UPDATE users SET active=0 WHERE username=?", (sel,))
                audit(st.session_state["user"], "Desactivar usuario", "Config", f"Usuario desactivado: {sel}")
                st.warning(f"Usuario '{sel}' desactivado."); st.rerun()
            st.write("**Cambiar rol:**")
            new_role = st.selectbox("Nuevo rol", ["Personal de central","Docente/Tutor","Administrador"], key="cfg_usr_role")
            if st.button("Guardar rol", use_container_width=True):
                execute("UPDATE users SET role=? WHERE username=?", (new_role, sel))
                audit(st.session_state["user"], "Cambiar rol", "Config", f"{sel} → {new_role}")
                st.success(f"Rol de '{sel}' actualizado a '{new_role}'."); st.rerun()
        st.subheader("⚠️ Zona de administración")
        st.warning("Solo para demostración académica. Acción irreversible.")
        confirm=st.text_input("Escriba CONFIRMAR para limpiar datos de prueba")
        if confirm=="CONFIRMAR":
            if st.button("🗑️ Limpiar datos de prueba"):
                for t in ["process_records","alerts","improvement_plans","staff_survey","audit_log"]:
                    execute(f"DELETE FROM {t}")
                execute("DELETE FROM instruments WHERE registered_by='sistema'")
                seed_demo_data()
                audit(st.session_state["user"],"Limpieza demo","Config","Datos de demostración reiniciados")
                st.success("Datos de prueba eliminados y reiniciados."); st.rerun()

# ─── Plan de pruebas ──────────────────────────────────────────────────────────
def tests_module():
    st.header("10. Plan de pruebas")
    df=pd.DataFrame([
        ["Login correcto","Ingresar con credenciales válidas","Acceso concedido y sesión registrada"],
        ["Login incorrecto","Contraseña errónea","Mensaje de error, sin acceso"],
        ["Registro instrumental","Registrar con código único","Guardado en BD"],
        ["Código duplicado","Repetir código existente","Error por duplicado"],
        ["8 etapas en orden","Registrar todas las etapas","Trazabilidad completa"],
        ["Secuencia incorrecta","Empaque sin inspección previa","Advertencia de secuencia"],
        ["Trazabilidad completa","8 etapas registradas","Estado: Completa"],
        ["Trazabilidad incompleta","Etapas faltantes","Lista de etapas faltantes"],
        ["Alerta automática","Resultado Rechazado","Alerta Alta generada"],
        ["Indicador biológico NC","Biológico No conforme","Alerta crítica + plan automático"],
        ["Cierre de alerta","Marcar como cerrada","Estado → Cerrada"],
        ["Plan de mejora","Registrar hallazgo","Plan guardado"],
        ["Reporte Excel","Descargar","Múltiples hojas con datos"],
        ["Reporte PDF","Descargar","Documento con portada y gráficas"],
        ["Encuesta","Contestar Likert","Promedios en gráfica"],
        ["Auditoría","Revisar acciones","Log con usuario y fecha"],
        ["Respaldo","Descargar BD y ZIP","Archivos descargados"],
        ["Limpieza demo (admin)","Confirmar limpieza","Datos reiniciados"],
    ],columns=["Prueba","Procedimiento","Criterio de aprobación"])
    st.dataframe(df,use_container_width=True)

# ─── Limitaciones ─────────────────────────────────────────────────────────────
def limitations_module():
    st.header("11. Limitaciones del prototipo")
    st.warning(NOTA_ACAD)
    for lim,desc in [
        ("Autenticación básica","Credenciales en texto plano. No usar en producción real."),
        ("Base de datos local","SQLite en archivo local. No apta para múltiples usuarios simultáneos en red."),
        ("Sin cifrado","Datos no cifrados. No almacenar información sensible de pacientes."),
        ("Sin validación IFU","No valida parámetros según instrucciones del fabricante del equipo."),
        ("Sin integración hospitalaria","No se conecta con HIS, LIS ni sistemas clínicos."),
        ("Sin trazabilidad de paciente","No vincula instrumental con paciente ni procedimiento real."),
        ("Sin firma digital","Los registros no tienen validez legal ni regulatoria."),
        ("Sin respaldo automático","El respaldo es manual. Producción requeriría copias automáticas."),
        ("Concurrencia limitada","SQLite tiene límites de escritura concurrente."),
        ("Sin validación de normas","No implementa ISO 17665, ANSI/AAMI ST79 ni normativas colombianas completas."),
    ]:
        st.markdown(f"**{lim}:** {desc}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title=APP_NAME, page_icon="🏥", layout="wide")
    init_db()
    if not st.session_state.get("seeded"):
        seed_demo_data(); st.session_state["seeded"] = True
    if "login" not in st.session_state: st.session_state["login"]=False
    if not st.session_state["login"]: login_screen(); return
    header()
    MENU=[
        "🏠 Panel principal","🔧 Registro de instrumental","📋 Registro del proceso",
        "🔍 Consulta de trazabilidad","🔔 Alertas y novedades","📌 Plan de mejora",
        "📊 Reportes e indicadores","📝 Encuesta de percepción","🔒 Auditoría de cambios",
        "⚙️ Configuración y respaldo","✅ Plan de pruebas","⚠️ Limitaciones del prototipo",
    ]
    menu=st.sidebar.radio("Menú",MENU)
    dispatch={
        "🏠 Panel principal":dashboard,
        "🔧 Registro de instrumental":instruments_module,
        "📋 Registro del proceso":process_module,
        "🔍 Consulta de trazabilidad":traceability_module,
        "🔔 Alertas y novedades":alerts_module,
        "📌 Plan de mejora":improvement_module,
        "📊 Reportes e indicadores":reports_module,
        "📝 Encuesta de percepción":survey_module,
        "🔒 Auditoría de cambios":audit_module,
        "⚙️ Configuración y respaldo":config_module,
        "✅ Plan de pruebas":tests_module,
        "⚠️ Limitaciones del prototipo":limitations_module,
    }
    dispatch.get(menu,dashboard)()

if __name__=="__main__":
    main()
