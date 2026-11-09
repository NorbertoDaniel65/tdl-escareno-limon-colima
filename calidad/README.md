# Sistema de Calidad y Registros PSP (`calidad/`)

Esta carpeta concentra la evidencia de calidad del proceso (PSP) y de operación de la máquina de captura del observatorio:

| Archivo | Propósito | Estado en E0 |
|---|---|---|
| [`objetivos.md`](objetivos.md) | Definición formal de los **3 objetivos de calidad medibles** (O1 Disponibilidad $\ge 95\%$, O2 Completitud $\ge 98\%$ e Integridad SHA-256, O3 Cero PII y Cobertura $\ge 80\%$). | ✅ Completo |
| [`tiempo-norberto.csv`](tiempo-norberto.csv) | Registro individual de tiempos PSP con el formato oficial (`fecha,inicio,fin,interrupcion_min,fase,actividad`). | ✅ Activo (6 sesiones registradas en E0) |
| [`defectos-norberto.csv`](defectos-norberto.csv) | Registro individual de defectos PSP con los 10 tipos estándar (`numero,fecha,tipo,fase_introducido,fase_eliminado,minutos_correccion,defecto_origen,descripcion`). | ✅ Activo (4 defectos reales documentados y corregidos en E0) |
| [`bitacora_capturas.jsonl`](bitacora_capturas.jsonl) | Bitácora estructurada en formato JSON Lines alimentada automáticamente en cada ejecución del extractor ético (base para el cálculo de MTBF, MTTR y disponibilidad real en E1). | ✅ Activa |
