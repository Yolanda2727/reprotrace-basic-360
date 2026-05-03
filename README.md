# ReproTrace Basic 360° - Versión auditada

Sistema académico básico para monitoreo y trazabilidad de instrumental quirúrgico en una central de reprocesamiento hospitalario.

## Advertencia académica
Este prototipo no es un dispositivo médico, no reemplaza sistemas institucionales y no valida clínicamente la esterilización. Su finalidad es formativa, investigativa y demostrativa.

## Módulos
1. Inicio de sesión
2. Panel principal
3. Registro maestro de instrumental
4. Registro de etapas del reprocesamiento
5. Consulta de trazabilidad por instrumental y lote
6. Alertas y novedades
7. Reportes e indicadores exportables
8. Encuesta de percepción del personal
9. Matriz de riesgos y plan de mejora
10. Plan de pruebas básicas

## Usuarios de prueba
- admin / admin123
- central / central123
- docente / docente123

## Instalación
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Qué se corrigió en esta versión
- Se agregaron campos específicos por etapa.
- Se incorporó clasificación de Spaulding.
- Se agregó validación de hora final mayor o igual a hora inicial.
- Se agregó advertencia de secuencia lógica incompleta.
- Se incorporaron indicadores químicos, biológicos, temperatura, presión, almacenamiento y destino.
- Se incorporó matriz de riesgos.
- Se fortaleció el plan de pruebas.
- Se mantuvo alcance básico y académico.
