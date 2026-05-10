# =============================================================================
# ReproTrace Basic 360°  |  v2.0 – 2026
# Prototipo académico – Universidad Libre Seccional Barranquilla
# Autor principal: Anderson Diaz Perez
# Apoyo académico: Ligia Elena Cabana Cabana · Cesar Augusto Vásquez Hurtado
# Facultad de Ciencias de la Salud, Exactas y Naturales
# Programa de Instrumentación Quirúrgica – Barranquilla, Colombia
# =============================================================================

import streamlit as st
import streamlit.components.v1 as st_components
import pandas as pd
import sqlite3
import io, zipfile, os, base64
from datetime import datetime, date, timedelta
from textwrap import wrap

@st.cache_resource
def _get_plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as _plt
    return _plt

# =============================================================================
# FUNCIONES DE IMÁGENES Y ESTILOS
# Para cambiar el logo: reemplaza assets/Logo.png
# Para cambiar el fondo: reemplaza assets/imagen de fondo de pantalla.png
# =============================================================================

def _img_to_base64(path: str) -> str | None:
    """Convierte una imagen local a base64 para usar en CSS/HTML."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def apply_login_background():
    """
    Aplica la imagen de fondo institucional en la pantalla de login.
    - Carga assets/imagen de fondo de pantalla.png y la convierte a base64.
    - La aplica como background-image con cover y overlay translúcido.
    - Si la imagen no existe, usa un degradado azul como fallback.
    - También oculta elementos de Streamlit no deseados en el login.
    """
    # ── RUTA DE LA IMAGEN DE FONDO ──────────────────────────────────────────
    # Para cambiar el fondo, modifica la ruta de abajo:
    bg_path = "assets/fondo_login.png"
    b64 = _img_to_base64(bg_path)

    if b64:
        # Fondo con imagen institucional convertida a base64
        bg_css = f"""
        background-image: url('data:image/png;base64,{b64}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        """
    else:
        # Fallback: degradado azul si la imagen no se encuentra
        bg_css = """
        background: linear-gradient(135deg, #0a0e1a 0%, #0d2060 40%, #0a1628 100%);
        """

    # ── CSS COMPLETO PARA LA PANTALLA DE LOGIN ──────────────────────────────
    # Aquí se define todo el estilo visual del login:
    # - fondo de pantalla con overlay oscuro
    # - tarjeta de acceso centrada con sombra y bordes redondeados
    # - tipografía limpia y jerarquía visual
    # - efecto hover en el botón
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');

    /* ── Animación de glow pulsante para el título ── */
    @keyframes glowPulse {{
        0%   {{ text-shadow: 0 0 10px #00d4ff, 0 0 25px rgba(0,212,255,0.5), 0 0 50px rgba(0,180,255,0.2); }}
        50%  {{ text-shadow: 0 0 20px #00d4ff, 0 0 50px rgba(0,212,255,0.8), 0 0 90px rgba(0,180,255,0.4); }}
        100% {{ text-shadow: 0 0 10px #00d4ff, 0 0 25px rgba(0,212,255,0.5), 0 0 50px rgba(0,180,255,0.2); }}
    }}
    /* ── Animación de scanline para el subtítulo ── */
    @keyframes fadeSlideUp {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    /* ── Parpadeo del cursor tecnológico ── */
    @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50%      {{ opacity: 0; }}
    }}

    /* ── Ocultar elementos de Streamlit innecesarios en el login ── */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    [data-testid="stToolbar"] {{ display: none; }}
    [data-testid="stDecoration"] {{ display: none; }}
    .stDeployButton {{ display: none; }}

    /* ── Fondo de pantalla completo con overlay oscuro-azul ── */
    html, body {{
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
    }}
    .stApp {{
        {bg_css}
    }}
    /* Overlay azul oscuro semitransparente sobre el fondo */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(
            135deg,
            rgba(5, 10, 30, 0.82) 0%,
            rgba(10, 30, 70, 0.75) 50%,
            rgba(5, 15, 40, 0.85) 100%
        );
        z-index: 0;
        pointer-events: none;
    }}

    /* ── Sidebar oculto / mínimo en login ── */
    section[data-testid="stSidebar"] {{
        display: none !important;
    }}

    /* ── Contenedor principal ── */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        position: relative;
        z-index: 1;
    }}

    /* ── Tarjeta de login centrada ── */
    /* Para cambiar colores de la tarjeta, modifica los valores de background y border abajo */
    .login-card {{
        background: linear-gradient(
            145deg,
            rgba(8, 20, 50, 0.92) 0%,
            rgba(12, 28, 65, 0.95) 100%
        );
        border: 1px solid rgba(0, 180, 220, 0.35);
        border-radius: 20px;
        padding: 2.5rem 2.8rem;
        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.6),
            0 0 40px rgba(0, 180, 220, 0.08),
            inset 0 1px 0 rgba(255,255,255,0.07);
        max-width: 520px;
        margin: 0 auto;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }}

    /* ── Logo dentro de la tarjeta ── */
    .login-logo-wrap {{
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    .login-logo-wrap img {{
        max-width: 150px;   /* Cambia este valor para ajustar el tamaño del logo */
        height: auto;
        filter: drop-shadow(0 4px 16px rgba(0,180,220,0.45));
        border-radius: 12px;
    }}

    /* ── Separador visual luminoso ── */
    .login-divider {{
        border: none;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(0, 212, 255, 0.15) 20%,
            rgba(0, 212, 255, 0.6) 50%,
            rgba(0, 212, 255, 0.15) 80%,
            transparent 100%
        );
        margin: 1rem 0 1.4rem 0;
        box-shadow: 0 0 8px rgba(0,212,255,0.3);
    }}

    /* ── Título principal ── */
    /* Fuente Orbitron: tipografía sci-fi tecnológica */
    .login-title {{
        font-family: 'Orbitron', 'Share Tech Mono', monospace;
        font-size: 2.15rem;
        font-weight: 900;
        color: #00e5ff;
        animation: glowPulse 3s ease-in-out infinite;
        text-align: center;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
        line-height: 1.2;
    }}
    /* Cursor parpadeante al final del título */
    .login-title::after {{
        content: '_';
        animation: blink 1.1s step-end infinite;
        color: #00d4ff;
        font-size: 1.8rem;
    }}

    /* ── Subtítulo institucional ── */
    .login-sub {{
        text-align: center;
        color: #a8d8ea;
        font-size: 0.86rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
        line-height: 1.7;
        animation: fadeSlideUp 0.8s ease both;
        text-shadow: 0 0 12px rgba(168,216,234,0.3);
    }}

    /* ── Lema de valor ── */
    .login-tagline {{
        text-align: center;
        color: #00d4ff;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.82rem;
        font-weight: 400;
        letter-spacing: 1px;
        margin-bottom: 1rem;
        padding: 0.45rem 1rem;
        background: rgba(0,212,255,0.06);
        border: 1px solid rgba(0,212,255,0.18);
        border-radius: 6px;
        animation: fadeSlideUp 1s ease both;
    }}

    /* ── Badges académicos ── */
    .badge-acad {{
        display: inline-block;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.35);
        border-radius: 20px;
        padding: 0.25rem 0.8rem;
        font-size: 0.72rem;
        font-weight: 600;
        color: #a8d8ea;
        margin: 0.15rem;
        letter-spacing: 0.5px;
        text-shadow: 0 0 6px rgba(0,212,255,0.3);
    }}

    /* ── Inputs dentro del login ── */
    .stTextInput > div > div > input {{
        background: rgba(5, 15, 40, 0.9) !important;
        border: 1px solid rgba(0, 180, 220, 0.3) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        padding: 0.6rem 1rem !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px rgba(0,212,255,0.25) !important;
    }}
    .stTextInput label {{
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }}

    /* ── Botón Ingresar con efecto hover ── */
    /* Cambia los colores de gradient para personalizar el botón */
    .stButton > button {{
        background: linear-gradient(135deg, #0e4080 0%, #1a6fa8 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 212, 255, 0.5) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 1px !important;
        padding: 0.65rem 1.5rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 15px rgba(0,100,200,0.3) !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #1a6fa8 0%, #00d4ff 100%) !important;
        color: #05101e !important;
        box-shadow: 0 6px 25px rgba(0,212,255,0.45) !important;
        transform: translateY(-2px) !important;
    }}

    /* ── Bloque de usuarios de prueba ── */
    .login-demo-users {{
        background: rgba(0, 50, 100, 0.35);
        border: 1px solid rgba(0, 150, 200, 0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-top: 1rem;
        font-size: 0.78rem;
        color: #7fb3d3;
        font-family: 'Share Tech Mono', monospace;
    }}
    .login-demo-users strong {{
        color: #00d4ff;
    }}

    /* ── Nota académica ── */
    .login-nota {{
        background: rgba(30, 15, 0, 0.5);
        border-left: 3px solid rgba(245, 158, 11, 0.6);
        border-radius: 0 8px 8px 0;
        padding: 0.7rem 1rem;
        margin-top: 1rem;
        font-size: 0.72rem;
        color: rgba(220, 180, 100, 0.85);
        line-height: 1.5;
    }}

    /* ── Footer discreto en login ── */
    .login-footer {{
        text-align: center;
        color: rgba(100, 130, 160, 0.6);
        font-size: 0.68rem;
        margin-top: 1rem;
    }}

    /* ── Bienvenida superior ── */
    .login-welcome {{
        text-align: center;
        color: rgba(180, 220, 255, 0.9);
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(0,180,255,0.35);
        animation: fadeSlideUp 0.6s ease both;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(5,10,25,0.5); }}
    ::-webkit-scrollbar-thumb {{ background: #1e3a5f; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #00d4ff; }}

    /* ── Logos en las 4 esquinas ── */
    /* Para ajustar el tamaño cambia width en .corner-logo img */
    .corner-logo {{
        position: fixed;
        z-index: 9999;
        opacity: 0.88;
        transition: opacity 0.25s, transform 0.25s;
    }}
    .corner-logo:hover {{
        opacity: 1;
        transform: scale(1.08);
    }}
    .corner-logo img {{
        width: 110px;   /* Cambia este valor para ajustar el tamaño de los logos de esquina */
        height: auto;
        filter: drop-shadow(0 2px 14px rgba(0,212,255,0.55));
        border-radius: 10px;
    }}
    .corner-tl {{ top: 16px;    left: 18px;  }}
    .corner-tr {{ top: 16px;    right: 18px; }}
    .corner-bl {{ bottom: 16px; left: 18px;  }}
    .corner-br {{ bottom: 16px; right: 18px; }}

    /* ── Alertas dentro del login ── */
    .stAlert {{
        border-radius: 10px !important;
        border-left: 4px solid !important;
        background: rgba(180,83,9,0.12) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def show_corner_logo() -> None:
    """
    Muestra el logo 1833387-middle.png en las 4 esquinas de la pantalla de login.
    - Para cambiar la imagen: reemplaza assets/1833387-middle.png.
    - Para ajustar tamaño: edita width en la clase .corner-logo img del CSS.
    - Si la imagen no existe, no muestra nada (sin errores).
    """
    # ── RUTA DEL LOGO DE ESQUINA ───────────────────────────────────────
    corner_path = "assets/1833387-middle.png"
    b64 = _img_to_base64(corner_path)
    if not b64:
        return  # Si no existe la imagen, no muestra nada
    img_tag = f'<img src="data:image/png;base64,{b64}" alt="Logo institucional" />'
    # Renderiza el logo en las 4 esquinas (top-left, top-right, bottom-left, bottom-right)
    st.markdown(f"""
    <div class="corner-logo corner-tl">{img_tag}</div>
    <div class="corner-logo corner-tr">{img_tag}</div>
    <div class="corner-logo corner-bl">{img_tag}</div>
    <div class="corner-logo corner-br">{img_tag}</div>
    """, unsafe_allow_html=True)


def show_logo(size_px: int = 150) -> str:
    """
    Devuelve HTML con el logo oficial.
    - Para cambiar el logo, reemplaza assets/Logo.png.
    - size_px controla el tamaño en píxeles.
    - Si el logo no existe, muestra un emoji como fallback.
    """
    # ── RUTA DEL LOGO ───────────────────────────────────────────────────────
    # Para cambiar el logo, modifica la ruta de abajo:
    logo_path = "assets/Logo.png"
    b64 = _img_to_base64(logo_path)

    if b64:
        return f"""
        <div class="login-logo-wrap">
            <img src="data:image/png;base64,{b64}" width="{size_px}"
                 alt="Logo ReproTrace Basic 360°" />
        </div>
        """
    else:
        # Fallback visual si el logo no se encuentra
        return f"""
        <div class="login-logo-wrap" style="font-size:{size_px//3}px;padding:0.5rem 0">
            🏥
        </div>
        """


def render_login_card():
    """
    Renderiza la tarjeta de acceso completa del login:
    - Logo, título, subtítulo, lema de valor.
    - Campos de usuario y contraseña.
    - Botón Ingresar con lógica de autenticación.
    - Bloque con usuarios de prueba.
    - Nota académica obligatoria.
    - Footer institucional discreto.
    """
    # ── Mensaje de bienvenida (encima de la tarjeta) ────────────────────────
    st.markdown("""
    <div class="login-welcome">
        Bienvenido al sistema académico de trazabilidad y reprocesamiento hospitalario.
    </div>
    """, unsafe_allow_html=True)

    # ── Columnas para centrar la tarjeta ───────────────────────────────────
    # Para desplazar la tarjeta, ajusta los ratios de las columnas:
    col_l, col_card, col_r = st.columns([1, 2, 1])

    with col_card:
        # ── Logo oficial ──────────────────────────────────────────────────
        st.markdown(show_logo(160), unsafe_allow_html=True)

        # ── Título y subtítulos ───────────────────────────────────────────
        st.markdown("""
        <div class="login-title">ReproTrace Basic 360°</div>
        <div class="login-sub">
            Sistema de monitoreo y trazabilidad<br>
            para centrales de reprocesamiento hospitalario
        </div>
        <div class="login-tagline">
            Seguridad, calidad y trazabilidad en cada etapa del proceso.
        </div>
        <hr class="login-divider">
        <div style="text-align:center;margin-bottom:1rem">
            <span class="badge-acad">🎓 Universidad Libre · Barranquilla</span>
            <span class="badge-acad">⚗️ Instrumentación Quirúrgica</span>
            <span class="badge-acad">🔬 Prototipo Académico v2.0</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Campos de login ───────────────────────────────────────────────
        # Usamos un contenedor para agrupar visualmente
        u = st.text_input("👤  Usuario", key="li_user", placeholder="admin")
        p = st.text_input("🔒  Contraseña", type="password", key="li_pass",
                          placeholder="••••••••")

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        # ── Botón Ingresar ────────────────────────────────────────────────
        if st.button("▶  Ingresar al sistema", use_container_width=True, key="btn_login"):
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
                st.error("⚠️ Usuario o contraseña incorrectos.")

        # ── Usuarios de prueba ────────────────────────────────────────────
        st.markdown("""
        <div class="login-demo-users">
            <strong>Accesos de prueba:</strong><br>
            🔑 admin / admin123 &nbsp;·&nbsp;
            🔑 central / central123 &nbsp;·&nbsp;
            🔑 docente / docente123
        </div>
        """, unsafe_allow_html=True)

        # ── Nota académica obligatoria ────────────────────────────────────
        # El texto de esta nota está definido en la constante NOTA_ACAD
        st.markdown(f"""
        <div class="login-nota">
            ⚠️ <strong>Nota académica:</strong> {NOTA_ACAD}
        </div>
        """, unsafe_allow_html=True)

        # ── Footer institucional discreto ─────────────────────────────────
        st.markdown("""
        <div class="login-footer">
            Desarrollado como prototipo académico para Instrumentación Quirúrgica &nbsp;·&nbsp;
            Universidad Libre Seccional Barranquilla · 2026
        </div>
        """, unsafe_allow_html=True)


# ─── CSS Tecnológico (panel interno post-login) ───────────────────────────────
TECH_CSS = """
<style>
/* ── Fuente y fondo ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Fondo degradado oscuro ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b35 50%, #0a1628 100%);
    color: #e2e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050d1f 0%, #0a1628 100%) !important;
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; font-size: 0.85rem; }
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { color: #e2e8f0 !important; }

/* ── Header custom ── */
.rt-header {
    background: linear-gradient(90deg, #0f3460 0%, #1a5276 50%, #154360 100%);
    border-bottom: 2px solid #00d4ff;
    padding: 1rem 1.5rem;
    border-radius: 0 0 12px 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(0,212,255,0.15);
    display: flex;
    align-items: center;
    gap: 1rem;
}
.rt-header-logo {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #00d4ff;
    text-shadow: 0 0 20px rgba(0,212,255,0.5);
    letter-spacing: 1px;
}
.rt-header-sub {
    font-size: 0.78rem;
    color: #7fb3d3;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.rt-header-badge {
    margin-left: auto;
    background: rgba(0,212,255,0.1);
    border: 1px solid #00d4ff;
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #00d4ff;
}

/* ── Métricas ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1b35 0%, #0f2444 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 20px rgba(0,212,255,0.2);
    border-color: #00d4ff;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #7fb3d3 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00d4ff !important; font-family: 'Share Tech Mono', monospace; font-size: 1.8rem;
}

/* ── Botones ── */
.stButton > button {
    background: linear-gradient(135deg, #0f3460 0%, #1a5276 100%) !important;
    color: #00d4ff !important;
    border: 1px solid #00d4ff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.1) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input {
    background: #0d1b35 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 8px rgba(0,212,255,0.2) !important;
}

/* ── Tablas ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    overflow: hidden;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: linear-gradient(90deg, #0d1b35, #0f2444) !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #00d4ff !important;
}

/* ── Alertas ── */
.stAlert {
    border-radius: 10px !important;
    border-left: 4px solid !important;
}
div[data-baseweb="notification"][kind="error"] {
    background: rgba(185,28,28,0.15) !important;
    border-left-color: #ef4444 !important;
}
div[data-baseweb="notification"][kind="warning"] {
    background: rgba(180,83,9,0.15) !important;
    border-left-color: #f59e0b !important;
}
div[data-baseweb="notification"][kind="success"] {
    background: rgba(21,128,61,0.15) !important;
    border-left-color: #22c55e !important;
}
div[data-baseweb="notification"][kind="info"] {
    background: rgba(29,78,216,0.15) !important;
    border-left-color: #3b82f6 !important;
}

/* ── Separadores ── */
hr { border-color: #1e3a5f !important; }

/* ── Títulos ── */
h1, h2, h3 { color: #e2e8f0 !important; }
h1 { border-bottom: 1px solid #1e3a5f; padding-bottom: .5rem; }

/* ── Texto general ── */
p, label, .stMarkdown { color: #cbd5e1 !important; }
.stCaption { color: #64748b !important; }

/* ── Card panel login ── */
.login-card {
    background: linear-gradient(135deg, #050d1f 0%, #0d1b35 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 40px rgba(0,212,255,0.05);
    max-width: 700px;
    margin: 0 auto;
}
.login-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem;
    color: #00d4ff;
    text-shadow: 0 0 30px rgba(0,212,255,0.4);
    text-align: center;
    letter-spacing: 2px;
}
.login-sub {
    text-align: center;
    color: #7fb3d3;
    font-size: 0.85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.badge-acad {
    display:inline-block;
    background: rgba(0,212,255,0.08);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.72rem;
    color: #7fb3d3;
    margin: 0.2rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }

/* ── Radio menu sidebar ── */
.stRadio > div { gap: 0.2rem; }
.stRadio label { padding: 0.4rem 0.8rem; border-radius: 6px; transition: background 0.15s; }
.stRadio label:hover { background: rgba(0,212,255,0.08); }
</style>
"""

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

import re as _re
# Patrón de lote aceptado — flexible para contexto hospitalario colombiano:
# Ejemplos válidos: LOTE-2026-001 | CRE-2026-045 | L-2026-001 | C-001 | C001
# Mínimo: 3 caracteres alfanuméricos (con guiones opcionales)
# Máximo: 30 caracteres. No permite espacios ni caracteres especiales.
# Referencia: práctica recomendada Circular 01/2016 Supersalud Colombia.
BATCH_PATTERN = _re.compile(r'^[A-Za-z0-9][A-Za-z0-9\-]{1,28}[A-Za-z0-9]$')
BATCH_HINT    = "Formato: letras, números y guiones (-). Mín. 3 caracteres. Ej: LOTE-2026-001, C-001, CRE-2026-045"

USERS = {
    "admin":   {"password": "admin123",   "role": "Administrador"},
    "central": {"password": "central123", "role": "Personal de central"},
    "docente": {"password": "docente123", "role": "Docente/Tutor"},
}

SEV_ICON  = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}

# Tiempos mínimos de duración total por etapa (minutos)
# Fuentes: AAMI ST79:2017 §6-11, ISO 15883-1:2006, ISO 17664:2017,
#          OPS/OMS Guía reprocesamiento 2016, Circular 01/2016 Supersalud Colombia
STAGE_MIN_DURATION = {
    "Recepción":                         2.0,   # Conteo, revisión y registro (práctica recomendada)
    "Limpieza y descontaminación":       5.0,   # AAMI ST79 §6.2 / ISO 15883-1 (mínimo manual)
    "Inspección funcional":              2.0,   # Revisión visual y funcional (práctica recomendada)
    "Empaque":                           2.0,   # Sellado y etiquetado (práctica recomendada)
    "Esterilización":                    7.0,   # Ciclo vapor 134°C mínimo (EN 285 / AAMI ST79 Table 11.1)
    "Validación / liberación de carga":  5.0,   # Lectura indicadores + decisión de liberación
    "Almacenamiento":                    1.0,   # Ubicación y registro
    "Distribución":                      1.0,   # Entrega y firma
}

# Tiempos mínimos de EXPOSICIÓN por tipo de ciclo (minutos)
# Fuentes: EN 285:2015 §22.3.2, AAMI ST79:2017 Table 11.1,
#          ISO 11135:2014 §10 (ETO), ISO 22441:2022 (VH2O2/plasma)
STERIL_MIN_EXPOSURE = {
    "Vapor 134°C":              3.0,   # EN 285 §22.3.2 / AAMI ST79 Table 11.1
    "Vapor 121°C":             15.0,   # AAMI ST79 Table 11.1 (15-30 min según carga)
    "Baja temperatura":        60.0,   # ISO 11135:2014 §10 (óxido de etileno típico)
    "Peróxido de hidrógeno":   28.0,   # ISO 22441:2022 / AAMI ST58 (plasma VH2O2)
    "Otro":                     1.0,   # Referirse a instrucciones del fabricante
}

# Parámetros mínimos de TEMPERATURA y PRESIÓN por tipo de ciclo
# Fuentes: EN 285:2015 Table 1 §22.3, AAMI ST79:2017 Table 11.1
STERIL_MIN_TEMP = {
    "Vapor 134°C":            134.0,   # EN 285:2015 Table 1 / AAMI ST79 Table 11.1
    "Vapor 121°C":            121.0,   # AAMI ST79 Table 11.1
    "Baja temperatura":        None,   # varía según agente (ETO, H2O2) — fabricante
    "Peróxido de hidrógeno":  45.0,   # Sterrad 100NX típico (indicativo)
    "Otro":                    None,   # según fabricante
}
STERIL_MIN_PRESSURE = {                # presion manometrica en bar (relativa)
    "Vapor 134°C":             2.05,  # EN 285:2015 §22.3 (3.0 bar abs ≈ 2.05 bar manometrico)
    "Vapor 121°C":             1.04,  # AAMI ST79 Table 11.1 (2.07 bar abs ≈ 1.04 bar manometrico)
    "Baja temperatura":        None,
    "Peróxido de hidrógeno":  None,
    "Otro":                    None,
}

AUTO_REC = {
    "Indicador biológico no conforme": "Rechazar la carga, inmovilizar el material, repetir el ciclo y notificar al coordinador.",
    "Instrumental dañado":             "Retirar del circuito, reportar novedad, verificar el set y documentar mantenimiento.",
    "Validación pendiente":            "No distribuir hasta completar la liberación de carga.",
    "Trazabilidad incompleta":         "Revisar registros por etapa, responsables, lote y fechas antes de liberar.",
    "Ciclo rechazado":                 "Reprocesar la carga, documentar causa y verificar parámetros del equipo.",
    "Limpieza no conforme":            "Rechazar etapa, identificar fallo, repetir con método adecuado y documentar.",
    "Incumplimiento de protocolo":     "Detener el proceso en la etapa afectada, identificar y documentar la desviación, reevaluar con el supervisor y registrar en el plan de mejora antes de continuar.",
    "Paquete no apto":                 "Retirar inmediatamente el paquete del circuito. Evaluar si aplica reempaque o reprocesamiento completo según el estado del instrumental.",
    "Paquete dañado en entrega":       "No utilizar el instrumental. Reportar la novedad al servicio receptor, retirar del quirófano y reprocesar desde la etapa de inspección funcional.",
    "Vencimiento próximo":             "Planificar uso o redistribución del lote antes de la fecha de vencimiento. Verificar condiciones de almacenamiento.",
    "Paquete vencido":                 "Retirar inmediatamente del almacenamiento. No distribuir. Evaluar reprocesamiento completo desde Limpieza y descontaminación.",
    "Tiempo insuficiente en etapa":     "Verificar el registro de fecha/hora de inicio y fin. Si el tiempo fue real, documentar desviación y evaluar reprocesamiento según protocolo del servicio.",
    "Tiempo de exposición insuficiente": "RECHAZAR LA CARGA. Exposición por debajo del mínimo normativo no garantiza esterilidad. Reprocesar con parámetros correctos y verificar calibración del equipo.",
    "Etapa duplicada":                   "Revisar si el segundo registro corresponde a un reproceso justificado o a un error de digitación. Documentar la causa y corregir la trazabilidad del lote.",
    "Parámetro real insuficiente (temperatura)":  "RECHAZAR LA CARGA. Temperatura real registrada en impresión no alcanzó el mínimo normativo (EN 285:2015 / AAMI ST79). Verificar calibración del equipo y reprocesar.",
    "Parámetro real insuficiente (presión)":      "RECHAZAR LA CARGA. Presión real registrada en impresión no alcanzó el mínimo normativo (EN 285:2015 §22.3). Verificar calibración del equipo y reprocesar.",
    "Parámetro real insuficiente (exposición)":   "RECHAZAR LA CARGA. Tiempo de exposición real registrado en impresión insuficiente. Reprocesar con parámetros correctos y verificar calibración.",
    "Límite de ciclos superado":                  "RETIRAR DEL CIRCUITO. El instrumental superó el límite de ciclos de reprocesamiento indicado por el fabricante (ISO 17664:2017). Dar de baja, documentar disposición final y reemplazar.",
    "Ciclos próximos al límite":                  "Planificar reemplazo del instrumental. Está próximo al límite de ciclos del fabricante (ISO 17664:2017). No descartarlo aún, pero gestionar adquisición de reemplazo.",
    "Equipo sin calibración vigente":             "BLOQUEAR uso del equipo. No esterilizar hasta obtener certificado de calibración vigente. Contactar entidad metrológica acreditada (ISO 17665-1 / ISO 15883-1 / Res. 4816/2008).",
    "Calibración de equipo próxima a vencer":     "Programar calibración antes del vencimiento. El equipo puede seguir operando, pero debe gestionarse la renovación del certificado (ISO 17665-1 §10 / AAMI ST79:2017 §12.4).",
    "No conformidad abierta":                     "Investigar causa raíz, registrar acción correctiva y preventiva en el módulo de No Conformidades. Verificar eficacia y cerrar con evidencia. (ISO 13485:2016 §8.7 / Res. 4816/2008)",
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
        manufacturer TEXT, model TEXT, max_cycles INTEGER,
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
        actual_temperature REAL, actual_pressure REAL, actual_exposure_time REAL,
        physical_indicator TEXT, chemical_indicator TEXT,
        biological_indicator TEXT, release_result TEXT,
        release_supervisor TEXT,
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
    # ─ Vinculación instrumental → paciente (ISO 13485:2016 §8.3 / Res. 4816/2008) ─
    cur.execute("""CREATE TABLE IF NOT EXISTS patient_deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT NOT NULL,
        batch_code TEXT NOT NULL,
        patient_id TEXT NOT NULL,
        patient_initials TEXT,
        procedure_type TEXT,
        operating_room TEXT,
        delivery_date TEXT,
        registered_by TEXT,
        created_at TEXT)""")
    # ─ Índices de rendimiento ──────────────────────────────────────────────
    # process_records: consultas más frecuentes por lote/instrumento y etapa
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pr_code_batch  ON process_records(instrument_code, batch_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pr_stage       ON process_records(stage)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pr_created_at  ON process_records(created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pr_result      ON process_records(result)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pr_exp_date    ON process_records(expiration_date)")
    # alerts: filtros por estado, severidad y lote
    cur.execute("CREATE INDEX IF NOT EXISTS idx_al_code_batch  ON alerts(instrument_code, batch_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_al_status_sev  ON alerts(status, severity)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_al_created_at  ON alerts(created_at)")
    # audit_log: filtros por usuario y módulo
    cur.execute("CREATE INDEX IF NOT EXISTS idx_aud_username   ON audit_log(username)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_aud_module     ON audit_log(module)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_aud_created_at ON audit_log(created_at)")
    # improvement_plans: filtro por estado pendiente
    cur.execute("CREATE INDEX IF NOT EXISTS idx_imp_state      ON improvement_plans(state)")
    # patient_deliveries: trazabilidad paciente y búsqueda recall
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pd_code_batch  ON patient_deliveries(instrument_code, batch_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pd_patient_id  ON patient_deliveries(patient_id)")
    # recall_events: eventos formales de retiro de lote
    cur.execute("""CREATE TABLE IF NOT EXISTS recall_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT NOT NULL,
        batch_code TEXT NOT NULL,
        trigger_type TEXT NOT NULL,
        trigger_description TEXT,
        patients_affected INTEGER DEFAULT 0,
        corrective_action TEXT,
        status TEXT NOT NULL DEFAULT 'Activo',
        closed_by TEXT,
        closed_at TEXT,
        closure_notes TEXT,
        registered_by TEXT,
        created_at TEXT)""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_re_code_batch ON recall_events(instrument_code, batch_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_re_status     ON recall_events(status)")
    # equipment_calibration: calibración y validación de equipos (ISO 17665 / ISO 15883)
    cur.execute("""CREATE TABLE IF NOT EXISTS equipment_calibration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id   TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        equipment_type TEXT,
        last_calibration_date TEXT,
        next_calibration_date TEXT NOT NULL,
        calibration_entity TEXT,
        certificate_number TEXT,
        result TEXT DEFAULT 'Conforme',
        observations TEXT,
        registered_by TEXT,
        created_at TEXT)""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ec_equip_id       ON equipment_calibration(equipment_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ec_next_cal_date  ON equipment_calibration(next_calibration_date)")
    # nonconformities: no conformidades vinculadas a alertas (ISO 13485:2016 §8.7 / Res. 4816/2008)
    cur.execute("""CREATE TABLE IF NOT EXISTS nonconformities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id       INTEGER,
        instrument_code TEXT,
        batch_code      TEXT,
        nc_type        TEXT NOT NULL,
        description    TEXT NOT NULL,
        root_cause     TEXT,
        corrective_action TEXT,
        preventive_action TEXT,
        responsible    TEXT,
        due_date       TEXT,
        status         TEXT NOT NULL DEFAULT 'Abierta',
        closed_by      TEXT,
        closed_at      TEXT,
        closure_evidence TEXT,
        registered_by  TEXT,
        created_at     TEXT)""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nc_alert_id      ON nonconformities(alert_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nc_code_batch    ON nonconformities(instrument_code, batch_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nc_status        ON nonconformities(status)")
    c.commit(); c.close()

def _migrate_db():
    """Agrega tablas, columnas e índices nuevos sin romper BD existente (migración segura)."""
    c = connect()
    # ─ Nuevas tablas (IF NOT EXISTS = idempotente) ───────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS patient_deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT NOT NULL,
        batch_code TEXT NOT NULL,
        patient_id TEXT NOT NULL,
        patient_initials TEXT,
        procedure_type TEXT,
        operating_room TEXT,
        delivery_date TEXT,
        registered_by TEXT,
        created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS recall_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrument_code TEXT NOT NULL,
        batch_code TEXT NOT NULL,
        trigger_type TEXT NOT NULL,
        trigger_description TEXT,
        patients_affected INTEGER DEFAULT 0,
        corrective_action TEXT,
        status TEXT NOT NULL DEFAULT 'Activo',
        closed_by TEXT,
        closed_at TEXT,
        closure_notes TEXT,
        registered_by TEXT,
        created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS equipment_calibration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id   TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        equipment_type TEXT,
        last_calibration_date TEXT,
        next_calibration_date TEXT NOT NULL,
        calibration_entity TEXT,
        certificate_number TEXT,
        result TEXT DEFAULT 'Conforme',
        observations TEXT,
        registered_by TEXT,
        created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS nonconformities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id       INTEGER,
        instrument_code TEXT,
        batch_code      TEXT,
        nc_type        TEXT NOT NULL,
        description    TEXT NOT NULL,
        root_cause     TEXT,
        corrective_action TEXT,
        preventive_action TEXT,
        responsible    TEXT,
        due_date       TEXT,
        status         TEXT NOT NULL DEFAULT 'Abierta',
        closed_by      TEXT,
        closed_at      TEXT,
        closure_evidence TEXT,
        registered_by  TEXT,
        created_at     TEXT)""")
    c.commit()
    # ─ Nuevas columnas ──────────────────────────────────────────────────
    for stmt in [
        "ALTER TABLE alerts ADD COLUMN closing_reason TEXT",
        "ALTER TABLE process_records ADD COLUMN release_supervisor TEXT",
        "ALTER TABLE process_records ADD COLUMN actual_temperature REAL",
        "ALTER TABLE process_records ADD COLUMN actual_pressure REAL",
        "ALTER TABLE process_records ADD COLUMN actual_exposure_time REAL",
        "ALTER TABLE instruments ADD COLUMN manufacturer TEXT",
        "ALTER TABLE instruments ADD COLUMN model TEXT",
        "ALTER TABLE instruments ADD COLUMN max_cycles INTEGER",
    ]:
        try:
            c.execute(stmt); c.commit()
        except sqlite3.OperationalError:
            pass  # columna ya existe
    # ─ Índices (idempotentes: IF NOT EXISTS) ────────────────────────────
    idx_stmts = [
        "CREATE INDEX IF NOT EXISTS idx_pr_code_batch  ON process_records(instrument_code, batch_code)",
        "CREATE INDEX IF NOT EXISTS idx_pr_stage       ON process_records(stage)",
        "CREATE INDEX IF NOT EXISTS idx_pr_created_at  ON process_records(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_pr_result      ON process_records(result)",
        "CREATE INDEX IF NOT EXISTS idx_pr_exp_date    ON process_records(expiration_date)",
        "CREATE INDEX IF NOT EXISTS idx_al_code_batch  ON alerts(instrument_code, batch_code)",
        "CREATE INDEX IF NOT EXISTS idx_al_status_sev  ON alerts(status, severity)",
        "CREATE INDEX IF NOT EXISTS idx_al_created_at  ON alerts(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_aud_username   ON audit_log(username)",
        "CREATE INDEX IF NOT EXISTS idx_aud_module     ON audit_log(module)",
        "CREATE INDEX IF NOT EXISTS idx_aud_created_at ON audit_log(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_imp_state      ON improvement_plans(state)",
        "CREATE INDEX IF NOT EXISTS idx_pd_code_batch  ON patient_deliveries(instrument_code, batch_code)",
        "CREATE INDEX IF NOT EXISTS idx_pd_patient_id  ON patient_deliveries(patient_id)",
        "CREATE INDEX IF NOT EXISTS idx_re_code_batch ON recall_events(instrument_code, batch_code)",
        "CREATE INDEX IF NOT EXISTS idx_re_status     ON recall_events(status)",
        "CREATE INDEX IF NOT EXISTS idx_ec_equip_id       ON equipment_calibration(equipment_id)",
        "CREATE INDEX IF NOT EXISTS idx_ec_next_cal_date  ON equipment_calibration(next_calibration_date)",
        "CREATE INDEX IF NOT EXISTS idx_nc_alert_id      ON nonconformities(alert_id)",
        "CREATE INDEX IF NOT EXISTS idx_nc_code_batch    ON nonconformities(instrument_code, batch_code)",
        "CREATE INDEX IF NOT EXISTS idx_nc_status        ON nonconformities(status)",
    ]
    for stmt in idx_stmts:
        try:
            c.execute(stmt); c.commit()
        except sqlite3.OperationalError:
            pass
    c.close()

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


def _check_equipment_calibration(equipment_id: str) -> None:
    """Genera alertas cuando un equipo esterilizador tiene calibración vencida o próxima a vencer.

    Consulta el registro más reciente de equipment_calibration para el equipo indicado.
    - Vencida  (today >= next_calibration_date): alerta Alta  'Equipo sin calibración vigente'
    - Próxima  (0 < días restantes ≤ 30):        alerta Media 'Calibración de equipo próxima a vencer'
    Idempotente: no genera alerta si ya existe una abierta del mismo tipo para el equipo.

    Referencia: ISO 17665-1:2006 §10 / ISO 15883-1:2009 §6.3 /
                AAMI ST79:2017 §12.4 / Resolución 4816/2008 MinSalud Colombia.
    """
    row = query_df(
        "SELECT next_calibration_date,equipment_name FROM equipment_calibration "
        "WHERE equipment_id=? ORDER BY next_calibration_date DESC LIMIT 1",
        (equipment_id,))
    if row.empty:
        return
    eq_name = row.iloc[0]["equipment_name"]
    try:
        next_cal = date.fromisoformat(str(row.iloc[0]["next_calibration_date"]))
    except (ValueError, TypeError):
        return
    today = date.today()
    days_left = (next_cal - today).days

    def _has_open(atype):
        ex = query_df(
            "SELECT id FROM alerts WHERE instrument_code=? AND alert_type=? AND status='Abierta'",
            (equipment_id,))
        return not ex.empty and (ex["alert_type"] == atype).any() if "alert_type" in ex.columns else not ex.empty

    # Reutilizamos instrument_code para identificar equipo en la tabla de alertas
    if days_left < 0:
        ex = query_df(
            "SELECT id FROM alerts WHERE instrument_code=? AND alert_type='Equipo sin calibración vigente' AND status='Abierta'",
            (equipment_id,))
        if ex.empty:
            add_alert(equipment_id, "—", "Equipo sin calibración vigente", "Alta",
                      f"Equipo '{eq_name}' ({equipment_id}): calibración vencida desde "
                      f"{next_cal.isoformat()} ({abs(days_left)} días de atraso). "
                      f"No utilizar para esterilización hasta renovar el certificado. "
                      f"(ISO 17665-1 / AAMI ST79:2017 §12.4)")
    elif days_left <= 30:
        ex = query_df(
            "SELECT id FROM alerts WHERE instrument_code=? AND alert_type='Calibración de equipo próxima a vencer' AND status='Abierta'",
            (equipment_id,))
        if ex.empty:
            add_alert(equipment_id, "—", "Calibración de equipo próxima a vencer", "Media",
                      f"Equipo '{eq_name}' ({equipment_id}): calibración vence en "
                      f"{days_left} día(s) ({next_cal.isoformat()}). "
                      f"Programar renovación de certificado. "
                      f"(ISO 17665-1 §10 / AAMI ST79:2017 §12.4)")


def _get_operator_stats(rec: "pd.DataFrame") -> "pd.DataFrame":
    """Métricas de calidad por operador (campo 'responsible' de process_records).

    Columnas calculadas:
      Registros       — total de registros del operador
      Cumplimientos   — registros con complies == 'Sí'
      % Cumplimiento  — porcentaje de cumplimiento
      Rechazados      — registros con result == 'Rechazado'
      Etapa más freq. — etapa con mayor frecuencia de registros
      T. prom. (min)  — tiempo promedio de etapas (duration_minutes)

    Referencia: ISO 13485:2016 §6.2 — competencia del personal /
                OPS-OMS Guía CEyE 2016.
    """
    if rec.empty:
        return pd.DataFrame()
    rows = []
    for op, g in rec.groupby("responsible", sort=False):
        total = len(g)
        cumple = int((g["complies"] == "Sí").sum())
        rechazados = int((g["result"] == "Rechazado").sum())
        pct = round(cumple / total * 100, 1) if total else 0.0
        etapa_frec = g["stage"].value_counts().idxmax() if total else "—"
        dur = g["duration_minutes"].dropna()
        t_prom = round(float(dur.mean()), 1) if not dur.empty else 0.0
        rows.append({
            "Operador": op,
            "Registros": total,
            "Cumplimientos": cumple,
            "% Cumplimiento": pct,
            "Rechazados": rechazados,
            "Etapa más freq.": etapa_frec,
            "T. prom. (min)": t_prom,
        })
    return (pd.DataFrame(rows)
            .sort_values("% Cumplimiento", ascending=True)
            .reset_index(drop=True))


def _chart_operator_stats(df_op: "pd.DataFrame"):
    """Gráfica de barras horizontales: % cumplimiento por operador."""
    plt = _get_plt()
    fig, ax = plt.subplots(figsize=(7, max(2, len(df_op) * 0.55)))
    colors = ["#d62728" if v < 90 else "#ff7f0e" if v < 95 else "#2ca02c"
              for v in df_op["% Cumplimiento"]]
    ax.barh(df_op["Operador"], df_op["% Cumplimiento"], color=colors, height=0.6)
    ax.axvline(95, color="#555555", linestyle="--", linewidth=1, label="Meta 95 %")
    ax.set_xlabel("% Cumplimiento")
    ax.set_xlim(0, 105)
    for i, (v, r) in enumerate(zip(df_op["% Cumplimiento"], df_op["Rechazados"])):
        label = f"{v}%  ({r} rec.)" if r > 0 else f"{v}%"
        ax.text(v + 1, i, label, va="center", fontsize=8)
    ax.legend(fontsize=8)
    ax.set_title("Cumplimiento por operador (meta ≥ 95 %)\nReferencia: ISO 13485:2016 §6.2", fontsize=9)
    fig.tight_layout()
    return fig


def _calc_failure_rate(rec):
    """
    Tasa de reprocesamiento fallido:
    % de lotes únicos con al menos un 'Rechazado' en Esterilización
    o Validación / liberación de carga.
    Base: lotes que al menos registraron Esterilización.
    Referencia: AAMI ST79 §11 / OPS/OMS 2016 – indicador de calidad CEYE.
    """
    if rec.empty: return None, 0, 0
    est = rec[rec["stage"].isin(["Esterilización","Validación / liberación de carga"])]
    if est.empty: return None, 0, 0
    lotes = est.groupby(["instrument_code","batch_code"])
    total = len(lotes)
    fallidos = sum(1 for _,g in lotes if (g["result"]=="Rechazado").any())
    tasa = (fallidos/total*100) if total else 0
    return round(tasa,1), fallidos, total

def _check_expiring_packages():
    """Genera alertas automáticas por paquetes vencidos o próximos a vencer (≤ 7 días)."""
    alm=query_df(
        "SELECT instrument_code,batch_code,expiration_date FROM process_records "
        "WHERE stage='Almacenamiento' AND expiration_date IS NOT NULL AND expiration_date!=''")
    if alm.empty: return
    today=date.today()
    exist=query_df("SELECT instrument_code,batch_code,alert_type FROM alerts WHERE status='Abierta'")
    dist=query_df("SELECT DISTINCT instrument_code,batch_code FROM process_records WHERE stage='Distribución'")
    for _,row in alm.iterrows():
        code,batch=row["instrument_code"],row["batch_code"]
        if not dist.empty and ((dist["instrument_code"]==code)&(dist["batch_code"]==batch)).any(): continue
        try: exp=date.fromisoformat(str(row["expiration_date"]))
        except (ValueError,TypeError): continue
        days=(exp-today).days
        def _has(atype,c=code,b=batch):
            return not exist.empty and ((exist["instrument_code"]==c)&(exist["batch_code"]==b)&(exist["alert_type"]==atype)).any()
        if days<0 and not _has("Paquete vencido"):
            add_alert(code,batch,"Paquete vencido","Alta",f"Paquete vencido desde {exp.isoformat()}. No distribuir. Reprocesar.")
        elif 0<=days<=7 and not _has("Vencimiento próximo"):
            add_alert(code,batch,"Vencimiento próximo","Media",f"Paquete vence en {days} día(s) ({exp.isoformat()}). Planificar uso o reprocesamiento.")

def _check_instrument_lifecycle(code: str) -> None:
    """Genera alerta cuando un instrumento alcanza o supera el límite de ciclos del fabricante.

    Referencia: ISO 17664:2017 — instrucciones del fabricante para reprocesamiento.
    Solo actúa si max_cycles fue definido en el registro del instrumental.
    """
    ins=query_df("SELECT name,max_cycles FROM instruments WHERE code=?",(code,))
    if ins.empty: return
    row=ins.iloc[0]
    max_c=row.get("max_cycles")
    if not max_c or max_c<=0: return          # sin límite definido
    max_c=int(max_c)
    # Contar ciclos completados de esterilización (≈ 1 ciclo de reprocesamiento)
    done=query_df(
        "SELECT COUNT(*) as n FROM process_records WHERE instrument_code=? AND stage='Esterilización'",
        (code,)).iloc[0]["n"]
    done=int(done)
    name=row.get("name","")
    pct=done/max_c
    # Alerta Alta: límite superado
    if pct>=1.0:
        ex_al=query_df(
            "SELECT id FROM alerts WHERE instrument_code=? AND alert_type='Límite de ciclos superado' AND status='Abierta'",
            (code,))
        if ex_al.empty:
            add_alert(code,"—","Límite de ciclos superado","Alta",
                      f"'{name}' ({code}) alcanzó {done}/{max_c} ciclos de reprocesamiento. "
                      f"Supera el límite del fabricante (ISO 17664:2017). Retirar del circuito y evaluar baja.")
    # Alerta Media: ≥80 % del límite
    elif pct>=0.8:
        ex_al=query_df(
            "SELECT id FROM alerts WHERE instrument_code=? AND alert_type='Ciclos próximos al límite' AND status='Abierta'",
            (code,))
        if ex_al.empty:
            add_alert(code,"—","Ciclos próximos al límite","Media",
                      f"'{name}' ({code}) llevan {done}/{max_c} ciclos "
                      f"({pct*100:.0f}% del límite del fabricante — ISO 17664:2017). Planificar reemplazo.")

def _trigger_recall(code: str, batch: str, trigger_type: str, description: str, user: str) -> bool:
    """Crea un evento formal de retiro de lote si el lote fue distribuido a pacientes.

    Retorna True si el recall fue activado. Res. 4816/2008 MinSalud / ISO 13485:2016 §8.3.
    Solo crea el evento si no existe ya uno activo con el mismo trigger para el mismo lote.
    """
    # Verificar si el lote fue distribuido (patient_deliveries o stage Distribución)
    pd_cnt = query_df(
        "SELECT COUNT(*) as n FROM patient_deliveries WHERE instrument_code=? AND batch_code=?",
        (code, batch)).iloc[0]["n"]
    dist_cnt = query_df(
        "SELECT COUNT(*) as n FROM process_records WHERE instrument_code=? AND batch_code=? AND stage='Distribución'",
        (code, batch)).iloc[0]["n"]
    if pd_cnt == 0 and dist_cnt == 0:
        return False   # lote no distribuido — no requiere recall
    # Evitar duplicados: si ya existe un recall Activo por el mismo trigger en este lote, salir
    existing = query_df(
        "SELECT id FROM recall_events WHERE instrument_code=? AND batch_code=? "
        "AND trigger_type=? AND status='Activo'",
        (code, batch, trigger_type))
    if not existing.empty:
        return False
    # Acción correctiva recomendada
    corr = AUTO_REC.get(trigger_type,
           "Aislar el lote, notificar al jefe de central y al equipo clínico. "
           "Documentar y abrir plan de mejora. Res. 4816/2008 MinSalud Colombia.")
    execute("""
        INSERT INTO recall_events
            (instrument_code,batch_code,trigger_type,trigger_description,
             patients_affected,corrective_action,status,registered_by,created_at)
        VALUES(?,?,?,?,?,?,'Activo',?,?)""",
        (code, batch, trigger_type, description,
         int(pd_cnt), corr, user, datetime.now().isoformat()))
    audit(user, "Recall activado automaticamente", "Recall",
          f"{code}/{batch} | Causa: {trigger_type} | Pacientes expuestos: {int(pd_cnt)}")
    return True

# ─── Gráficas ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
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

def _survey_excel(df: pd.DataFrame) -> bytes:
    """Genera un Excel con los resultados de la encuesta de percepción."""
    LABELS = {
        "id": "ID", "role": "Cargo / Rol", "experience_years": "Años de experiencia",
        "q1": "P1 – Fácil de usar", "q2": "P2 – Facilita registro",
        "q3": "P3 – Reduce errores", "q4": "P4 – Mejora trazabilidad",
        "q5": "P5 – Control de etapas", "q6": "P6 – Optimiza tiempo",
        "q7": "P7 – Comodidad de uso", "q8": "P8 – Seguridad del paciente",
        "q9": "P9 – Organización del trabajo", "q10": "P10 – Recomendaría su uso",
        "comments": "Comentarios", "created_at": "Fecha de registro",
    }
    out = df.rename(columns={k: v for k, v in LABELS.items() if k in df.columns})
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        wb = w.book
        hf = wb.add_format({"bold": True, "bg_color": "#1F4E79", "font_color": "white", "border": 1})
        tf = wb.add_format({"bold": True, "font_size": 13})
        nf = wb.add_format({"italic": True, "font_color": "gray"})
        out.to_excel(w, sheet_name="Encuestas", index=False, startrow=2)
        s = w.sheets["Encuestas"]
        s.write(0, 0, f"{APP_NAME} – Encuesta de percepción – {now}", tf)
        s.write(1, 0, NOTA_ACAD, nf)
        for i, col in enumerate(out.columns):
            s.write(2, i, col, hf)
            cw = max(len(str(col)) + 4, out[col].astype(str).str.len().max() + 2 if not out.empty else 10)
            s.set_column(i, i, min(cw, 50))
        s.autofilter(2, 0, 2 + len(out), len(out.columns) - 1)
        # Hoja de promedios por pregunta
        means = df[[f"q{i}" for i in range(1,11)]].mean().round(2)
        ws2 = wb.add_worksheet("Promedios por pregunta")
        ws2.write(0, 0, f"{APP_NAME} – Promedios – {now}", tf)
        ws2.write(2, 0, "Pregunta", hf); ws2.write(2, 1, "Promedio (1-5)", hf)
        labels = [LABELS.get(f"q{i}", f"P{i}") for i in range(1,11)]
        for r, (label, val) in enumerate(zip(labels, means.values)):
            ws2.write(3 + r, 0, label); ws2.write(3 + r, 1, float(val))
        ws2.set_column(0, 0, 50); ws2.set_column(1, 1, 20)
    buf.seek(0)
    return buf.read()

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
        ws(ins,"Instrumental"); ws(rec,"Registros")
        # Hoja Alertas: renombrar columnas clave para legibilidad
        if not alerts.empty:
            _al_export=alerts.rename(columns={
                "id":"ID","instrument_code":"Código","batch_code":"Lote",
                "alert_type":"Tipo de alerta","severity":"Severidad",
                "description":"Descripción","status":"Estado",
                "closed_by":"Cerrada por","closed_at":"Fecha de cierre",
                "closing_reason":"Justificación de cierre","created_at":"Fecha creación"})
            ws(_al_export,"Alertas")
            # Hoja exclusiva de alertas cerradas con justificación
            _cerradas=_al_export[_al_export["Estado"]=="Cerrada"].copy()
            if not _cerradas.empty:
                ws(_cerradas[["ID","Código","Lote","Tipo de alerta","Severidad",
                               "Descripción","Cerrada por","Fecha de cierre",
                               "Justificación de cierre"]],"Alertas_Cerradas")
        else:
            ws(alerts,"Alertas")
        ws(survey,"Encuestas"); ws(plans,"Plan_Mejora")
        if not rec.empty:
            t=rec.groupby(["instrument_code","batch_code"])["stage"].apply(list).reset_index()
            t["completadas"]=t["stage"].apply(len)
            t["estado"]=t["stage"].apply(lambda s:"Completa" if set(STAGES).issubset(set(s)) else "Incompleta")
            t.drop(columns=["stage"],inplace=True); ws(t,"Trazabilidad")
        # Hoja Vinculación Paciente
        pd_data=query_df("SELECT * FROM patient_deliveries")
        if not pd_data.empty:
            ws(pd_data.rename(columns={
                "id":"ID","instrument_code":"Código","batch_code":"Lote",
                "patient_id":"ID Paciente","patient_initials":"Iniciales",
                "procedure_type":"Procedimiento","operating_room":"Quirófano/Sala",
                "delivery_date":"Fecha entrega","registered_by":"Registrado por",
                "created_at":"Fecha creación"}),"Vinculacion_Paciente")
        else:
            ws(pd.DataFrame(columns=["ID","Código","Lote","ID Paciente","Iniciales",
                                     "Procedimiento","Quirófano/Sala","Fecha entrega",
                                     "Registrado por","Fecha creación"]),"Vinculacion_Paciente")
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
                ("Alertas cerradas con justificación",
                 len(alerts[(alerts['status']=='Cerrada')&(alerts.get('closing_reason','').fillna('')!='')]) if not alerts.empty and 'closing_reason' in alerts.columns else 0),
                ("Tasa de reprocesamiento fallido (%)",
                 f"{_calc_failure_rate(rec)[0]}" if not rec.empty else "N/A"),
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
        def normalize_text(self, txt):
            # Transliterate common non-Latin-1 chars so core fonts don't crash
            txt = (str(txt)
                .replace("\u2013", "-")    # en dash
                .replace("\u2014", "--")   # em dash
                .replace("\u2018", "'")    # left single quote
                .replace("\u2019", "'")    # right single quote
                .replace("\u201c", '"')    # left double quote
                .replace("\u201d", '"')    # right double quote
                .replace("\u2026", "...")  # ellipsis
                .replace("\u00b0", "\u00b0"))  # degree sign – keep as-is (latin-1 0xB0)
            return super().normalize_text(txt)
        def header(self):
            self.set_font("Helvetica","B",10)
            self.cell(0,8,f"{APP_NAME} - Informe de Trazabilidad",**_NL,align="C")
            self.set_draw_color(30,80,130); self.set_line_width(0.5)
            self.line(10,self.get_y(),200,self.get_y()); self.ln(3)
        def footer(self):
            self.set_y(-15); self.set_font("Helvetica","I",8)
            self.cell(0,8,f"Generado: {now}  -  Pag. {self.page_no()}",align="C")
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
                 f"Barranquilla - Colombia  |  {now}",
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
    """
    Pantalla de acceso principal.
    - Aplica fondo institucional mediante apply_login_background().
    - Muestra tarjeta de acceso elegante mediante render_login_card().
    - El registro de nuevos usuarios se mantiene en un expander adicional.
    """
    # ── Aplicar fondo y estilos del login ───────────────────────────────────
    apply_login_background()

    # ── Logo en la esquina superior derecha ───────────────────────────────
    show_corner_logo()

    # ── Mostrar tarjeta principal de login ──────────────────────────────────
    render_login_card()

    # ── Registro de nuevos usuarios (expander discreto) ─────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    _, col_reg, _ = st.columns([1, 2, 1])
    with col_reg:
        with st.expander("📝 ¿Nuevo usuario? Crear cuenta", expanded=False):
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

def _live_avatar_floating():
    """Inyecta el widget LiveAvatar como iframe flotante fijo en la esquina inferior derecha."""
    _la_key = st.secrets.get("liveavatar", {}).get("api_key", "")
    _la_params = "?orientation=horizontal"
    if _la_key and _la_key not in ("PEGA_AQUI_TU_CLAVE_API", "tu_clave_aqui", ""):
        _la_params += f"&api_key={_la_key}"
    avatar_url = f"https://embed.liveavatar.com/v1/c46cf5ac-deb0-4078-8d23-a0438f4d3482{_la_params}"
    # JS que escapa el sandbox de components.html e inyecta el iframe en el DOM raíz
    st_components.html(f"""
    <script>
    (function() {{
        var _id = 'liveavatar-floating-widget';
        if (window.parent.document.getElementById(_id)) return;
        var iframe = window.parent.document.createElement('iframe');
        iframe.id = _id;
        iframe.src = '{avatar_url}';
        iframe.allow = 'microphone';
        iframe.title = 'Asistente LiveAvatar';
        iframe.style.cssText = [
            'position:fixed',
            'bottom:24px',
            'right:24px',
            'width:320px',
            'height:200px',
            'border:none',
            'border-radius:14px',
            'box-shadow:0 6px 32px rgba(0,0,0,0.5)',
            'z-index:99999',
            'background:#0d1b2a',
        ].join(';');
        window.parent.document.body.appendChild(iframe);
    }})();
    </script>
    """, height=0, scrolling=False)

def header():
    """
    Encabezado del panel interno post-login.
    Muestra el Logo.png en el sidebar y en el header superior.
    """
    now_str = datetime.now().strftime("%Y-%m-%d  %H:%M")

    # ── Logo en el header superior ──────────────────────────────────────────
    # Para cambiar el logo del encabezado, modifica show_logo() o assets/Logo.png
    logo_html = show_logo(48)  # 48px en el header
    st.markdown(f"""
    <div class="rt-header">
        <div style="display:flex;align-items:center;gap:0.8rem">
            <div style="line-height:0">{logo_html.replace('<div class="login-logo-wrap">','<div style="line-height:0">').replace('max-width: 150px','max-width:48px')}</div>
            <div>
                <div class="rt-header-logo">{APP_NAME}</div>
                <div class="rt-header-sub">Sistema de Trazabilidad · {VERSION}</div>
            </div>
        </div>
        <div class="rt-header-badge">🕐 {now_str}</div>
    </div>""", unsafe_allow_html=True)

    # ── Logo y usuario en el sidebar ────────────────────────────────────────
    logo_b64 = _img_to_base64("assets/Logo.png")
    if logo_b64:
        st.sidebar.markdown(f"""
        <div style="text-align:center;padding:0.8rem 0 0.4rem 0">
            <img src="data:image/png;base64,{logo_b64}" width="100"
                 style="filter:drop-shadow(0 2px 8px rgba(0,180,220,0.4));border-radius:10px;"
                 alt="Logo ReproTrace" />
        </div>
        """, unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="background:rgba(0,212,255,0.08);border:1px solid #1e3a5f;border-radius:10px;
                padding:0.8rem;margin-bottom:0.8rem;text-align:center;">
        <div style="font-size:1.5rem">👤</div>
        <div style="font-weight:700;color:#00d4ff;font-size:0.9rem">{st.session_state['user']}</div>
        <div style="font-size:0.72rem;color:#7fb3d3;text-transform:uppercase;letter-spacing:1px">{st.session_state['role']}</div>
    </div>""", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Cerrar sesión", use_container_width=True):
        execute("INSERT INTO login_sessions(username,role,event,timestamp) VALUES(?,?,?,?)",
                (st.session_state["user"],st.session_state["role"],"Cierre de sesión",datetime.now().isoformat()))
        audit(st.session_state["user"],"Cierre de sesión","Login")
        st.session_state.clear(); st.rerun()
    st.sidebar.markdown(inst_footer())
    # ── Asistente LiveAvatar (widget flotante) ───────────────────────────────
    _live_avatar_floating()

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
    # Panel de paquetes próximos a vencer
    _check_expiring_packages()
    _alm_exp=query_df(
        "SELECT instrument_code,batch_code,expiration_date FROM process_records "
        "WHERE stage='Almacenamiento' AND expiration_date IS NOT NULL AND expiration_date!=''")
    if not _alm_exp.empty:
        _dist=query_df("SELECT DISTINCT instrument_code,batch_code FROM process_records WHERE stage='Distribución'")
        _today=date.today(); _prox=[]
        for _,_r in _alm_exp.iterrows():
            if not _dist.empty and ((_dist["instrument_code"]==_r["instrument_code"])&(_dist["batch_code"]==_r["batch_code"])).any(): continue
            try:
                _e=date.fromisoformat(str(_r["expiration_date"])); _d=(_e-_today).days
                if _d<=7: _prox.append({"Código":_r["instrument_code"],"Lote":_r["batch_code"],"Vence":str(_e),"Días":_d})
            except (ValueError,TypeError): pass
        if _prox:
            st.subheader("📦 Paquetes próximos a vencer (≤ 7 días)")
            for _row in sorted(_prox,key=lambda x:x["Días"]):
                _msg=f"**{_row['Código']}** / Lote `{_row['Lote']}` — vence el **{_row['Vence']}**"
                if _row["Días"]<0:   st.error(f"🔴 {_msg} (VENCIDO hace {abs(int(_row['Días']))} día(s))")
                else:                st.warning(f"🟡 {_msg} ({int(_row['Días'])} día(s) restantes)")
    # ── Panel de lotes críticos ──────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🚨 Panel de lotes críticos")
    st.caption("Lotes con alertas Alta abiertas o trazabilidad incompleta. Requieren acción antes de continuar el proceso.")
    if not rec.empty:
        # Construir tabla de estado por lote
        _lotes = rec.groupby(["instrument_code","batch_code"])["stage"].apply(list).reset_index()
        _lotes["etapas_completas"] = _lotes["stage"].apply(lambda s: len(set(s) & set(STAGES)))
        _lotes["etapas_faltantes"] = _lotes["stage"].apply(
            lambda s: [e for e in STAGES if e not in s])
        _lotes["trazabilidad"] = _lotes["etapas_faltantes"].apply(
            lambda f: "✅ Completa" if not f else f"⚠️ Faltan {len(f)}")
        # Alertas Alta abiertas por lote
        _al_alta = query_df(
            "SELECT instrument_code,batch_code,COUNT(*) as n_alertas "
            "FROM alerts WHERE status='Abierta' AND severity='Alta' "
            "GROUP BY instrument_code,batch_code")
        _lotes = _lotes.merge(_al_alta, on=["instrument_code","batch_code"], how="left")
        _lotes["n_alertas"] = _lotes["n_alertas"].fillna(0).astype(int)
        # Solo lotes con algún problema
        _criticos = _lotes[(_lotes["n_alertas"]>0) | (_lotes["etapas_faltantes"].apply(len)>0)].copy()
        if _criticos.empty:
            st.success("🟢 Sin lotes críticos. Todos los lotes tienen trazabilidad completa y sin alertas Alta abiertas.")
        else:
            # Filtros interactivos
            _fc1,_fc2 = st.columns(2)
            _fcode = _fc1.text_input("🔍 Filtrar por código",key="crit_code")
            _fbatch = _fc2.text_input("🔍 Filtrar por lote",key="crit_batch")
            if _fcode:
                _criticos = _criticos[_criticos["instrument_code"].str.contains(_fcode,case=False,na=False)]
            if _fbatch:
                _criticos = _criticos[_criticos["batch_code"].str.contains(_fbatch,case=False,na=False)]
            # Tabla enriquecida
            _tabla = _criticos[["instrument_code","batch_code","etapas_completas","trazabilidad","n_alertas"]].copy()
            _tabla["faltantes"] = _criticos["etapas_faltantes"].apply(lambda f: ", ".join(f) if f else "—")
            _tabla.columns = ["Código","Lote","Etapas completas","Trazabilidad","Alertas Alta 🔴","Etapas faltantes"]
            _tabla = _tabla.sort_values("Alertas Alta 🔴", ascending=False).reset_index(drop=True)
            st.dataframe(_tabla, use_container_width=True)
            st.caption(f"🔴 {len(_criticos)} lote(s) requieren atención. Navegue a Alertas o Trazabilidad para gestionar cada caso.")
    else:
        st.info("Sin registros de proceso aún.")
    # ── Panel de recalls activos ─────────────────────────────────────────────
    _recalls=query_df("SELECT instrument_code,batch_code,trigger_type,patients_affected,created_at FROM recall_events WHERE status='Activo' ORDER BY created_at DESC")
    if not _recalls.empty:
        st.markdown("---")
        st.subheader("🚨 Retiros de lote activos")
        st.error(f"⚠️ **{len(_recalls)} evento(s) de retiro ACTIVO(S).** Acceda al módulo '🚨 Retiro de lote (Recall)' para gestionarlos.")
        st.dataframe(_recalls.rename(columns={
            "instrument_code":"Código","batch_code":"Lote","trigger_type":"Causa",
            "patients_affected":"Pacientes expuestos","created_at":"Activado en"}),
            use_container_width=True)

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
            st.markdown("**🔄 Ciclo de vida (ISO 17664:2017)**")
            st.caption("Ingrese la información del fabricante para controlar el límite de reprocesos.")
            lc1,lc2,lc3=st.columns(3)
            mfr=lc1.text_input("Fabricante",placeholder="Aesculap, KLS Martin…")
            mdl=lc2.text_input("Modelo / referencia",placeholder="BB417R")
            max_c=lc3.number_input("Máx. ciclos de reprocesamiento",min_value=0,value=0,
                                    help="0 = no definido / ilimitado. Consulte las instrucciones del fabricante (ISO 17664:2017).")
            if st.form_submit_button("💾 Guardar"):
                if not code.strip() or not name.strip():
                    st.error("Código y nombre son obligatorios.")
                else:
                    try:
                        execute("""INSERT INTO instruments(code,name,category,spaulding,service_origin,quantity,status,observations,manufacturer,model,max_cycles,registered_by,created_at)
                                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                (code.strip(),name.strip(),cat,spa,srv,qty,sta,obs,
                                 mfr.strip(),mdl.strip(),max_c if max_c>0 else None,
                                 st.session_state["user"],datetime.now().isoformat()))
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
    # ─ Tabla de ciclos de vida ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🔄 Ciclos de reprocesamiento por instrumento")
    st.caption("Fuente: registros de Esterilización completados. Referencia: ISO 17664:2017.")
    rec_all=query_df("SELECT instrument_code FROM process_records WHERE stage='Esterilización'")
    if not rec_all.empty and not df.empty:
        cycles_df=rec_all.groupby("instrument_code").size().reset_index(name="ciclos_realizados")
        merged=df[["code","name","max_cycles","status"]].merge(
            cycles_df, left_on="code", right_on="instrument_code", how="left")
        merged["ciclos_realizados"]=merged["ciclos_realizados"].fillna(0).astype(int)
        merged["max_cycles"]=merged["max_cycles"].where(merged["max_cycles"].notna(), None)
        def _pct(row):
            if row["max_cycles"] and row["max_cycles"]>0:
                return f"{row['ciclos_realizados']}/{int(row['max_cycles'])} ({row['ciclos_realizados']/row['max_cycles']*100:.0f}%)"
            return f"{row['ciclos_realizados']} / sin límite"
        def _estado(row):
            if row["max_cycles"] and row["max_cycles"]>0:
                p=row["ciclos_realizados"]/row["max_cycles"]
                if p>=1.0: return "🔴 Límite superado"
                if p>=0.8: return "🟡 Próximo al límite"
            return "🟢 OK"
        merged["uso"]=merged.apply(_pct,axis=1)
        merged["alerta_ciclos"]=merged.apply(_estado,axis=1)
        tabla=merged[["code","name","status","ciclos_realizados","uso","alerta_ciclos"]].rename(columns={
            "code":"Código","name":"Nombre","status":"Estado",
            "ciclos_realizados":"Ciclos realizados","uso":"Uso vs límite","alerta_ciclos":"Estado ciclo"})
        st.dataframe(tabla,use_container_width=True)
    else:
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
        st.caption(f"ℹ️ {BATCH_HINT}")
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
        act_temp=act_pres=act_exp_t=None  # parámetros reales de impresión
        ph_i=ch_i=bi_i=rel=""
        release_sup=""
        sl=s_d=p_c=ex_d=""
        ds=dr=rr=ps=""
        pat_id=pat_init=proc_type=or_room=""

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
            _prev_ins=query_df(
                "SELECT inspection_status FROM process_records WHERE instrument_code=? AND batch_code=? AND stage='Inspección funcional' ORDER BY created_at DESC LIMIT 1",
                (code,batch.strip()))
            if not _prev_ins.empty and _prev_ins.iloc[0]["inspection_status"]=="Requiere mantenimiento":
                st.error("🔴 BLOQUEO: Inspección funcional marcó este instrumental como 'Requiere mantenimiento'. "
                         "No puede esterilizarse hasta que se registre una nueva Inspección funcional con estado apto.")
            a,b=st.columns(2)
            st_e=a.text_input("Equipo esterilizador",placeholder="EST-01")
            cy_t=b.selectbox("Tipo de ciclo",["Vapor 134°C","Vapor 121°C","Baja temperatura","Peróxido de hidrógeno","Otro"])
            ld_n=st.text_input("N° carga",placeholder="C-001")
            st.markdown("**📌 Parámetros programados (objetivo)**")
            st.caption("Valores configurados en el equipo antes del ciclo.")
            pa1,pa2,pa3=st.columns(3)
            temp=pa1.number_input("Temp. objetivo °C",0.0,250.0,134.0 if cy_t=="Vapor 134°C" else 121.0)
            pres=pa2.number_input("Presión objetivo (bar)",0.0,10.0,2.1)
            exp_t=pa3.number_input("Exposición objetivo (min)",0.0,120.0,4.0)
            st.markdown("**📊 Parámetros reales (impresión / tira gráfica del equipo)**")
            st.caption("Ingrese los valores que figuren en la impresión o registro del ciclo. "
                       "Requerido por AAMI ST79:2017 §12 / EN 285:2015 §6.")
            ra1,ra2,ra3=st.columns(3)
            act_temp=ra1.number_input("Temp. real °C",0.0,250.0,temp,key="act_temp")
            act_pres=ra2.number_input("Presión real (bar)",0.0,10.0,pres,key="act_pres")
            act_exp_t=ra3.number_input("Exposición real (min)",0.0,120.0,exp_t,key="act_exp_t")
            # Indicadores de desviación en tiempo real
            _min_t=STERIL_MIN_TEMP.get(cy_t)
            _min_p=STERIL_MIN_PRESSURE.get(cy_t)
            _min_e=STERIL_MIN_EXPOSURE.get(cy_t,1.0)
            _flags=[]
            if _min_t and act_temp<_min_t:   _flags.append(f"Temp. real {act_temp:.1f}°C < mínimo {_min_t:.0f}°C")
            if _min_p and act_pres<_min_p:   _flags.append(f"Presión real {act_pres:.2f} bar < mínimo {_min_p:.2f} bar")
            if cy_t!="Otro" and act_exp_t<_min_e: _flags.append(f"Exposición real {act_exp_t:.1f} min < mínimo {_min_e:.0f} min")
            if _flags:
                st.error("🔴 Parámetros reales por debajo del mínimo normativo:\n" + "\n".join(f"  • {f}" for f in _flags))
        elif stage=="Validación / liberación de carga":
            a,b,c_=st.columns(3)
            ph_i=a.selectbox("Indicador físico",["Conforme","No conforme","No aplica"])
            ch_i=b.selectbox("Indicador químico",["Conforme","No conforme","No aplica"])
            bi_i=c_.selectbox("Indicador biológico",["Conforme","No conforme","Pendiente","No aplica"])
            rel=st.selectbox("Resultado de liberación",["Aprobado","Rechazado","Pendiente"])
            st.markdown("---")
            st.markdown("**👥 Doble verificación — principio de cuatro ojos** *(AAMI ST79:2017 §12 / IAHCSMM)*")
            st.caption("La liberación de carga requiere la firma de un segundo profesional independiente al responsable.")
            release_sup=st.text_input("Supervisor / segundo verificador ✱",
                                      placeholder="Nombre del supervisor o jefe de central",
                                      key="release_sup",
                                      help="Debe ser una persona distinta al responsable principal del registro.")
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
            st.markdown("---")
            st.markdown("**👤 Vinculación con paciente** *(ISO 13485:2016 §8.3 — trazabilidad postmercado)*")
            pa1,pa2=st.columns(2)
            pat_id=pa1.text_input("ID paciente / Historia clínica ✱",placeholder="HC-2026-00123",
                                  help="Requerido. Número de historia clínica o identificación del paciente.")
            pat_init=pa2.text_input("Iniciales del paciente",placeholder="J.G.R.",
                                    help="Opcional — para preservar privacidad en reportes.")
            pa3,pa4=st.columns(2)
            proc_type=pa3.selectbox("Tipo de procedimiento",
                ["Cirugía general","Ortopedia","Ginecología","Urología",
                 "Cardiovascular","Neurocirugía","Laparoscopia","Otorrinolaringología",
                 "Oftalmología","Urgencias","Otro"])
            or_room=pa4.text_input("Quirófano / Sala",placeholder="Quirófano 3")

        obs=st.text_area("Observaciones generales")
        # Advertencia de etapa ya registrada (visible antes de enviar)
        if batch.strip():
            _dup_chk=query_df(
                "SELECT id,created_at,responsible FROM process_records WHERE instrument_code=? AND batch_code=? AND stage=? ORDER BY created_at DESC LIMIT 1",
                (code,batch.strip(),stage))
            if not _dup_chk.empty:
                _dr=_dup_chk.iloc[0]
                st.warning(f"⚠️ Esta etapa ya fue registrada para este lote — "
                           f"{_dr['created_at'][:16]} por {_dr['responsible']}. "
                           "Si guarda de nuevo, quedará como registro adicional (desviación).")
        submit=st.form_submit_button("💾 Guardar etapa")

    if submit:
        if not batch.strip() or not resp.strip():
            st.error("Lote/carga y responsable son obligatorios."); return
        if not BATCH_PATTERN.match(batch.strip()):
            st.error(f"🔴 Formato de lote inválido: '{batch.strip()}'. {BATCH_HINT}")
            return
        if stage=="Distribución" and not pat_id.strip():
            st.error("🔴 El ID del paciente es obligatorio para registrar la distribución "
                     "(ISO 13485:2016 §8.3 — trazabilidad postmercado)."); return
        if stage=="Validación / liberación de carga":
            if not release_sup.strip():
                st.error("🔴 DOBLE VERIFICACIÓN REQUERIDA: Ingrese el nombre del supervisor o segundo verificador. "
                         "La liberación de carga requiere firma de dos personas distintas "
                         "(AAMI ST79:2017 §12 — principio de cuatro ojos)."); return
            if release_sup.strip().lower()==resp.strip().lower():
                st.error("🔴 DOBLE VERIFICACIÓN INVÁLIDA: El supervisor debe ser una persona "
                         "diferente al responsable principal del registro. "
                         "No se permite que una misma persona actúe como técnico y supervisor "
                         "(AAMI ST79:2017 §12 / IAHCSMM)."); return
        # Detección de etapa duplicada
        _dup=query_df(
            "SELECT id,created_at,responsible FROM process_records WHERE instrument_code=? AND batch_code=? AND stage=? ORDER BY created_at DESC LIMIT 1",
            (code,batch.strip(),stage))
        if not _dup.empty:
            _dr=_dup.iloc[0]
            add_alert(code,batch.strip(),"Etapa duplicada","Media",
                      f"'{stage}' fue registrada más de una vez para este lote. "
                      f"Primer registro: {_dr['created_at'][:16]} por {_dr['responsible']}. "
                      "Revisar si corresponde a reprocesamiento o error de digitación.")
        ok,msg=validate_stage_order(code,batch.strip(),stage)
        if not ok: st.warning(f"⚠️ {msg} Se guarda como desviación académica.")
        s_dt=datetime.combine(sd,st_); e_dt=datetime.combine(ed,et)
        if e_dt<s_dt: st.error("Hora final no puede ser anterior a la inicial."); return
        if stage=="Esterilización":
            _ins_mant=query_df(
                "SELECT inspection_status FROM process_records WHERE instrument_code=? AND batch_code=? AND stage='Inspección funcional' ORDER BY created_at DESC LIMIT 1",
                (code,batch.strip()))
            if not _ins_mant.empty and _ins_mant.iloc[0]["inspection_status"]=="Requiere mantenimiento":
                st.error("🔴 BLOQUEO DE SEGURIDAD: El instrumental fue marcado como 'Requiere mantenimiento' en "
                         "Inspección funcional. Realice el mantenimiento, actualice el estado en Registro de "
                         "instrumental y registre una nueva Inspección funcional con resultado apto antes de esterilizar.")
                return
            _emq=query_df(
                "SELECT alert_type FROM alerts WHERE instrument_code=? AND batch_code=? AND status='Abierta' AND severity='Alta' AND alert_type LIKE '%conforme%'",
                (code,batch.strip()))
            if not _emq.empty:
                st.error(f"🔴 BLOQUEO DE SEGURIDAD: El lote tiene {len(_emq)} alerta(s) de indicador no conforme abiertas. Resuelva las alertas de Empaque antes de esterilizar.")
                for _,_a in _emq.iterrows(): st.caption(f"• {_a['alert_type']}")
                return
            if cy_t and exp_t is not None:
                _min_exp=STERIL_MIN_EXPOSURE.get(cy_t,1.0)
                if exp_t<_min_exp and cy_t!="Otro":
                    st.error(f"🔴 BLOQUEO DE SEGURIDAD: El tiempo de exposición registrado ({exp_t:.1f} min) es inferior al "
                             f"mínimo normativo para '{cy_t}': {_min_exp:.0f} min "
                             f"(EN 285 / AAMI ST79 Table 11.1 / ISO 11135 / ISO 22441). "
                             "Corríjalo antes de guardar.")
                    return
            # Bloqueo de calibración vigente (Mejora Q) ───────────────────────
            if st_e and st_e.strip():
                _cal = query_df(
                    "SELECT next_calibration_date FROM equipment_calibration "
                    "WHERE equipment_id=? ORDER BY next_calibration_date DESC LIMIT 1",
                    (st_e.strip(),))
                if not _cal.empty:
                    try:
                        _ncd = date.fromisoformat(str(_cal.iloc[0]["next_calibration_date"]))
                        if date.today() >= _ncd:
                            _check_equipment_calibration(st_e.strip())
                            st.error(
                                f"🔴 BLOQUEO DE SEGURIDAD: El equipo '{st_e.strip()}' tiene calibración "
                                f"vencida desde {_ncd.isoformat()}. No puede usarse para esterilización "
                                f"hasta que se registre un certificado de calibración vigente. "
                                f"(ISO 17665-1 / AAMI ST79:2017 §12.4 / Res. 4816/2008)")
                            return
                    except (ValueError, TypeError):
                        pass
            # Validación de parámetros REALES (impresión ciclo) ───────────────
            if act_temp is not None and cy_t not in ("Otro",""):
                _min_t=STERIL_MIN_TEMP.get(cy_t)
                _min_p=STERIL_MIN_PRESSURE.get(cy_t)
                _min_e_r=STERIL_MIN_EXPOSURE.get(cy_t,1.0)
                _real_fails=[]
                if _min_t and act_temp<_min_t:
                    _real_fails.append(f"Temperatura real {act_temp:.1f}°C < mínimo normativo {_min_t:.0f}°C")
                if _min_p and act_pres<_min_p:
                    _real_fails.append(f"Presión real {act_pres:.2f} bar < mínimo normativo {_min_p:.2f} bar")
                if act_exp_t<_min_e_r and cy_t!="Otro":
                    _real_fails.append(f"Exposición real {act_exp_t:.1f} min < mínimo normativo {_min_e_r:.0f} min")
                if _real_fails:
                    st.error("🔴 BLOQUEO DE SEGURIDAD — PARÁMETROS REALES INSUFICIENTES:\n"
                             + "\n".join(f"  • {f}" for f in _real_fails)
                             + "\n\nLos valores registrados en la impresión del equipo no alcanzan los mínimos "
                               "normativos (EN 285:2015 / AAMI ST79:2017). No se garantiza la esterilidad. "
                               "Rechace la carga y reprocese.")
                    return
        if stage=="Distribución":
            _open=query_df(
                "SELECT alert_type FROM alerts WHERE instrument_code=? AND batch_code=? AND status='Abierta' AND severity='Alta'",
                (code,batch.strip()))
            if not _open.empty:
                st.error(f"🔴 BLOQUEO DE SEGURIDAD: El lote tiene {len(_open)} alerta(s) de riesgo ALTO abiertas. Ciérrelas en el módulo de Alertas antes de distribuir.")
                for _,_a in _open.iterrows(): st.caption(f"• {_a['alert_type']}")
                return
        dur=(e_dt-s_dt).total_seconds()/60
        execute("""INSERT INTO process_records(
            instrument_code,batch_code,stage,responsible,start_datetime,end_datetime,duration_minutes,complies,result,
            reception_origin,reception_initial_state,reception_quantity,
            cleaning_method,cleaning_complies,cleaning_novelties,
            inspection_status,
            package_type,chem_indicator_ext,chem_indicator_int,
            sterilizer_id,cycle_type,temperature,pressure,exposure_time,load_number,
            actual_temperature,actual_pressure,actual_exposure_time,
            physical_indicator,chemical_indicator,biological_indicator,release_result,release_supervisor,
            storage_location,storage_date,package_condition,expiration_date,
            destination_service,delivery_responsible,reception_responsible,package_state_delivery,
            observations,registered_by,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code,batch.strip(),stage,resp,s_dt.isoformat(),e_dt.isoformat(),dur,complies,result,
             r_ori,r_sta,r_qty,cl_m,cl_c,cl_n,ins_s,pk_t,ce_e,ce_i,
             st_e,cy_t,temp,pres,exp_t,ld_n,act_temp,act_pres,act_exp_t,
             ph_i,ch_i,bi_i,rel,release_sup.strip(),
             sl,s_d,p_c,ex_d,ds,dr,rr,ps,obs,st.session_state["user"],datetime.now().isoformat()))
        audit(st.session_state["user"],"Registro etapa","Proceso",f"{code}/{batch}/{stage}")
        if stage=="Validación / liberación de carga" and rel=="Aprobado":
            audit(st.session_state["user"],"Doble verificación — Liberación aprobada","Proceso",
                  f"{code}/{batch} | Técnico: {resp} | Supervisor: {release_sup.strip()}")
        if not ok: add_alert(code,batch.strip(),"Secuencia incompleta","Media",msg)
        if complies=="No": add_alert(code,batch.strip(),"Incumplimiento de protocolo","Alta",f"No cumple en {stage}. {obs}")
        if result=="Rechazado": add_alert(code,batch.strip(),"Ciclo rechazado","Alta",f"Rechazado en {stage}.")
        if ins_s in ["Incompleto","Dañado","Oxidado"]: add_alert(code,batch.strip(),"Instrumental dañado","Alta",f"Estado: {ins_s}.")
        if ce_e=="No conforme" or ce_i=="No conforme": add_alert(code,batch.strip(),"Indicador no conforme","Alta","Indicador químico no conforme en empaque.")
        if bi_i=="No conforme": add_alert(code,batch.strip(),"Indicador biológico no conforme","Alta","Indicador biológico no conforme. Rechazar carga.")
        if ch_i=="No conforme": add_alert(code,batch.strip(),"Indicador no conforme","Alta","Indicador químico no conforme en validación.")
        if cl_c=="No conforme": add_alert(code,batch.strip(),"Limpieza no conforme","Alta",f"Limpieza no conforme. {cl_n}")
        # ─ Detección automática de recall post-distribución (Res. 4816/2008 / ISO 13485 §8.3) ──
        _usr=st.session_state["user"]
        if bi_i=="No conforme":
            _rc=_trigger_recall(code,batch.strip(),"Indicador biológico no conforme",
                                f"Indicador biológico no conforme en {stage}. Lote potencialmente contaminado.",_usr)
            if _rc:
                st.error("🚨 RECALL ACTIVADO AUTOMÁTICAMENTE: el indicador biológico no conforme y este lote "
                         "ya fue distribuido. Se creó un Evento de Retiro en el módulo '🚨 Retiro de lote (Recall)'. "
                         "Notifique al personal clínico inmediatamente (Res. 4816/2008 MinSalud).")
        if result=="Rechazado" and stage in ["Esterilización","Validación / liberación de carga"]:
            _rc2=_trigger_recall(code,batch.strip(),"Ciclo rechazado",
                                 f"Ciclo rechazado en {stage}. Lote no apto para uso clínico.",_usr)
            if _rc2:
                st.error("🚨 RECALL ACTIVADO AUTOMÁTICAMENTE: ciclo rechazado y lote ya distribuido. "
                         "Verifique el módulo '🚨 Retiro de lote (Recall)' y active el protocolo institucional.")
        # ─ Validación de tiempos mínimos por etapa (AAMI ST79 / ISO 15883 / EN 285)
        _min_dur=STAGE_MIN_DURATION.get(stage,0)
        if dur<_min_dur:
            add_alert(code,batch.strip(),"Tiempo insuficiente en etapa","Media",
                      f"'{stage}' duró {dur:.1f} min, inferior al mínimo normativo de {_min_dur:.0f} min "
                      f"(AAMI ST79/ISO 15883/ISO 17664). Verificar registro de fechas/horas.")
        if stage=="Esterilización" and cy_t and exp_t is not None:
            _min_exp=STERIL_MIN_EXPOSURE.get(cy_t,1.0)
            if exp_t<_min_exp:
                add_alert(code,batch.strip(),"Tiempo de exposición insuficiente","Alta",
                          f"Ciclo '{cy_t}': exposición registrada {exp_t:.1f} min, mínimo normativo {_min_exp:.0f} min "
                          f"(EN 285 / AAMI ST79 Table 11.1 / ISO 11135 / ISO 22441). Rechazar carga.")
        # ─ Alertas por parámetros REALES insuficientes (AAMI ST79:2017 §12 / EN 285:2015) ──
        if stage=="Esterilización" and cy_t and act_temp is not None and cy_t not in ("Otro",""):
            _mn_t=STERIL_MIN_TEMP.get(cy_t); _mn_p=STERIL_MIN_PRESSURE.get(cy_t)
            _mn_e=STERIL_MIN_EXPOSURE.get(cy_t,1.0)
            if _mn_t and act_temp<_mn_t:
                add_alert(code,batch.strip(),"Parámetro real insuficiente (temperatura)","Alta",
                          f"Temperatura real: {act_temp:.1f}°C < mínimo: {_mn_t:.0f}°C "
                          f"(EN 285:2015 / AAMI ST79 Table 11.1). No se garantiza esterilidad. Rechazar carga.")
            if _mn_p and act_pres<_mn_p:
                add_alert(code,batch.strip(),"Parámetro real insuficiente (presión)","Alta",
                          f"Presión real: {act_pres:.2f} bar < mínimo: {_mn_p:.2f} bar "
                          f"(EN 285:2015 §22.3). No se garantiza esterilidad. Rechazar carga.")
            if act_exp_t<_mn_e:
                add_alert(code,batch.strip(),"Parámetro real insuficiente (exposición)","Alta",
                          f"Exposición real: {act_exp_t:.1f} min < mínimo: {_mn_e:.0f} min "
                          f"(EN 285 / AAMI ST79 Table 11.1). No se garantiza esterilidad. Rechazar carga.")
        if stage=="Almacenamiento" and p_c in ["Dañado","Vencido"]: add_alert(code,batch.strip(),"Paquete no apto","Alta",f"Paquete en almacenamiento con condición '{p_c}'. No distribuir hasta verificar estado.")
        if stage=="Distribución" and ps=="Dañado": add_alert(code,batch.strip(),"Paquete dañado en entrega","Alta",f"Paquete entregado con daño visible al servicio '{ds}'. Riesgo directo al paciente.")
        if stage=="Distribución":
            _val=query_df(
                "SELECT release_result FROM process_records WHERE instrument_code=? AND batch_code=? AND stage='Validación / liberación de carga'",
                (code,batch.strip()))
            if _val.empty or _val.iloc[0]["release_result"]!="Aprobado":
                add_alert(code,batch.strip(),"Validación pendiente","Alta","Distribución sin liberación de carga aprobada.")
        check_and_recommend()
        _check_expiring_packages()
        if stage=="Esterilización":
            _check_instrument_lifecycle(code)
            if st_e and st_e.strip():
                _check_equipment_calibration(st_e.strip())
        if stage=="Distribución" and pat_id.strip():
            execute("""
                INSERT INTO patient_deliveries
                    (instrument_code,batch_code,patient_id,patient_initials,
                     procedure_type,operating_room,delivery_date,registered_by,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (code, batch.strip(), pat_id.strip(), pat_init.strip(),
                 proc_type, or_room.strip(), s_dt.isoformat()[:10],
                 st.session_state["user"], datetime.now().isoformat()))
            audit(st.session_state["user"],"Vinculación paciente","Proceso",
                  f"{code}/{batch.strip()} → Paciente {pat_id.strip()}, {proc_type}, {or_room.strip()}")
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
    _alm_row=df[df["stage"]=="Almacenamiento"]
    if not _alm_row.empty:
        _exp_val=_alm_row.iloc[-1]["expiration_date"]
        if _exp_val and str(_exp_val) not in ("None","nan",""):
            try:
                _exp=date.fromisoformat(str(_exp_val)); _days=(_exp-date.today()).days
                if _days<0:    st.error(f"🔴 PAQUETE VENCIDO: venció el {_exp_val} (hace {abs(_days)} día(s)). No distribuir.")
                elif _days<=7: st.warning(f"🟡 VENCIMIENTO PRÓXIMO: {_days} día(s) restantes ({_exp_val}). Planificar uso urgente.")
            except (ValueError,TypeError): pass
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
    # ─ Pacientes vinculados ───────────────────────────────────────────────────
    st.subheader("👤 Pacientes vinculados a este lote")
    pd_df=query_df(
        "SELECT patient_id,patient_initials,procedure_type,operating_room,delivery_date,registered_by,created_at "
        "FROM patient_deliveries WHERE instrument_code=? AND batch_code=? ORDER BY created_at",
        (code,batch))
    if not pd_df.empty:
        st.info(f"ℹ️ {len(pd_df)} paciente(s) recibieron instrumental de este lote.")
        st.dataframe(pd_df.rename(columns={
            "patient_id":"ID Paciente","patient_initials":"Iniciales",
            "procedure_type":"Procedimiento","operating_room":"Quirófano/Sala",
            "delivery_date":"Fecha entrega","registered_by":"Registrado por",
            "created_at":"Creado en"}), use_container_width=True)
        if not al.empty and len(al[al["severity"]=="Alta"])>0:
            st.error("🚨 Este lote tiene alertas de riesgo ALTO. Evalúe activar protocolo de retiro de lote "
                     "en el módulo '🚨 Retiro de lote (Recall)'.")
    else:
        st.info("Sin vinculación de pacientes registrada para este lote.")

# ─── Retiro de lote / Recall ──────────────────────────────────────────────────
def recall_module():
    st.header("🚨 Retiro de lote (Recall) / Búsqueda por paciente")
    st.warning(
        "⚠️ Use esta función cuando se detecte una No Conformidad post-distribución que pueda "
        "afectar la seguridad del paciente. Permite identificar todos los pacientes expuestos "
        "a un lote específico y activar el protocolo de notificación. "
        "**Referencia normativa:** ISO 13485:2016 §8.3 — Resolución 4816/2008 MinSalud Colombia.")
    tab1, tab2, tab3 = st.tabs(["🔍 Búsqueda por lote", "👤 Búsqueda por paciente",
                                 "📋 Eventos de retiro activos"])
    with tab1:
        st.subheader("Pacientes expuestos a un lote específico")
        rc1,rc2=st.columns(2)
        r_code=rc1.text_input("Código del instrumental",key="rc_code",placeholder="IQ-001")
        r_batch=rc2.text_input("Número de lote",key="rc_batch",placeholder="LOTE-2026-001")
        if st.button("🔍 Buscar pacientes expuestos",key="rc_search"):
            if not r_code.strip() or not r_batch.strip():
                st.error("Ingrese código de instrumental y número de lote."); return
            pd_df=query_df(
                "SELECT patient_id,patient_initials,procedure_type,operating_room,"
                "delivery_date,registered_by,created_at "
                "FROM patient_deliveries WHERE instrument_code=? AND batch_code=? ORDER BY created_at",
                (r_code.strip(),r_batch.strip()))
            al_df=query_df(
                "SELECT alert_type,severity,description,status,created_at FROM alerts "
                "WHERE instrument_code=? AND batch_code=? ORDER BY severity,created_at",
                (r_code.strip(),r_batch.strip()))
            st.markdown("---")
            if not al_df.empty:
                alta_cnt=len(al_df[al_df["severity"]=="Alta"])
                if alta_cnt>0:
                    st.error(f"🔴 **Lote con {alta_cnt} alerta(s) de riesgo ALTO**")
                st.dataframe(al_df.rename(columns={
                    "alert_type":"Tipo de alerta","severity":"Severidad",
                    "description":"Descripción","status":"Estado","created_at":"Fecha"}),
                    use_container_width=True)
            else:
                st.success("✅ No se encontraron alertas para este lote.")
            if pd_df.empty:
                st.info("No hay pacientes vinculados a este lote.")
            else:
                n=len(pd_df)
                st.error(f"🚨 **{n} paciente(s) expuesto(s)** a este lote. "
                         "Activar protocolo institucional de notificación.")
                st.dataframe(pd_df.rename(columns={
                    "patient_id":"ID Paciente","patient_initials":"Iniciales",
                    "procedure_type":"Procedimiento","operating_room":"Quirófano/Sala",
                    "delivery_date":"Fecha entrega","registered_by":"Registrado por",
                    "created_at":"Creado en"}), use_container_width=True)
                # Descarga Excel del recall
                out=io.BytesIO()
                with pd.ExcelWriter(out,engine="xlsxwriter") as w:
                    pd_df.to_excel(w,sheet_name="Pacientes_expuestos",index=False)
                    if not al_df.empty:
                        al_df.to_excel(w,sheet_name="Alertas_lote",index=False)
                out.seek(0)
                st.download_button(
                    "📥 Descargar listado de recall (Excel)",
                    data=out.read(),
                    file_name=f"recall_{r_code.strip()}_{r_batch.strip()}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                audit(st.session_state["user"],"Consulta recall","Recall",
                      f"{r_code.strip()}/{r_batch.strip()} — {n} paciente(s) expuesto(s)")
    with tab2:
        st.subheader("Historial de lotes recibidos por un paciente")
        p_id=st.text_input("ID del paciente / Historia clínica",key="rc_pid",placeholder="HC-2026-00123")
        if st.button("🔍 Buscar historial del paciente",key="rc_pid_search"):
            if not p_id.strip():
                st.error("Ingrese el ID del paciente."); return
            pr_df=query_df(
                "SELECT instrument_code,batch_code,procedure_type,operating_room,"
                "delivery_date,registered_by,created_at "
                "FROM patient_deliveries WHERE patient_id=? ORDER BY created_at",
                (p_id.strip(),))
            st.markdown("---")
            if pr_df.empty:
                st.info("No se encontraron registros de entrega para este paciente.")
            else:
                st.warning(f"El paciente **{p_id.strip()}** tiene {len(pr_df)} registro(s) de entrega de instrumental.")
                st.dataframe(pr_df.rename(columns={
                    "instrument_code":"Código","batch_code":"Lote",
                    "procedure_type":"Procedimiento","operating_room":"Quirófano/Sala",
                    "delivery_date":"Fecha entrega","registered_by":"Registrado por",
                    "created_at":"Creado en"}), use_container_width=True)
                audit(st.session_state["user"],"Consulta paciente","Recall",
                      f"Paciente: {p_id.strip()} — {len(pr_df)} lote(s)")
    with tab3:
        st.subheader("📋 Eventos de retiro activos / histórico")
        st.caption("Generados automáticamente cuando se detecta un fallo crítico en un lote ya distribuido. "
                   "Res. 4816/2008 MinSalud — ISO 13485:2016 §8.3.")
        re_df=query_df("SELECT * FROM recall_events ORDER BY created_at DESC")
        if re_df.empty:
            st.success("✅ Sin eventos de retiro registrados.")
        else:
            activos=re_df[re_df["status"]=="Activo"]
            cerrados=re_df[re_df["status"]!="Activo"]
            if not activos.empty:
                st.error(f"🚨 **{len(activos)} evento(s) de retiro ACTIVO(S)** — requieren acción inmediata.")
                st.dataframe(activos[["id","instrument_code","batch_code","trigger_type",
                                      "trigger_description","patients_affected",
                                      "corrective_action","registered_by","created_at"]].rename(columns={
                    "id":"ID","instrument_code":"Código","batch_code":"Lote",
                    "trigger_type":"Causa","trigger_description":"Descripción",
                    "patients_affected":"Pacientes expuestos","corrective_action":"Acción correctiva",
                    "registered_by":"Registrado por","created_at":"Fecha activación"}),
                    use_container_width=True)
                # Cierre de evento de retiro
                st.markdown("---")
                st.subheader("Cerrar evento de retiro")
                st.caption("Complete el cierre sólo cuando todas las acciones correctivas hayan sido implementadas "
                           "y se haya notificado a los servicios clínicos afectados.")
                re_opts=[f"ID {r['id']} — {r['instrument_code']}/{r['batch_code']} — {r['trigger_type']}"
                         for _,r in activos.iterrows()]
                sel_re=st.selectbox("Evento a cerrar",re_opts,key="re_close_sel")
                re_id=int(sel_re.split("ID ")[1].split(" ")[0])
                closure_notes=st.text_area("Acciones realizadas y justificación de cierre *",
                                           key="re_close_notes",
                                           placeholder="Describa las acciones correctivas implementadas, "
                                           "notificaciones al personal clínico y resultado del seguimiento.")
                if st.button("✅ Cerrar evento de retiro",key="re_close_btn"):
                    if not closure_notes.strip():
                        st.error("Las notas de cierre son obligatorias."); return
                    _now=datetime.now().isoformat()
                    _usr=st.session_state["user"]
                    execute("UPDATE recall_events SET status='Cerrado',closed_by=?,closed_at=?,closure_notes=? WHERE id=?",
                            (_usr,_now,closure_notes.strip(),re_id))
                    audit(_usr,"Recall cerrado","Recall",
                          f"Evento {re_id} cerrado. Notas: {closure_notes.strip()[:80]}")
                    st.success(f"✅ Evento de retiro ID {re_id} cerrado. Acciones registradas en auditoría.")
                    st.rerun()
            else:
                st.success("✅ Sin eventos de retiro activos.")
            if not cerrados.empty:
                with st.expander(f"Historial de retiros cerrados ({len(cerrados)})"):
                    st.dataframe(cerrados[["id","instrument_code","batch_code","trigger_type",
                                           "patients_affected","closed_by","closed_at","closure_notes"]].rename(columns={
                        "id":"ID","instrument_code":"Código","batch_code":"Lote",
                        "trigger_type":"Causa","patients_affected":"Pacientes",
                        "closed_by":"Cerrado por","closed_at":"Fecha cierre",
                        "closure_notes":"Notas de cierre"}), use_container_width=True)
    with tab1:
        st.subheader("Pacientes expuestos a un lote específico")
        rc1,rc2=st.columns(2)
        r_code=rc1.text_input("Código del instrumental",key="rc_code",placeholder="IQ-001")
        r_batch=rc2.text_input("Número de lote",key="rc_batch",placeholder="LOTE-2026-001")
        if st.button("🔍 Buscar pacientes expuestos",key="rc_search"):
            if not r_code.strip() or not r_batch.strip():
                st.error("Ingrese código de instrumental y número de lote."); return
            pd_df=query_df(
                "SELECT patient_id,patient_initials,procedure_type,operating_room,"
                "delivery_date,registered_by,created_at "
                "FROM patient_deliveries WHERE instrument_code=? AND batch_code=? ORDER BY created_at",
                (r_code.strip(),r_batch.strip()))
            al_df=query_df(
                "SELECT alert_type,severity,description,status,created_at FROM alerts "
                "WHERE instrument_code=? AND batch_code=? ORDER BY severity,created_at",
                (r_code.strip(),r_batch.strip()))
            st.markdown("---")
            if not al_df.empty:
                alta_cnt=len(al_df[al_df["severity"]=="Alta"])
                if alta_cnt>0:
                    st.error(f"🔴 **Lote con {alta_cnt} alerta(s) de riesgo ALTO**")
                st.dataframe(al_df.rename(columns={
                    "alert_type":"Tipo de alerta","severity":"Severidad",
                    "description":"Descripción","status":"Estado","created_at":"Fecha"}),
                    use_container_width=True)
            else:
                st.success("✅ No se encontraron alertas para este lote.")
            if pd_df.empty:
                st.info("No hay pacientes vinculados a este lote.")
            else:
                n=len(pd_df)
                st.error(f"🚨 **{n} paciente(s) expuesto(s)** a este lote. "
                         "Activar protocolo institucional de notificación.")
                st.dataframe(pd_df.rename(columns={
                    "patient_id":"ID Paciente","patient_initials":"Iniciales",
                    "procedure_type":"Procedimiento","operating_room":"Quirófano/Sala",
                    "delivery_date":"Fecha entrega","registered_by":"Registrado por",
                    "created_at":"Creado en"}), use_container_width=True)
                # Descarga Excel del recall
                out=io.BytesIO()
                with pd.ExcelWriter(out,engine="xlsxwriter") as w:
                    pd_df.to_excel(w,sheet_name="Pacientes_expuestos",index=False)
                    if not al_df.empty:
                        al_df.to_excel(w,sheet_name="Alertas_lote",index=False)
                out.seek(0)
                st.download_button(
                    "📥 Descargar listado de recall (Excel)",
                    data=out.read(),
                    file_name=f"recall_{r_code.strip()}_{r_batch.strip()}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                audit(st.session_state["user"],"Consulta recall","Recall",
                      f"{r_code.strip()}/{r_batch.strip()} — {n} paciente(s) expuesto(s)")
    with tab2:
        st.subheader("Historial de lotes recibidos por un paciente")
        p_id=st.text_input("ID del paciente / Historia clínica",key="rc_pid",placeholder="HC-2026-00123")
        if st.button("🔍 Buscar historial del paciente",key="rc_pid_search"):
            if not p_id.strip():
                st.error("Ingrese el ID del paciente."); return
            pr_df=query_df(
                "SELECT instrument_code,batch_code,procedure_type,operating_room,"
                "delivery_date,registered_by,created_at "
                "FROM patient_deliveries WHERE patient_id=? ORDER BY created_at",
                (p_id.strip(),))
            st.markdown("---")
            if pr_df.empty:
                st.info("No se encontraron registros de entrega para este paciente.")
            else:
                st.warning(f"El paciente **{p_id.strip()}** tiene {len(pr_df)} registro(s) de entrega de instrumental.")
                st.dataframe(pr_df.rename(columns={
                    "instrument_code":"Código","batch_code":"Lote",
                    "procedure_type":"Procedimiento","operating_room":"Quirófano/Sala",
                    "delivery_date":"Fecha entrega","registered_by":"Registrado por",
                    "created_at":"Creado en"}), use_container_width=True)
                audit(st.session_state["user"],"Consulta paciente","Recall",
                      f"Paciente: {p_id.strip()} — {len(pr_df)} lote(s)")

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
        reason=st.text_area("Justificación de cierre *",placeholder="Ej: Se reprocesó el lote y se verificó conformidad del indicador biológico.")
        if st.button("✅ Marcar como cerrada"):
            if not reason.strip():
                st.error("Debe ingresar una justificación antes de cerrar la alerta.")
            else:
                aid=int(sel.split("|")[0].strip())
                execute("UPDATE alerts SET status='Cerrada',closed_by=?,closed_at=?,closing_reason=? WHERE id=?",
                        (st.session_state["user"],datetime.now().isoformat(),reason.strip(),aid))
                audit(st.session_state["user"],"Cerrar alerta","Alertas",f"ID:{aid} – {reason.strip()[:80]}")
                st.success("Alerta cerrada."); st.rerun()
    # ─ Historial de alertas cerradas con justificación
    _cerr=query_df(
        "SELECT id,instrument_code,batch_code,alert_type,severity,description,closed_by,closed_at,closing_reason "
        "FROM alerts WHERE status='Cerrada' ORDER BY closed_at DESC")
    if not _cerr.empty:
        st.subheader("📜 Historial de alertas cerradas")
        _cerr_show=_cerr.rename(columns={
            "id":"ID","instrument_code":"Código","batch_code":"Lote",
            "alert_type":"Tipo","severity":"Severidad","description":"Descripción",
            "closed_by":"Cerrada por","closed_at":"Fecha cierre",
            "closing_reason":"Justificación"})
        _sin_just=_cerr[_cerr["closing_reason"].isna()|(~_cerr["closing_reason"].astype(str).str.strip().astype(bool))]
        if not _sin_just.empty:
            st.warning(f"🟡 {len(_sin_just)} alerta(s) cerrada(s) sin justificación registrada (registros anteriores a esta mejora).")
        st.dataframe(_cerr_show,use_container_width=True)
        # Descarga exclusiva de cerradas
        _buf=io.BytesIO()
        with pd.ExcelWriter(_buf,engine="xlsxwriter") as _w:
            _wb=_w.book
            _hf=_wb.add_format({"bold":True,"bg_color":"#1F4E79","font_color":"white","border":1})
            _tf=_wb.add_format({"bold":True,"font_size":13})
            _now=datetime.now().strftime("%Y-%m-%d %H:%M")
            _cerr_show.to_excel(_w,sheet_name="Alertas_Cerradas",index=False,startrow=2)
            _s=_w.sheets["Alertas_Cerradas"]
            _s.write(0,0,f"{APP_NAME} – Alertas cerradas – {_now}",_tf)
            for _i,_c in enumerate(_cerr_show.columns):
                _s.write(2,_i,_c,_hf)
                _cw=max(len(str(_c))+4,_cerr_show[_c].astype(str).str.len().max()+2 if not _cerr_show.empty else 10)
                _s.set_column(_i,_i,min(_cw,60))
            _s.autofilter(2,0,2+len(_cerr_show),len(_cerr_show.columns)-1)
        _buf.seek(0)
        st.download_button("📥 Descargar alertas cerradas (Excel)",_buf.read(),
                           file_name=f"alertas_cerradas_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # ─ Generar NC desde alerta abierta (Mejora R) ─────────────────────────────
    st.markdown("---")
    st.subheader("📋 Generar no conformidad desde alerta")
    st.caption("Referencia: ISO 13485:2016 §8.7 — Control de salidas no conformes / Res. 4816/2008 MinSalud Colombia")
    op_nc = query_df("SELECT id,alert_type,severity,instrument_code,batch_code FROM alerts WHERE status='Abierta' ORDER BY created_at DESC")
    if op_nc.empty:
        st.info("No hay alertas abiertas en este momento.")
    else:
        sel_nc = st.selectbox(
            "Seleccionar alerta de origen",
            [f"{r.id} | [{r.severity}] {r.alert_type} – {r.instrument_code}/{r.batch_code}" for _, r in op_nc.iterrows()],
            key="nc_alert_sel")
        if sel_nc:
            _nc_aid = int(sel_nc.split("|")[0].strip())
            _nc_row = op_nc[op_nc["id"] == _nc_aid].iloc[0]
            _nc_existing = query_df(
                "SELECT id FROM nonconformities WHERE alert_id=? AND status='Abierta'", (_nc_aid,))
            if not _nc_existing.empty:
                st.info(f"Ya existe una no conformidad abierta vinculada a esta alerta (NC #{_nc_existing.iloc[0]['id']}).")
            else:
                with st.form("nc_from_alert_form", clear_on_submit=True):
                    nc_type = st.selectbox("Tipo de no conformidad",
                        ["Proceso","Instrumental","Equipo","Personal","Documentación","Infraestructura","Otro"])
                    nc_desc = st.text_area("Descripción de la no conformidad *",
                        value=f"Alerta [{_nc_row['severity']}] '{_nc_row['alert_type']}' en "
                              f"{_nc_row['instrument_code']}/{_nc_row['batch_code']}.",
                        height=90)
                    nc_cause = st.text_area("Causa raíz (análisis preliminar)", height=80,
                        placeholder="Ej: Fallo en validación del ciclo por temperatura insuficiente.")
                    nc_corr = st.text_area("Acción correctiva propuesta", height=80,
                        placeholder="Ej: Rechazar carga, reprocesar y calibrar el equipo.")
                    nc_prev = st.text_area("Acción preventiva propuesta", height=80,
                        placeholder="Ej: Establecer verificación diaria de parámetros del autoclave.")
                    c1nc, c2nc = st.columns(2)
                    nc_resp = c1nc.text_input("Responsable de cierre", placeholder="Nombre del responsable")
                    nc_due  = c2nc.date_input("Fecha límite de cierre", value=date.today() + timedelta(days=15))
                    nc_sub  = st.form_submit_button("💾 Registrar no conformidad")
                if nc_sub:
                    if not nc_desc.strip():
                        st.error("La descripción es obligatoria.")
                    else:
                        execute("""INSERT INTO nonconformities
                            (alert_id,instrument_code,batch_code,nc_type,description,
                             root_cause,corrective_action,preventive_action,
                             responsible,due_date,status,registered_by,created_at)
                            VALUES(?,?,?,?,?,?,?,?,?,?,'Abierta',?,?)""",
                            (_nc_aid, str(_nc_row["instrument_code"]), str(_nc_row["batch_code"]),
                             nc_type, nc_desc.strip(), nc_cause.strip(), nc_corr.strip(),
                             nc_prev.strip(), nc_resp.strip(), nc_due.isoformat(),
                             st.session_state["user"], datetime.now().isoformat()))
                        audit(st.session_state["user"], "NC registrada", "No conformidades",
                              f"Alerta #{_nc_aid} – {nc_type} – {_nc_row['instrument_code']}/{_nc_row['batch_code']}")
                        st.success("✅ No conformidad registrada y vinculada a la alerta.")
                        st.rerun()

# ─── Asistente IA – Plan de mejora ───────────────────────────────────────────
# ─── Prompt base de Trace ────────────────────────────────────────────────────
_TRACE_SYSTEM = """
Eres Trace, asistente de inteligencia artificial especializado en centrales de
reprocesamiento de instrumental quirurgico (CEYE / CRE). Fuiste creado para apoyar
al equipo de ReproTrace Basic 360 de la Universidad Libre Seccional Barranquilla,
Programa de Instrumentacion Quirurgica.

Conocimiento de dominio:
- Las 8 etapas del reprocesamiento: Recepcion, Limpieza y descontaminacion,
  Inspeccion funcional, Empaque, Esterilizacion, Validacion y liberacion de carga,
  Almacenamiento, Distribucion.
- Clasificacion de Spaulding: critico, semicritico, no critico.
- Normas y guias aplicables: ISO 17664, AAMI ST79, ISO 11135, ISO 11138, OPS/OMS
  guias de reprocesamiento 2016, normativa INVIMA Colombia, Resolucion 4816/2008 del
  Ministerio de Salud de Colombia sobre tecnovigilancia.
- Metodos de esterilizacion: vapor saturado a presion (autoclave), oxido de etileno
  (ETO), plasma de peroxido de hidrogeno (VH2O2), formaldehido.
- Indicadores biologicos, quimicos y fisicos de proceso.
- Parametros criticos de los ciclos: temperatura, presion, tiempo de exposicion,
  parametros de secado.
- Causas comunes de no conformidad: carga excesiva, mal empaque, humedad residual,
  fallos de sellado, uso de detergentes incompatibles, omision de etapas.
- Gestion de calidad: PHVA (Planificar-Hacer-Verificar-Actuar), analisis causa raiz,
  5 porques, diagrama de Ishikawa.
- Roles: tecnico en instrumentacion, enfermero jefe, supervisor de central, auditoria.

Ejemplos de analisis estructurado:

Hallazgo: "Se encontro instrumental con manchas de oxido despues del ciclo de
           esterilizacion en autoclave."
Respuesta JSON:
{
  "causa_probable": "Humedad residual post-esterilizacion por fallo en fase de secado
    o carga excesiva que impide circulacion del vapor; posible uso de agua no
    desmineralizada en el autoclave.",
  "accion_correctiva": "Revisar y calibrar ciclo de secado del autoclave. Reducir
    densidad de carga. Verificar calidad del agua de alimentacion (conductividad < 5
    uS/cm segun EN 285). Retirar y limpiar instrumental afectado.",
  "accion_preventiva": "Establecer protocolo de verificacion diaria del secado
    (prueba de humedad en empaque). Capacitar al personal en criterios de carga.
    Registrar parametros de cada ciclo como evidencia.",
  "nivel_riesgo": "Alto"
}

Hallazgo: "Falta un instrumento en la caja de cirugia entregada a quirofano."
Respuesta JSON:
{
  "causa_probable": "Error en conteo de instrumental en etapa de inspeccion funcional
    o empaque; posible extravío durante la distribucion.",
  "accion_correctiva": "Realizar conteo de verificacion en central antes de la
    siguiente entrega. Localizar el instrumento faltante. Notificar al quirofano y
    registrar la no conformidad en el modulo de alertas.",
  "accion_preventiva": "Implementar lista de verificacion de conteo por caja (check
    list con imagen). Capacitar al personal en el doble conteo. Usar etiquetas con
    contenido esperado por caja.",
  "nivel_riesgo": "Critico"
}

Reglas de respuesta:
- Cuando el usuario solicite analisis de un hallazgo, responde SOLO con un objeto
  JSON valido con las claves: causa_probable, accion_correctiva, accion_preventiva,
  nivel_riesgo (valores: Bajo, Medio, Alto, Critico).
- Para preguntas de chat (no hallazgos), responde en texto claro, profesional y en
  espanol, sin JSON. Puedes usar listas con guiones.
- Nunca inventes normativas que no existan. Si no tienes seguridad, indícalo.
- Dirígete al usuario con respeto y en contexto academico colombiano.
"""

def _trace_suggest(finding: str, api_key: str) -> dict:
    """Llama a Trace (GPT) y devuelve sugerencias estructuradas en JSON."""
    import openai, json
    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _TRACE_SYSTEM},
            {"role": "user", "content": f"Analiza el siguiente hallazgo y devuelve el JSON:\n{finding}"},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    raw = resp.choices[0].message.content.strip()
    try:
        clean = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    except Exception:
        return {"raw": raw}

def _trace_chat(messages: list, api_key: str) -> str:
    """Envia el historial de chat a Trace y devuelve la respuesta en texto."""
    import openai
    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": _TRACE_SYSTEM}] + messages,
        temperature=0.5,
        max_tokens=900,
    )
    return resp.choices[0].message.content.strip()


_TRACE_PLAN_SYSTEM = """
Eres Trace, asistente de IA especializado en centrales de reprocesamiento (CEYE/CRE).

Tarea:
- A partir de una lista de hallazgos/no conformidades, genera un PLAN DE MEJORA (PHVA)
  con acciones correctivas y preventivas, e incluye cuando aplique: capacitacion,
  recursos necesarios, indicador/KPI y verificacion.

Reglas de respuesta:
- Responde SOLO con JSON valido (sin texto adicional, sin markdown).
- Devuelve un objeto con la clave "planes" que contiene una lista.
- Cada elemento de "planes" debe incluir estas claves:
  hallazgo, tipo_riesgo, nivel_riesgo, causa_probable, accion_correctiva,
  accion_preventiva, capacitacion, recursos, indicador_kpi, responsable_rol,
  plazo_dias, verificacion.
- "nivel_riesgo" debe ser exactamente uno de: Bajo, Medio, Alto, Crítico.
- "plazo_dias" debe ser un entero (p. ej., 7, 15, 30).
- No inventes normativas. Si no estas seguro, di "No especificado".
""".strip()


def _normalize_risk_level(level: str) -> str:
    if not level:
        return "Medio"
    lvl = str(level).strip()
    mapping = {
        "bajo": "Bajo",
        "medio": "Medio",
        "alto": "Alto",
        "critico": "Crítico",
        "crítico": "Crítico",
        "alta": "Alto",
        "media": "Medio",
        "baja": "Bajo",
    }
    return mapping.get(lvl.lower(), "Medio")


def _read_text_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        try:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            return ""


def _extract_audit_findings(md_text: str) -> list[str]:
    """Extrae hallazgos desde secciones típicas del archivo de auditoría."""
    if not md_text:
        return []

    import re

    targets = {
        "hallazgos críticos corregidos": "Hallazgo",
        "limitaciones que permanecen": "Limitación",
    }

    findings: list[str] = []
    current_prefix: str | None = None

    for raw in md_text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.startswith("## "):
            title = line.removeprefix("## ").strip().lower()
            current_prefix = None
            for key, prefix in targets.items():
                if title.startswith(key):
                    current_prefix = prefix
                    break
            continue

        if current_prefix is None:
            continue

        # Numeradas: "1. ..." o bullets: "- ..."
        item = None
        m_num = re.match(r"^\d+\.\s+(.*)$", line)
        if m_num:
            item = m_num.group(1).strip()
        else:
            m_bul = re.match(r"^-\s+(.*)$", line)
            if m_bul:
                item = m_bul.group(1).strip()

        if item:
            findings.append(f"{current_prefix}: {item}")
    return findings


def _trace_generate_plan(findings: list[str], api_key: str) -> dict:
    """Genera un plan de mejora (lista) a partir de múltiples hallazgos."""
    import openai, json

    content = "\n".join([f"- {f}" for f in findings if str(f).strip()])
    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _TRACE_PLAN_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Genera el plan de mejora a partir de estos hallazgos:\n" + content
                ),
            },
        ],
        temperature=0.25,
        max_tokens=1400,
    )
    raw = resp.choices[0].message.content.strip()
    try:
        clean = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    except Exception:
        return {"raw": raw}


def _format_plan_evidence(item: dict, source: str) -> str:
    cap = item.get("capacitacion", "")
    rec = item.get("recursos", "")
    kpi = item.get("indicador_kpi", "")
    ver = item.get("verificacion", "")
    resp = item.get("responsable_rol", "")
    parts = [
        f"Fuente: {source}",
        f"Capacitación: {cap or 'No especificado'}",
        f"Recursos: {rec or 'No especificado'}",
        f"Indicador/KPI: {kpi or 'No especificado'}",
        f"Verificación: {ver or 'No especificado'}",
        f"Responsable (rol): {resp or 'No especificado'}",
    ]
    return "\n".join(parts)


def _extract_open_alert_findings(severity: str = "Todas", limit: int = 20) -> list[str]:
    """Convierte alertas abiertas en una lista de hallazgos para el plan de mejora."""
    lim = max(1, min(int(limit or 20), 50))
    if severity and severity != "Todas":
        df = query_df(
            """SELECT severity, alert_type, instrument_code, batch_code, description, created_at
               FROM alerts
               WHERE status='Abierta' AND severity=?
               ORDER BY created_at DESC
               LIMIT ?""",
            (severity, lim),
        )
    else:
        df = query_df(
            """SELECT severity, alert_type, instrument_code, batch_code, description, created_at
               FROM alerts
               WHERE status='Abierta'
               ORDER BY created_at DESC
               LIMIT ?""",
            (lim,),
        )
    findings: list[str] = []
    if df.empty:
        return findings
    for _, r in df.iterrows():
        sev = str(r.get("severity", "")).strip()
        at = str(r.get("alert_type", "")).strip()
        code = str(r.get("instrument_code", "")).strip()
        batch = str(r.get("batch_code", "")).strip()
        desc = str(r.get("description", "")).strip()
        findings.append(f"Alerta abierta: [{sev}] {at} – {code} / {batch}: {desc}")
    return findings


def _decode_bytes(data: bytes) -> str:
    if not data:
        return ""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return ""


def _extract_text_from_uploaded(uploaded) -> tuple[str, str]:
    """Devuelve (texto, error). Soporta PDF/DOCX/TXT/MD/CSV."""
    if uploaded is None:
        return "", "Archivo vacío."

    name = getattr(uploaded, "name", "") or "archivo"
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""

    try:
        data = uploaded.getvalue()
    except Exception:
        try:
            data = uploaded.read()
        except Exception:
            data = b""

    if not data:
        return "", "No se pudo leer el archivo."

    if ext in ("txt", "md"):
        return _decode_bytes(data), ""

    if ext == "csv":
        try:
            df = pd.read_csv(io.BytesIO(data))
            # Limitar tamaño para evitar prompts gigantes
            preview = df.head(200)
            return preview.to_csv(index=False), ""
        except Exception as e:
            return "", f"No pude leer el CSV: {e}"

    if ext == "pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            parts = []
            for i, page in enumerate(reader.pages):
                try:
                    txt = page.extract_text() or ""
                except Exception:
                    txt = ""
                if txt.strip():
                    parts.append(txt)
                # corte defensivo
                if sum(len(p) for p in parts) > 200_000:
                    parts.append("\n[...texto truncado por tamaño...]")
                    break
            out = "\n\n".join(parts).strip()
            return out, "" if out else "No se extrajo texto del PDF (puede ser escaneado)."
        except Exception as e:
            return "", f"No pude procesar el PDF: {e}"

    if ext == "docx":
        try:
            from docx import Document

            doc = Document(io.BytesIO(data))
            parts = []
            for p in doc.paragraphs:
                if p.text and p.text.strip():
                    parts.append(p.text.strip())
            for t in getattr(doc, "tables", []) or []:
                for row in t.rows:
                    cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
                    if cells:
                        parts.append(" | ".join(cells))
            out = "\n".join(parts).strip()
            return out, "" if out else "No se extrajo texto del DOCX."
        except Exception as e:
            return "", f"No pude procesar el DOCX: {e}"

    return "", "Tipo de archivo no soportado. Usa PDF, DOCX, TXT, MD o CSV."


def _build_docs_context(docs: list[dict], max_chars_total: int = 12000, max_chars_each: int = 4000) -> str:
    """Construye un contexto compacto con límites de tamaño para enviarlo a Trace."""
    if not docs:
        return ""
    blocks: list[str] = []
    used = 0
    for d in docs:
        name = str(d.get("name", "documento")).strip()
        text = str(d.get("text", ""))
        if not text.strip():
            continue
        trimmed = text.strip()
        if len(trimmed) > max_chars_each:
            trimmed = trimmed[:max_chars_each] + "\n[...contenido truncado...]"
        block = f"### {name}\n{trimmed}"
        if used + len(block) > max_chars_total:
            remain = max_chars_total - used
            if remain < 200:
                break
            blocks.append(block[:remain] + "\n[...contexto truncado...]")
            break
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks).strip()

# ─── Plan de mejora ───────────────────────────────────────────────────────────
def improvement_module():
    st.header("5. Plan de mejora")
    st.info("💡 El sistema genera recomendaciones automáticas ante alertas críticas. También puede registrar hallazgos manualmente.")
    check_and_recommend()

    # ── Asistente Trace ────────────────────────────────────────────────────────
    ai_key = st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, "secrets") else None
    with st.expander("🤖 Trace – Asistente IA de Reprocesamiento", expanded=False):
        if not ai_key:
            st.warning(
                "⚠️ Clave de OpenAI no configurada. "
                "Añade `OPENAI_API_KEY` en los secretos de Streamlit Cloud "
                "(Settings → Secrets) o en `.streamlit/secrets.toml` localmente."
            )
        else:
            st.markdown(
                "> **Trace** es tu asistente especializado en centrales de reprocesamiento. "
                "Puede analizar hallazgos y generar planes de mejora, o responder preguntas "
                "sobre normas (ISO 17664, AAMI ST79, INVIMA), etapas del proceso, "
                "esterilización y gestión de calidad."
            )
            tab_suggest, tab_bulk, tab_docs, tab_chat = st.tabs(["📋 Analizar hallazgo", "📑 Plan desde hallazgos", "📎 Documentos", "💬 Chat con Trace"])

            # ── Tab 1: análisis estructurado ──
            with tab_suggest:
                ai_finding = st.text_area(
                    "Describe el hallazgo de no conformidad",
                    key="ai_finding_input",
                    height=100,
                    placeholder="Ej: Se detectó instrumental con residuos orgánicos tras el ciclo de limpieza en la etapa de inspección funcional.",
                )
                if st.button("✨ Analizar con Trace", key="ai_suggest_btn"):
                    if ai_finding.strip():
                        with st.spinner("Trace está analizando el hallazgo…"):
                            try:
                                result = _trace_suggest(ai_finding.strip(), ai_key)
                                st.session_state["_ai_sugg"] = result
                            except Exception as e:
                                st.error(f"Error al consultar Trace: {e}")
                                st.session_state.pop("_ai_sugg", None)
                    else:
                        st.warning("Ingresa el hallazgo antes de consultar.")

                sugg = st.session_state.get("_ai_sugg")
                if sugg:
                    if "raw" in sugg:
                        st.text_area("Respuesta de Trace", sugg["raw"], height=180, disabled=True)
                    else:
                        nivel = sugg.get("nivel_riesgo", "")
                        color_map = {"Bajo": "#2ecc71", "Medio": "#f39c12", "Alto": "#e67e22", "Critico": "#e74c3c"}
                        badge_color = color_map.get(nivel, "#95a5a6")
                        st.markdown(
                            f"<span style='background:{badge_color};color:#fff;padding:3px 12px;"
                            f"border-radius:12px;font-weight:bold;'>Nivel de riesgo: {nivel}</span>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("")
                        colA, colB = st.columns(2)
                        colA.info(f"**🔍 Causa probable**\n\n{sugg.get('causa_probable', '')}")
                        colB.warning(f"**🔧 Acción correctiva**\n\n{sugg.get('accion_correctiva', '')}")
                        st.success(f"**🛡️ Acción preventiva**\n\n{sugg.get('accion_preventiva', '')}")
                        st.info("Usa estas sugerencias para completar el formulario ➕ Registrar nuevo plan.", icon="👇")

            # ── Tab 2: chat conversacional ──
            with tab_bulk:
                st.markdown(
                    "Genera un plan de mejora a partir de varios hallazgos (por ejemplo, "
                    "los de una auditoría). Puedes previsualizarlo y guardarlo en el módulo."
                )

                src = st.radio(
                    "Fuente de hallazgos",
                    [
                        "📄 Leer AUDITORIA_PROFUNDA.md",
                        "🔔 Usar alertas abiertas",
                        "📄 + 🔔 Auditoría + alertas abiertas",
                        "✍️ Pegar hallazgos",
                    ],
                    horizontal=True,
                )

                findings: list[str] = []
                source_label = ""
                preview_lines: list[str] = []

                if src.startswith("📄 +"):
                    source_label = "AUDITORIA_PROFUNDA.md + Alertas abiertas"

                    md = _read_text_file("AUDITORIA_PROFUNDA.md")
                    extracted = _extract_audit_findings(md)
                    if extracted:
                        max_items = min(30, len(extracted))
                        n_aud = st.slider("Auditoría: cantidad a incluir", 1, max_items, value=min(8, max_items))
                        findings.extend(extracted[:n_aud])
                    else:
                        st.warning("No pude extraer hallazgos desde AUDITORIA_PROFUNDA.md (o el archivo está vacío).")

                    sev = st.selectbox("Alertas: severidad", ["Todas", "Alta", "Media", "Baja"], index=1)
                    n_al = st.slider("Alertas: cantidad a incluir", 1, 30, value=8)
                    alert_findings = _extract_open_alert_findings(severity=sev, limit=n_al)
                    if not alert_findings:
                        st.warning("No hay alertas abiertas para esa severidad.")
                    findings.extend(alert_findings)

                    # Dedupe manteniendo orden
                    seen = set()
                    findings = [x for x in findings if not (x in seen or seen.add(x))]
                    preview_lines = findings[:30]
                    st.caption(f"Hallazgos combinados: {len(findings)}")
                    st.text_area("Vista previa (solo lectura)", "\n".join(preview_lines), height=190, disabled=True)

                elif src.startswith("📄"):
                    source_label = "AUDITORIA_PROFUNDA.md"
                    md = _read_text_file("AUDITORIA_PROFUNDA.md")
                    extracted = _extract_audit_findings(md)
                    if not extracted:
                        st.warning("No pude extraer hallazgos desde AUDITORIA_PROFUNDA.md (o el archivo está vacío).")
                    else:
                        st.caption(f"Hallazgos detectados: {len(extracted)}")
                        max_items = min(30, len(extracted))
                        n = st.slider("Cantidad a incluir", 1, max_items, value=min(10, max_items))
                        findings = extracted[:n]
                        st.text_area("Vista previa (solo lectura)", "\n".join(findings), height=170, disabled=True)

                elif src.startswith("🔔"):
                    source_label = "Alertas abiertas"
                    sev = st.selectbox("Severidad", ["Todas", "Alta", "Media", "Baja"], index=1)
                    n_al = st.slider("Cantidad a incluir", 1, 30, value=10)
                    findings = _extract_open_alert_findings(severity=sev, limit=n_al)
                    if not findings:
                        st.warning("No hay alertas abiertas para esa severidad.")
                    else:
                        st.text_area("Vista previa (solo lectura)", "\n".join(findings), height=190, disabled=True)

                else:
                    source_label = "Hallazgos pegados por el usuario"
                    pasted = st.text_area(
                        "Pega los hallazgos (uno por línea)",
                        height=170,
                        placeholder="Ej:\n- Hallazgo: ...\n- Hallazgo: ...\n- Limitación: ...",
                    )
                    findings = [ln.strip("- ").strip() for ln in pasted.splitlines() if ln.strip()]

                colg1, colg2 = st.columns([1, 1])
                with colg1:
                    if st.button("🧠 Generar plan con Trace", key="ai_bulk_generate"):
                        if not findings:
                            st.warning("No hay hallazgos para analizar.")
                        else:
                            with st.spinner("Trace está generando el plan de mejora…"):
                                try:
                                    result = _trace_generate_plan(findings, ai_key)
                                    st.session_state["_ai_bulk_plan"] = result
                                except Exception as e:
                                    st.error(f"Error al consultar Trace: {e}")
                                    st.session_state.pop("_ai_bulk_plan", None)

                bulk = st.session_state.get("_ai_bulk_plan")
                if bulk:
                    if "raw" in bulk:
                        st.text_area("Respuesta de Trace", bulk["raw"], height=220, disabled=True)
                    else:
                        planes = bulk.get("planes", []) if isinstance(bulk, dict) else []
                        if not isinstance(planes, list) or not planes:
                            st.warning("Trace no devolvió una lista 'planes' válida.")
                        else:
                            # Normalizar para previsualización
                            rows = []
                            for it in planes:
                                if not isinstance(it, dict):
                                    continue
                                rows.append(
                                    {
                                        "Hallazgo": it.get("hallazgo", ""),
                                        "Riesgo": it.get("tipo_riesgo", ""),
                                        "Nivel": _normalize_risk_level(it.get("nivel_riesgo", "")),
                                        "Acción correctiva": it.get("accion_correctiva", ""),
                                        "Capacitación": it.get("capacitacion", ""),
                                        "KPI": it.get("indicador_kpi", ""),
                                        "Plazo (días)": it.get("plazo_dias", ""),
                                    }
                                )
                            st.subheader("Previsualización del plan")
                            st.dataframe(pd.DataFrame(rows), use_container_width=True)

                            if st.button("💾 Guardar planes en el módulo", key="ai_bulk_save"):
                                existing = set(
                                    query_df("SELECT finding FROM improvement_plans")["finding"].tolist()
                                )
                                saved = 0
                                skipped = 0
                                for it in planes:
                                    if not isinstance(it, dict):
                                        continue
                                    finding_txt = str(it.get("hallazgo", "")).strip()
                                    if not finding_txt or finding_txt in existing:
                                        skipped += 1
                                        continue
                                    risk_type = str(it.get("tipo_riesgo", "")).strip() or "Hallazgo"
                                    risk_level = _normalize_risk_level(it.get("nivel_riesgo", ""))
                                    cause = str(it.get("causa_probable", "")).strip()
                                    corr = str(it.get("accion_correctiva", "")).strip()
                                    prev = str(it.get("accion_preventiva", "")).strip()
                                    resp_role = str(it.get("responsable_rol", "")).strip()
                                    try:
                                        plazo = int(it.get("plazo_dias", 15) or 15)
                                    except Exception:
                                        plazo = 15
                                    follow = (date.today() + timedelta(days=max(1, min(plazo, 365)))).isoformat()
                                    evid = _format_plan_evidence(it, source_label)
                                    execute(
                                        """INSERT INTO improvement_plans(
                                            finding,risk_type,risk_level,probable_cause,corrective_action,
                                            preventive_action,responsible,follow_up_date,state,evidence,registered_by,created_at
                                        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                                        (
                                            finding_txt,
                                            risk_type,
                                            risk_level,
                                            cause,
                                            corr,
                                            prev,
                                            resp_role,
                                            follow,
                                            "Pendiente",
                                            evid,
                                            st.session_state["user"],
                                            datetime.now().isoformat(),
                                        ),
                                    )
                                    saved += 1
                                    existing.add(finding_txt)
                                audit(
                                    st.session_state["user"],
                                    "Registro",
                                    "Plan de mejora",
                                    f"Trace bulk: guardados={saved}, omitidos={skipped}",
                                )
                                st.success(f"Planes guardados: {saved}. Omitidos (duplicados/vacíos): {skipped}.")
                                st.rerun()

            with tab_docs:
                st.markdown(
                    "Adjunta documentos (PDF/DOCX/TXT/MD/CSV) para que **Trace** los lea y los analice. "
                    "⚠️ El contenido se enviará a OpenAI al analizar, así que evita datos sensibles."
                )

                uploaded_docs = st.file_uploader(
                    "Adjuntar documentos",
                    type=["pdf", "docx", "txt", "md", "csv"],
                    accept_multiple_files=True,
                    key="trace_docs_uploader",
                )

                colu1, colu2 = st.columns([1, 1])
                with colu1:
                    if st.button("📥 Procesar adjuntos", key="trace_docs_process"):
                        docs_store: list[dict] = []
                        for up in uploaded_docs or []:
                            try:
                                size = len(up.getvalue())
                            except Exception:
                                size = 0
                            if size > 10 * 1024 * 1024:
                                docs_store.append(
                                    {
                                        "name": getattr(up, "name", "archivo"),
                                        "text": "",
                                        "error": "Archivo demasiado grande (>10MB).",
                                    }
                                )
                                continue

                            txt, err = _extract_text_from_uploaded(up)
                            docs_store.append(
                                {
                                    "name": getattr(up, "name", "archivo"),
                                    "text": txt,
                                    "error": err,
                                    "chars": len(txt or ""),
                                }
                            )
                        st.session_state["_trace_docs"] = docs_store

                with colu2:
                    if st.button("🗑️ Limpiar adjuntos", key="trace_docs_clear"):
                        st.session_state.pop("_trace_docs", None)
                        st.rerun()

                docs = st.session_state.get("_trace_docs", [])
                if docs:
                    ok = sum(1 for d in docs if d.get("text"))
                    bad = sum(1 for d in docs if d.get("error") and not d.get("text"))
                    st.caption(f"Adjuntos procesados: {len(docs)} | con texto: {ok} | con error: {bad}")

                    for d in docs:
                        nm = d.get("name", "documento")
                        err = d.get("error", "")
                        ch = d.get("chars", 0)
                        if err and not d.get("text"):
                            st.warning(f"{nm}: {err}")
                        else:
                            st.success(f"{nm}: {ch} caracteres extraídos")

                    with st.expander("Vista previa (solo lectura)", expanded=False):
                        ctx = _build_docs_context(docs, max_chars_total=8000, max_chars_each=2500)
                        st.text_area("", ctx or "(sin texto)", height=220, disabled=True)

                doc_task = st.text_area(
                    "¿Qué necesitas que Trace haga con estos documentos?",
                    key="trace_docs_question",
                    height=120,
                    placeholder="Ej: Extrae hallazgos de no conformidad y sugiere acciones correctivas/preventivas.",
                )

                if st.button("🧠 Analizar documentos con Trace", key="trace_docs_analyze"):
                    docs = st.session_state.get("_trace_docs", [])
                    ctx = _build_docs_context(docs)
                    if not ctx:
                        st.warning("Primero adjunta y procesa documentos con texto extraíble.")
                    elif not doc_task.strip():
                        st.warning("Escribe una instrucción/pregunta para analizar.")
                    else:
                        with st.spinner("Trace está analizando los documentos…"):
                            try:
                                prompt = (
                                    "Analiza el contenido de los documentos adjuntos y responde a la solicitud. "
                                    "Si el documento contiene pasos/etapas, identifica desviaciones y recomendaciones.\n\n"
                                    "DOCUMENTOS (solo lectura):\n" + ctx + "\n\n"
                                    "SOLICITUD:\n" + doc_task.strip()
                                )
                                reply = _trace_chat([{"role": "user", "content": prompt}], ai_key)
                                st.session_state["_trace_docs_reply"] = reply
                            except Exception as e:
                                st.session_state["_trace_docs_reply"] = f"Error al consultar Trace: {e}"

                if st.session_state.get("_trace_docs_reply"):
                    st.subheader("Respuesta de Trace")
                    st.write(st.session_state["_trace_docs_reply"])

            with tab_chat:
                if "_trace_history" not in st.session_state:
                    st.session_state["_trace_history"] = []

                for msg in st.session_state["_trace_history"]:
                    role_label = "🧑 Tú" if msg["role"] == "user" else "🤖 Trace"
                    with st.chat_message(msg["role"]):
                        st.write(f"{msg['content']}")

                user_input = st.chat_input(
                    "Pregunta a Trace sobre reprocesamiento, normas o mejora continua…",
                    key="trace_chat_input",
                )
                if user_input:
                    st.session_state["_trace_history"].append({"role": "user", "content": user_input})
                    with st.chat_message("user"):
                        st.write(user_input)
                    with st.chat_message("assistant"):
                        with st.spinner("Trace está pensando…"):
                            try:
                                reply = _trace_chat(st.session_state["_trace_history"], ai_key)
                            except Exception as e:
                                reply = f"Error al consultar Trace: {e}"
                        st.write(reply)
                    st.session_state["_trace_history"].append({"role": "assistant", "content": reply})

                if st.session_state.get("_trace_history"):
                    if st.button("🗑️ Limpiar conversación", key="trace_clear"):
                        st.session_state["_trace_history"] = []
                        st.rerun()
    # ─────────────────────────────────────────────────────────────────────────
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
    # ─ Fila 1: KPIs básicos
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Registros",len(rec))
    c2.metric("Cumplimiento",f"{(rec['complies']=='Sí').mean()*100:.1f}%" if not rec.empty else "N/A")
    c3.metric("Tiempo promedio",f"{rec['duration_minutes'].mean():.1f} min" if not rec.empty else "N/A")
    c4.metric("Alertas abiertas",len(alerts[alerts["status"]=="Abierta"]) if not alerts.empty else 0)
    # ─ Fila 2: KPI tasa de reprocesamiento fallido
    _tasa,_fall,_tot=_calc_failure_rate(rec)
    st.markdown("---")
    st.subheader("🚫 Indicador de calidad: Tasa de reprocesamiento fallido")
    st.caption("Referencia: AAMI ST79:2017 §11 / OPS-OMS Guía reprocesamiento 2016 / Circular 01/2016 Supersalud Colombia")
    r1,r2,r3=st.columns(3)
    r1.metric("Tasa de fallo (%)",
              f"{_tasa}%" if _tasa is not None else "N/A",
              help="Lotes con al menos un 'Rechazado' en Esterilización o Validación / liberación de carga.")
    r2.metric("Lotes fallidos", _fall if _tasa is not None else "N/A")
    r3.metric("Lotes evaluados", _tot if _tasa is not None else "N/A")
    if _tasa is not None and _tasa>0:
        # Tabla de lotes fallidos
        _est=rec[rec["stage"].isin(["Esterilización","Validación / liberación de carga"])]
        if not _est.empty:
            _fail_df=(_est[_est["result"]=="Rechazado"]
                      [["instrument_code","batch_code","stage","result","responsible","created_at","observations"]]
                      .drop_duplicates(subset=["instrument_code","batch_code","stage"])
                      .sort_values("created_at",ascending=False))
            if not _fail_df.empty:
                st.dataframe(_fail_df.rename(columns={
                    "instrument_code":"Código","batch_code":"Lote","stage":"Etapa",
                    "result":"Resultado","responsible":"Responsable",
                    "created_at":"Fecha","observations":"Observaciones"}),
                    use_container_width=True)
    elif _tasa==0.0:
        st.success("🟢 Sin lotes fallidos en Esterilización/Validación. Índice de calidad óptimo.")
    # ─── Métricas por personal (Mejora P) ────────────────────────────────────
    st.markdown("---")
    st.subheader("👤 Métricas de desempeño por operador")
    st.caption("Referencia: ISO 13485:2016 §6.2 — Competencia del personal / OPS-OMS Guía CEyE 2016. Meta de cumplimiento: ≥ 95 %")
    df_op = _get_operator_stats(rec)
    if df_op.empty:
        st.info("Sin registros de proceso disponibles para calcular métricas por operador.")
    else:
        # ── Semáforo de operadores críticos ──────────────────────────────────
        criticos = df_op[df_op["% Cumplimiento"] < 90]
        advertencia = df_op[(df_op["% Cumplimiento"] >= 90) & (df_op["% Cumplimiento"] < 95)]
        if not criticos.empty:
            ops_cr = ", ".join(criticos["Operador"].tolist())
            st.error(f"🔴 Operadores con cumplimiento crítico (< 90 %): **{ops_cr}**")
        if not advertencia.empty:
            ops_adv = ", ".join(advertencia["Operador"].tolist())
            st.warning(f"🟡 Operadores por debajo de la meta (90–94 %): **{ops_adv}**")
        if criticos.empty and advertencia.empty:
            st.success("🟢 Todos los operadores cumplen la meta de ≥ 95 %.")
        # ── Tabla de métricas ────────────────────────────────────────────────
        st.dataframe(
            df_op.rename(columns={
                "Operador": "Operador / Responsable",
                "T. prom. (min)": "Tiempo prom. (min)",
            }),
            use_container_width=True,
            hide_index=True,
        )
        # ── Gráfica ──────────────────────────────────────────────────────────
        st.subheader("Gráfica de cumplimiento por operador")
        fig_op = _chart_operator_stats(df_op)
        st.pyplot(fig_op)
        # ── Exportar ─────────────────────────────────────────────────────────
        import io as _io
        _buf_op = _io.BytesIO()
        with pd.ExcelWriter(_buf_op, engine="openpyxl") as _wr:
            df_op.to_excel(_wr, index=False, sheet_name="Métricas por operador")
        st.download_button(
            "📥 Exportar métricas por operador (Excel)",
            data=_buf_op.getvalue(),
            file_name=f"metricas_operadores_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        _get_plt().close(fig_op)
    st.markdown("---")
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

    # ── Resultados almacenados (siempre persistentes) ─────────────────────────
    df = query_df("SELECT * FROM staff_survey ORDER BY created_at DESC")
    if not df.empty:
        st.subheader(f"📋 Resultados almacenados ({len(df)} respuestas)")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Gráfica de promedios por pregunta")
        fig = chart_survey(df)
        st.pyplot(fig)

        # ── Exportaciones ─────────────────────────────────────────────────────
        st.subheader("📥 Exportar resultados")
        col_xls, col_png = st.columns(2)
        with col_xls:
            excel_bytes = _survey_excel(df)
            st.download_button(
                label="📊 Descargar Excel",
                data=excel_bytes,
                file_name=f"encuesta_percepcion_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_png:
            img_bytes = fig_bytes(fig)
            st.download_button(
                label="🖼️ Descargar gráfica (PNG)",
                data=img_bytes,
                file_name=f"grafica_encuesta_{date.today()}.png",
                mime="image/png",
                use_container_width=True,
            )
        _get_plt().close(fig)
    else:
        st.info("Aún no hay respuestas registradas.")

    # ── Borrado exclusivo para administrador ──────────────────────────────────
    if st.session_state.get("role") == "Administrador":
        st.divider()
        with st.expander("🗑️ Zona de administrador – Eliminar encuestas"):
            st.warning("⚠️ Esta acción es irreversible y eliminará TODAS las respuestas.")
            confirm_del = st.text_input(
                "Escriba ELIMINAR para confirmar el borrado de todas las encuestas",
                key="surv_del_confirm",
            )
            if confirm_del == "ELIMINAR":
                if st.button("🗑️ Borrar todas las encuestas", type="primary", use_container_width=True):
                    execute("DELETE FROM staff_survey")
                    audit(st.session_state["user"], "Borrar encuestas", "Encuesta",
                          "Todas las encuestas eliminadas por administrador")
                    st.success("Encuestas eliminadas correctamente.")
                    st.rerun()

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
                for t in ["process_records","alerts","improvement_plans","audit_log"]:
                    execute(f"DELETE FROM {t}")
                # Las encuestas de percepción NO se eliminan con el reset de demo;
                # solo el administrador puede borrarlas desde la sección 7.
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

# ─── Calibración de equipos (Mejora Q) ────────────────────────────────────────
def calibration_module():
    st.header("🔩 Calibración y validación de equipos")
    st.caption(
        "Referencia: ISO 17665-1:2006 §10 / ISO 15883-1:2009 §6.3 / "
        "AAMI ST79:2017 §12.4 / Resolución 4816/2008 MinSalud Colombia"
    )
    user = st.session_state["user"]
    tab_reg, tab_lista = st.tabs(["➕ Registrar calibración", "📋 Historial de equipos"])

    # ── Tab 1: Registro ───────────────────────────────────────────────────────
    with tab_reg:
        st.subheader("Registrar certificado de calibración")
        with st.form("cal_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            eq_id   = c1.text_input("ID del equipo *", placeholder="EST-01",
                                    help="Debe coincidir con el 'Equipo esterilizador' en el Registro del proceso.")
            eq_name = c2.text_input("Nombre del equipo *", placeholder="Autoclave de vapor 134°C")
            c3, c4 = st.columns(2)
            eq_type = c3.selectbox("Tipo de equipo",
                                   ["Autoclave / esterilizador de vapor",
                                    "Esterilizador de óxido de etileno",
                                    "Esterilizador de peróxido de hidrógeno",
                                    "Termodesinfectadora (ISO 15883)",
                                    "Lavadora-descontaminadora",
                                    "Otro"])
            cal_result = c4.selectbox("Resultado de calibración", ["Conforme", "No conforme"])
            c5, c6 = st.columns(2)
            last_date = c5.date_input("Fecha de última calibración", value=date.today())
            next_date = c6.date_input("Próxima calibración (vencimiento) *",
                                      value=date.today() + timedelta(days=365),
                                      min_value=date.today())
            c7, c8 = st.columns(2)
            entity = c7.text_input("Entidad calibradora", placeholder="Metrocal S.A.S.")
            cert_no = c8.text_input("Nº certificado", placeholder="CAL-2026-0001")
            obs = st.text_area("Observaciones")
            submitted = st.form_submit_button("💾 Guardar calibración")
        if submitted:
            if not eq_id.strip() or not eq_name.strip():
                st.error("El ID y el nombre del equipo son obligatorios.")
            elif next_date <= last_date:
                st.error("La fecha de próxima calibración debe ser posterior a la última calibración.")
            else:
                execute("""INSERT INTO equipment_calibration
                    (equipment_id,equipment_name,equipment_type,last_calibration_date,
                     next_calibration_date,calibration_entity,certificate_number,
                     result,observations,registered_by,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (eq_id.strip(), eq_name.strip(), eq_type,
                     last_date.isoformat(), next_date.isoformat(),
                     entity.strip(), cert_no.strip(), cal_result, obs.strip(),
                     user, datetime.now().isoformat()))
                audit(user, "Calibración registrada", "Calibración",
                      f"Equipo {eq_id.strip()} — {eq_name.strip()} — vence {next_date.isoformat()}")
                st.success(f"✅ Calibración registrada para '{eq_name.strip()}'. Vence: {next_date.isoformat()}")
                st.rerun()

    # ── Tab 2: Historial y semáforo ───────────────────────────────────────────
    with tab_lista:
        st.subheader("Estado de calibración por equipo")
        df_cal = query_df(
            "SELECT equipment_id,equipment_name,equipment_type,last_calibration_date,"
            "next_calibration_date,calibration_entity,certificate_number,result,observations,registered_by,created_at "
            "FROM equipment_calibration ORDER BY next_calibration_date ASC")
        if df_cal.empty:
            st.info("No hay registros de calibración. Usa la pestaña '➕ Registrar calibración' para agregar el primer equipo.")
        else:
            today = date.today()
            def _estado(nxt_raw):
                try:
                    nxt = date.fromisoformat(str(nxt_raw))
                    days = (nxt - today).days
                    if days < 0:       return f"🔴 Vencida ({abs(days)} días)"
                    elif days <= 30:   return f"🟡 Vence en {days} días"
                    else:              return f"🟢 Vigente ({days} días)"
                except (ValueError, TypeError):
                    return "❓ Fecha inválida"

            df_show = df_cal.copy()
            df_show["Estado calibración"] = df_cal["next_calibration_date"].apply(_estado)
            # Disparar alertas para equipos vencidos o próximos durante visualización
            for _, row in df_cal.iterrows():
                _check_equipment_calibration(str(row["equipment_id"]))
            st.dataframe(
                df_show.rename(columns={
                    "equipment_id":          "ID Equipo",
                    "equipment_name":        "Nombre",
                    "equipment_type":        "Tipo",
                    "last_calibration_date": "Última calibración",
                    "next_calibration_date": "Próxima calibración",
                    "calibration_entity":    "Entidad calibradora",
                    "certificate_number":    "N° cert.",
                    "result":                "Resultado",
                    "observations":          "Observaciones",
                    "registered_by":         "Registrado por",
                    "created_at":            "Fecha registro",
                }),
                use_container_width=True,
                hide_index=True,
                column_order=["ID Equipo","Nombre","Tipo","Última calibración",
                              "Próxima calibración","Estado calibración",
                              "Entidad calibradora","N° cert.","Resultado","Observaciones"],
            )
            vencidos = df_show[df_show["Estado calibración"].str.startswith("🔴")]
            proximos = df_show[df_show["Estado calibración"].str.startswith("🟡")]
            if not vencidos.empty:
                st.error(f"🔴 {len(vencidos)} equipo(s) con calibración VENCIDA: "
                         + ", ".join(vencidos["equipment_id"].tolist()))
            if not proximos.empty:
                st.warning(f"🟡 {len(proximos)} equipo(s) próximos a vencer: "
                           + ", ".join(proximos["equipment_id"].tolist()))
            if vencidos.empty and proximos.empty:
                st.success("🟢 Todos los equipos tienen calibración vigente con más de 30 días restantes.")


# ─── No conformidades (Mejora R) ──────────────────────────────────────────────
def nonconformities_module():
    st.header("📋 No conformidades")
    st.caption(
        "Referencia: ISO 13485:2016 §8.7 — Control de salidas no conformes / "
        "ISO 9001:2015 §10.2 / Resolución 4816/2008 MinSalud Colombia"
    )
    user = st.session_state["user"]

    tab_list, tab_close, tab_kpi = st.tabs(["📂 Listado", "✅ Cerrar NC", "📊 Indicadores"])

    # ── Tab 1: Listado ────────────────────────────────────────────────────────
    with tab_list:
        df_nc = query_df(
            "SELECT nc.id, nc.alert_id, nc.instrument_code, nc.batch_code, nc.nc_type, "
            "nc.description, nc.root_cause, nc.corrective_action, nc.preventive_action, "
            "nc.responsible, nc.due_date, nc.status, nc.closed_by, nc.closed_at, "
            "nc.closure_evidence, nc.registered_by, nc.created_at, "
            "al.alert_type, al.severity "
            "FROM nonconformities nc "
            "LEFT JOIN alerts al ON nc.alert_id = al.id "
            "ORDER BY nc.created_at DESC")
        if df_nc.empty:
            st.info("No hay no conformidades registradas. Puedes crearlas desde el módulo de Alertas.")
        else:
            # Semáforo global
            abiertas  = df_nc[df_nc["status"] == "Abierta"]
            vencidas  = abiertas[abiertas["due_date"].apply(
                lambda d: bool(d) and date.fromisoformat(str(d)) < date.today()
                if d and str(d).strip() else False)]
            if not vencidas.empty:
                st.error(f"🔴 {len(vencidas)} no conformidad(es) VENCIDA(S) sin cerrar.")
            if not abiertas.empty:
                st.warning(f"🟡 {len(abiertas)} no conformidad(es) abiertas.")
            else:
                st.success("🟢 Todas las no conformidades están cerradas.")

            # Filtros
            f1, f2 = st.columns(2)
            fst = f1.selectbox("Estado", ["Todas", "Abierta", "Cerrada"], key="nc_fst")
            ftyp = f2.selectbox("Tipo", ["Todos"] + sorted(df_nc["nc_type"].dropna().unique().tolist()), key="nc_ftyp")
            view = df_nc.copy()
            if fst != "Todas":  view = view[view["status"] == fst]
            if ftyp != "Todos": view = view[view["nc_type"] == ftyp]

            st.dataframe(
                view.rename(columns={
                    "id": "NC #", "alert_id": "Alerta origen", "instrument_code": "Código",
                    "batch_code": "Lote", "nc_type": "Tipo", "description": "Descripción",
                    "root_cause": "Causa raíz", "corrective_action": "Acción correctiva",
                    "preventive_action": "Acción preventiva", "responsible": "Responsable",
                    "due_date": "Fecha límite", "status": "Estado",
                    "closed_by": "Cerrada por", "closed_at": "Fecha cierre",
                    "closure_evidence": "Evidencia cierre",
                    "alert_type": "Tipo alerta", "severity": "Severidad alerta",
                }).drop(columns=["registered_by", "created_at"], errors="ignore"),
                use_container_width=True,
                hide_index=True,
            )
            # Exportar
            _buf_nc = __import__("io").BytesIO()
            with pd.ExcelWriter(_buf_nc, engine="openpyxl") as _wr:
                view.to_excel(_wr, index=False, sheet_name="No conformidades")
            st.download_button(
                "📥 Exportar no conformidades (Excel)",
                data=_buf_nc.getvalue(),
                file_name=f"no_conformidades_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ── Tab 2: Cerrar NC ──────────────────────────────────────────────────────
    with tab_close:
        st.subheader("Cerrar no conformidad")
        open_nc = query_df(
            "SELECT id, nc_type, description, instrument_code, batch_code, due_date "
            "FROM nonconformities WHERE status='Abierta' ORDER BY due_date ASC")
        if open_nc.empty:
            st.success("🟢 No hay no conformidades abiertas.")
        else:
            sel_c = st.selectbox(
                "Seleccionar NC a cerrar",
                [f"NC #{r.id} | {r.nc_type} | {r.instrument_code}/{r.batch_code} | vence {r.due_date}"
                 for _, r in open_nc.iterrows()],
                key="nc_close_sel")
            if sel_c:
                _close_id = int(sel_c.split("|")[0].replace("NC #", "").strip())
                with st.form("nc_close_form", clear_on_submit=True):
                    evidence = st.text_area(
                        "Evidencia de cierre *",
                        height=100,
                        placeholder="Ej: Se reprocesó el lote, se verificó conformidad del IB y se capacitó al personal.")
                    submitted_c = st.form_submit_button("✅ Cerrar NC")
                if submitted_c:
                    if not evidence.strip():
                        st.error("La evidencia de cierre es obligatoria (ISO 13485:2016 §8.7).")
                    else:
                        execute(
                            "UPDATE nonconformities SET status='Cerrada',closed_by=?,closed_at=?,closure_evidence=? WHERE id=?",
                            (user, datetime.now().isoformat(), evidence.strip(), _close_id))
                        audit(user, "NC cerrada", "No conformidades",
                              f"NC #{_close_id} cerrada con evidencia: {evidence.strip()[:80]}")
                        st.success(f"NC #{_close_id} cerrada correctamente.")
                        st.rerun()

    # ── Tab 3: Indicadores ────────────────────────────────────────────────────
    with tab_kpi:
        st.subheader("Indicadores de no conformidades")
        st.caption("Referencia: ISO 13485:2016 §8.7 / AAMI ST79:2017 §11 / OPS-OMS Guía CEyE 2016")
        df_all = query_df("SELECT nc_type, status, created_at, due_date FROM nonconformities")
        if df_all.empty:
            st.info("Aún no hay no conformidades registradas.")
        else:
            total  = len(df_all)
            n_open = int((df_all["status"] == "Abierta").sum())
            n_clos = total - n_open
            n_venc = int(df_all[df_all["status"] == "Abierta"]["due_date"].apply(
                lambda d: bool(d) and date.fromisoformat(str(d)) < date.today()
                if d and str(d).strip() else False).sum())
            pct_cl = round(n_clos / total * 100, 1) if total else 0.0
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total NC", total)
            k2.metric("Abiertas", n_open)
            k3.metric("Cerradas", n_clos, f"{pct_cl}%")
            k4.metric("Vencidas", n_venc, delta_color="inverse")

            # Gráfica por tipo
            plt = _get_plt()
            fig_r, ax_r = plt.subplots(figsize=(6, 3))
            counts = df_all.groupby("nc_type").size().sort_values(ascending=True)
            ax_r.barh(counts.index, counts.values, color="#1F4E79", height=0.5)
            ax_r.set_xlabel("Cantidad")
            ax_r.set_title("No conformidades por tipo", fontsize=9)
            fig_r.tight_layout()
            st.pyplot(fig_r)
            plt.close(fig_r)


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
    st.set_page_config(page_title=APP_NAME, page_icon="🏥", layout="wide",
                       initial_sidebar_state="collapsed")
    init_db(); _migrate_db()
    if not st.session_state.get("seeded"):
        seed_demo_data(); st.session_state["seeded"] = True
    if "login" not in st.session_state: st.session_state["login"]=False
    if not st.session_state["login"]:
        # En el login NO se aplica el TECH_CSS (tiene su propio estilo)
        login_screen()
        return
    # Panel interno: aplicar el CSS tecnológico
    st.markdown(TECH_CSS, unsafe_allow_html=True)
    header()
    MENU=[
        "🏠 Panel principal","🔧 Registro de instrumental","📋 Registro del proceso",
        "🔍 Consulta de trazabilidad","🚨 Retiro de lote (Recall)","🔔 Alertas y novedades","📌 Plan de mejora",
        "📊 Reportes e indicadores","🔩 Calibración de equipos","📋 No conformidades","📝 Encuesta de percepción",
        "🔒 Auditoría de cambios","⚙️ Configuración y respaldo","✅ Plan de pruebas","⚠️ Limitaciones del prototipo",
    ]
    menu=st.sidebar.radio("Menú",MENU)
    dispatch={
        "🏠 Panel principal":dashboard,
        "🔧 Registro de instrumental":instruments_module,
        "📋 Registro del proceso":process_module,
        "🔍 Consulta de trazabilidad":traceability_module,
        "🚨 Retiro de lote (Recall)":recall_module,
        "🔔 Alertas y novedades":alerts_module,
        "📌 Plan de mejora":improvement_module,
        "📊 Reportes e indicadores":reports_module,
        "🔩 Calibración de equipos":calibration_module,
        "📋 No conformidades":nonconformities_module,
        "📝 Encuesta de percepción":survey_module,
        "🔒 Auditoría de cambios":audit_module,
        "⚙️ Configuración y respaldo":config_module,
        "✅ Plan de pruebas":tests_module,
        "⚠️ Limitaciones del prototipo":limitations_module,
    }
    dispatch.get(menu,dashboard)()

if __name__=="__main__":
    main()
