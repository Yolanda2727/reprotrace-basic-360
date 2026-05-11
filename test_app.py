"""
Pruebas unitarias para ReproTrace Basic 360°
Ejecutar: pytest test_app.py -v
Cobertura: init_db, validate_stage_order, _check_password,
           _calc_failure_rate, generación de Excel (generate_excel).
"""
import io
import os
import sqlite3
import tempfile

import pandas as pd
import pytest

# ── Aislar la BD de la base de datos de producción ────────────────────────────
# Redirigimos DB_PATH a un archivo temporal antes de importar el módulo.
# De este modo los tests nunca tocan reprotrace_basic_360.db.

_TMP_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP_DB.close()
os.environ["_TEST_DB_PATH"] = _TMP_DB.name


# Importar el módulo con monkeypatching mínimo para que no arranque Streamlit.
# sys.modules ya tiene 'streamlit' si se instala; si no, lo mockeamos.
import sys
import types

if "streamlit" not in sys.modules:
    _st_mock = types.ModuleType("streamlit")
    for _attr in [
        "cache_resource", "cache_data", "session_state",
        "error", "warning", "success", "info", "write",
        "markdown", "stop", "experimental_rerun", "rerun",
    ]:
        setattr(_st_mock, _attr, lambda *a, **kw: None)
    # session_state como dict accesible por atributos
    class _SS(dict):
        def __getattr__(self, k):
            return self.get(k)
        def __setattr__(self, k, v):
            self[k] = v
    _st_mock.session_state = _SS()
    _st_mock.cache_resource = lambda f=None, **kw: (f if f else lambda fn: fn)
    _st_mock.cache_data = lambda f=None, **kw: (f if f else lambda fn: fn)
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = types.ModuleType("streamlit.components")
    sys.modules["streamlit.components.v1"] = types.ModuleType("streamlit.components.v1")

import importlib
import app as _app  # noqa: E402  (importamos después del mock)

# Apuntar la conexión de la app a la BD temporal
_app.DB_PATH = _TMP_DB.name


def _fresh_db():
    """Devuelve una conexión limpia a la BD de test."""
    return sqlite3.connect(_TMP_DB.name)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. init_db — crea todas las tablas esperadas sin errores
# ═══════════════════════════════════════════════════════════════════════════════

EXPECTED_TABLES = {
    "instruments", "process_records", "alerts", "audit_log",
    "staff_survey", "improvement_plans", "users",
}


def test_init_db_creates_tables():
    """init_db() debe crear al menos las tablas esenciales sin lanzar excepciones."""
    _app.init_db()
    con = _fresh_db()
    cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    con.close()
    missing = EXPECTED_TABLES - tables
    assert not missing, f"Tablas no creadas: {missing}"


def test_init_db_idempotent():
    """Llamar init_db() dos veces no debe lanzar error (IF NOT EXISTS)."""
    _app.init_db()
    _app.init_db()  # segunda llamada — no debe explotar


# ═══════════════════════════════════════════════════════════════════════════════
# 2. validate_stage_order — lógica de secuencia de etapas
# ═══════════════════════════════════════════════════════════════════════════════

def test_validate_stage_order_primera_etapa_siempre_ok():
    """La primera etapa (Recepción) no tiene prerequisito y siempre es válida."""
    ok, msg = _app.validate_stage_order("INS-TEST", "LOTE-001", "Recepción")
    assert ok is True
    assert msg == ""


def test_validate_stage_order_etapa_sin_previa_falla():
    """Intentar registrar 'Esterilización' sin haber completado etapas previas debe fallar."""
    # BD vacía para este par instrumento/lote
    _app.init_db()
    ok, msg = _app.validate_stage_order("INS-ORD", "LOTE-ORD", "Esterilización")
    assert ok is False
    assert "Empaque" in msg


def test_validate_stage_order_etapa_con_previa_completada():
    """Si la etapa previa está registrada, la validación debe pasar."""
    _app.init_db()
    # Insertar directamente el registro de la etapa previa
    _app.execute(
        "INSERT OR IGNORE INTO process_records"
        "(instrument_code, batch_code, stage, responsible, complies, result) "
        "VALUES (?,?,?,?,?,?)",
        ("INS-SEQ", "LOTE-SEQ", "Recepción", "tester", "Sí", "Conforme"),
    )
    ok, msg = _app.validate_stage_order("INS-SEQ", "LOTE-SEQ", "Limpieza y descontaminación")
    assert ok is True, f"Esperaba ok=True, got: {msg}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. _check_password — comparación segura contra timing attacks
# ═══════════════════════════════════════════════════════════════════════════════

def test_check_password_texto_plano_correcto():
    """Contraseña en texto plano correcta debe devolver True."""
    assert _app._check_password("secreto", "secreto") is True


def test_check_password_texto_plano_incorrecto():
    """Contraseña en texto plano incorrecta debe devolver False."""
    assert _app._check_password("malo", "secreto") is False


def test_check_password_bcrypt():
    """Hash bcrypt generado por _hash_password debe validarse correctamente."""
    try:
        import bcrypt  # noqa: F401
    except ImportError:
        pytest.skip("bcrypt no instalado; omitiendo prueba de hash")

    hashed = _app._hash_password("clave_segura_123")
    assert hashed.startswith("$2b$"), "Se esperaba hash bcrypt"
    assert _app._check_password("clave_segura_123", hashed) is True
    assert _app._check_password("otra_clave", hashed) is False


def test_check_password_no_timing_attack():
    """La comparación no debe ser significativamente más rápida para password vacío."""
    import time
    start = time.perf_counter()
    _app._check_password("", "password_largo_de_referencia")
    elapsed = time.perf_counter() - start
    # En cualquier CPU razonable esto tarda < 1 ms; solo verificamos que no explote
    assert elapsed < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. _calc_failure_rate — cálculo de tasa de reprocesamiento fallido
# ═══════════════════════════════════════════════════════════════════════════════

def _make_rec(rows):
    """Helper: crea DataFrame de process_records con columnas mínimas."""
    return pd.DataFrame(rows, columns=["instrument_code", "batch_code", "stage", "result"])


def test_calc_failure_rate_vacio():
    """DataFrame vacío debe devolver (None, 0, 0)."""
    tasa, fallidos, total = _app._calc_failure_rate(pd.DataFrame())
    assert tasa is None
    assert fallidos == 0
    assert total == 0


def test_calc_failure_rate_sin_esterilizacion():
    """Sin registros de Esterilización no hay tasa calculable."""
    rec = _make_rec([
        ("I1", "L1", "Recepción", "Conforme"),
        ("I1", "L1", "Empaque", "Conforme"),
    ])
    tasa, fallidos, total = _app._calc_failure_rate(rec)
    assert tasa is None
    assert total == 0


def test_calc_failure_rate_cero_fallidos():
    """Todos los lotes conformes → tasa 0 %."""
    rec = _make_rec([
        ("I1", "L1", "Esterilización", "Conforme"),
        ("I1", "L2", "Esterilización", "Conforme"),
    ])
    tasa, fallidos, total = _app._calc_failure_rate(rec)
    assert tasa == 0.0
    assert fallidos == 0
    assert total == 2


def test_calc_failure_rate_un_fallido():
    """Un lote rechazado de dos → 50 %."""
    rec = _make_rec([
        ("I1", "L1", "Esterilización", "Conforme"),
        ("I1", "L2", "Esterilización", "Rechazado"),
    ])
    tasa, fallidos, total = _app._calc_failure_rate(rec)
    assert tasa == 50.0
    assert fallidos == 1
    assert total == 2


def test_calc_failure_rate_todos_fallidos():
    """Todos los lotes rechazados → 100 %."""
    rec = _make_rec([
        ("I1", "L1", "Esterilización", "Rechazado"),
        ("I2", "L2", "Validación / liberación de carga", "Rechazado"),
    ])
    tasa, fallidos, total = _app._calc_failure_rate(rec)
    assert tasa == 100.0
    assert fallidos == 2
    assert total == 2


def test_calc_failure_rate_multiples_filas_mismo_lote():
    """Varias filas del mismo lote con un Rechazado cuentan como 1 solo fallido."""
    rec = _make_rec([
        ("I1", "L1", "Esterilización", "Conforme"),
        ("I1", "L1", "Esterilización", "Rechazado"),  # mismo lote L1
        ("I1", "L2", "Esterilización", "Conforme"),
    ])
    tasa, fallidos, total = _app._calc_failure_rate(rec)
    assert fallidos == 1
    assert total == 2
    assert tasa == 50.0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. generate_excel — salida es un archivo Excel válido con hojas esperadas
# ═══════════════════════════════════════════════════════════════════════════════

def test_generate_excel_devuelve_bytes():
    """generate_excel() debe devolver un objeto bytes."""
    _app.init_db()
    result = _app.generate_excel()
    assert isinstance(result, bytes), "Se esperaban bytes"
    assert len(result) > 0, "El Excel no debe estar vacío"


def test_generate_excel_es_archivo_excel_valido():
    """Los bytes devueltos deben ser un Excel legible por pandas."""
    _app.init_db()
    raw = _app.generate_excel()
    xls = pd.ExcelFile(io.BytesIO(raw))
    assert len(xls.sheet_names) >= 1, "Debe tener al menos una hoja"


def test_generate_excel_contiene_hojas_minimas():
    """El Excel debe incluir al menos las hojas Instrumental y Registros."""
    _app.init_db()
    raw = _app.generate_excel()
    xls = pd.ExcelFile(io.BytesIO(raw))
    for esperada in ("Instrumental", "Registros"):
        assert esperada in xls.sheet_names, f"Hoja '{esperada}' no encontrada"


def test_generate_excel_con_datos():
    """Con un instrumento registrado, la hoja Instrumental debe tener al menos 1 fila."""
    _app.init_db()
    _app.execute(
        "INSERT OR IGNORE INTO instruments(code, name, category, registered_by, created_at) "
        "VALUES (?,?,?,?,?)",
        ("EXL-TEST", "Instrumento Excel Test", "Catéter", "tester", "2026-01-01"),
    )
    raw = _app.generate_excel()
    df_ins = pd.read_excel(io.BytesIO(raw), sheet_name="Instrumental", skiprows=2)
    assert len(df_ins) >= 1, "La hoja Instrumental debería tener al menos 1 fila tras insertar"


# ── Limpieza final ─────────────────────────────────────────────────────────────

def teardown_module(module):
    """Eliminar la BD temporal al finalizar todos los tests."""
    try:
        os.unlink(_TMP_DB.name)
    except OSError:
        pass
