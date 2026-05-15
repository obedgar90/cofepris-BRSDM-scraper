# cofepris-BRSDM-scraper

Este script obtiene automáticamente y de forma periódica el contenido del sitio de COFEPRIS México de Visor de Registros de Medicamentos

## Antecedentes

La COFEPRIS (Comisión Federal para la Protección contra Riesgos Sanitarios) liberó un portal desde donde se pueden descargar los registros de medicamentos. La url actual (Abril 2026) del portal está en [[esta URL](https://tramiteselectronicos02.cofepris.gob.mx/BRSDM/default.aspx)] https://tramiteselectronicos02.cofepris.gob.mx/BRSDM/default.aspx

Dicho portal cuanta con un selector combobox para descargar en excel la información del registro de Medicamentos.

## Motivación

Como parte del derecho constitucional mexicano de acceder a la información pública, se desarrolla este proyecto y se pone a disposición del público general para que la información expuesta en el portal mencionado pueda ser descargada automaticamente y cargada en una base de datos para su posible análisis y uso según el marco de derecho.

## Funcionamiento

Se utiliza Playwright para  entrar al portal y seleccionar la descarga del regisro completo en el selector y presionar el botón descargar para luego insertar el resultado descargado en excel en una base de datos.

### Pasos

1. Se ejecuta el script de playwright en modo headless para entrar al portal y descargar el archivo
2. Una vez descargado el archivo, se utiliza la librería pandas para normalizar los headers del archivo para que no tengan acentos u otro tipo de caracteres especiales, estén en minúsculas y se sustituyan los espacios por guión bajo (_). El objetivo es que no existan problemas de compatibilidad con la base de datos
3. Con el archivo preparado en excel, pandas convierte el dataset a SQL compatible con PostreSQL y lo inserta a la base de datos con un engine creado por SQLAlchemy

### Consideraciones

- El proyecto debe usar principios SOLID de desarrollo de software
- El proyecto debe tener un archivo AGENTS.md actualizado con instrucciones específicas para agentes LLM
- El proyecto debe utilizar el principio TDD (Test Driven Development). Escribir pruebas antes de escribir el código funcional y siempre comprobar contra pruebas
- El proyecto debe utilizar contenedores para ser ejecutado
- Todo el código debe estar documentado en español

#### Consideraciones técnicas

- Lenguaje de programación: Python
- Contenedores: docker compose
- Pruebas: Pytest
- Browser para ejecutar scraping: Chromium

### Inspiración

Se hicieron pequeñas pruebas de concepto que sirven de inspiración arquitectónica para el proyecto

#### Inspiración para el scraper

El siguiente código se generó utilizando la extensión de Playwright desde un navegador basado en Chromium

```python
import re

from playwright.sync_api import Page, expect

def test_example(page: Page) -> None:
page.goto("https://tramiteselectronicos02.cofepris.gob.mx/BRSDM/default.aspx")
page.locator("#ContentPlaceHolder1_DropDownList1").select_option("7")
page.get_by_role("button", name="Descargar").click()
```

Este código es un ejemplo simple que funciona para descargar el catálogo completo y la parte de scraping puede estar basado en este código. Aunque el código final y productivo debe de contar con los principios arriba mencionados, además de contar con las verificaciones, arquitectura y estilo de código suficientes para garantizar la calidad, mantenibilidad y estabilidad del proyecto.

Además se deben considerar casos de fallo por indisponibilidad del portal, cambio de UI y demás consideraciones

#### Inspiración para la subida a base de datos

El siguiente código fue generando utilizando Inteligencia Artificial y ha sido validado humanamente:

```python
import pandas as pd
from sqlalchemy import create_engine

# 1. Configuración de la conexión a PostgreSQL
# Formato: postgresql+psycopg2://usuario:contraseña@host:puerto/nombre_base_datos
engine = create_engine('postgresql+psycopg2://usuario:password@localhost:5432/mi_base_datos')

# 2. Leer archivo Excel
archivo_excel = 'datos.xlsx'
df = pd.read_excel(archivo_excel, sheet_name='Hoja1') # Cambia 'Hoja1' por el nombre real

# 3. Subir a PostgreSQL
df.to_sql(
    'nombre_tabla_destino', # Nombre de la tabla en Postgres
    engine,
    if_exists='replace', # Opciones: 'fail', 'replace', 'append'
    index=False,         # No subir el índice de Pandas como columna
    chunksize=10000      # Útil para archivos grandes (subir por lotes)
)

print("Datos subidos exitosamente.")
```

Se considera como un ejemplo simple sólo para demostrar como se debe procesar el archivo excel obtenido, sin embargo, el código final y productivo debe de contar con las validaciones necesarias para la subida completa de los datos de una forma debida para ser analizados y consumidos de la forma más óptima.

## Estructura del archivo excel (13 de Mayo 2026)

El archivo excel que se descarga de la opción "COMPLETO" del portal tiene los siguientes encabezados:

* Número de Registro
* Denominación Distintiva
* Fecha Expedición Vigencia
* Fecha Expedición Vigencia Prorroga
* Estado
* Forma Farmaceutica
* Indicaciones Terapéuticas
* Contra Indicaciones
* Vida Útil
* Fracción
* Denominacion Generica
* Vista Administración
* Tipo Medicamento
* Presentación
* Cantidad
* Sistema Orgánico
* Grupo Farmacológico
* Subgrupo Farmacológico
* Subgrupo QuÍmico
* Sustancia Química
* Titular
* Domicilio
* Fabricantes Medicamentos
* Fabricantes Farmacos
* Acondicionado Por
* Acondicionado Extranjero
* Distribuidores
* Unidad Farmaco Vigilancia
* Fecha Emisión

Un ejemplo de encabezado con 3 registros es:

| Número de Registro | Denominación Distintiva | Fecha Expedición Vigencia | Fecha Expedición Vigencia Prorroga | Estado | Forma Farmaceutica | Indicaciones Terapéuticas | Contra Indicaciones | Vida Útil | Fracción | Denominacion Generica | Vista Administración | Tipo Medicamento | Presentación | Cantidad | Sistema Orgánico | Grupo Farmacológico | Subgrupo Farmacológico | Subgrupo QuÍmico | Sustancia Química | Titular | Domicilio | Fabricantes Medicamentos | Fabricantes Farmacos | Acondicionado Por | Acondicionado Extranjero | Distribuidores | Unidad Farmaco Vigilancia | Fecha Emisión |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 363M2018 SSA | ROLODIQUIM FST | 28 de Noviembre de 2018 / 28 de Noviembre de 2023 | 8 de Mayo de 2023 / 8 de Mayo de 2028 | VIGENTE | TABLETA | ANALGÉSICO NO NARCÓTICO. | HIPERSENSIBILIDAD AL FÁRMACO O A LOS COMPONENTES DE LA FÓRMULA, PACIENTES CON ANTECEDENTES O HEMORRAGIA ACTIVA, PERFORACIÓN GASTROINTESTINAL RECIENTE RELACIONADAS CON AINES, CON ÚLCERA O HEMORRAGIA PÉPTICA RECURRENTES, INSUFICIENCIA CARDIACA GRAVE, INSUFICIENCIA RENAL MODERADA O GRAVE (CREATININA SÉRICA > 442 µMOL/L O 5 MG/DL) Y EN LOS PACIENTES CON RIESGO DE INSUFICIENCIA RENAL POR HIPOVOLEMIA O DESHIDRATACIÓN, DURANTE EL PARTO, PACIENTES CON ANTECEDENTES DE ALERGIA AL ÁCIDO ACETILSALICÍLICO U OTROS INHIBIDORES DE LA SÍNTESIS DE PROSTAGLANDINAS, PREVIO O DURANTE UNA INTERVENCIÓN QUIRÚRGICA, PACIENTES CON HEMORRAGIA CEREBROVASCULAR POSIBLE O CONFIRMADA, PACIENTES QUE HAN TENIDO CIRUGÍAS CON UN ALTO RIESGO DE HEMORRAGIA O HEMOSTASIA INCOMPLETA, Y AQUELLOS CON ALTO RIESGO DE SANGRADO, USO CONCOMITANTE CON ÁCIDO ACETILSALICÍLICO U OTROS AINES. LA COMBINACIÓN CON PENTOXIFILINA ESTÁ CONTRAINDICADA, MENORES DE 16 AÑOS DE EDAD Y EN EL POSTOPERATORIO DE AMIGDALECTOMÍA. | 24 meses debiendo expresar el año con número y el mes con letra. | IV. Medicamentos que para adquirirse requiere receta médica, pero que pueden resurtirse tantas veces como lo indique el médico | KETOROLACO / / / | SUBLINGUAL | GENÉRICO | Caja de cartón con 2, 4 o 6 tabletas de 30 mg en envase de burbuja. | Ketorolaco trometamina 30.000 mg | M SISTEMA MUSCULOESQUELÉTICO | M01 Productos antiinflamatorios y antirreumáticos | M01A Productos antiinflamatorios y antirreumáticos no esteroideos. | M01AB Derivados del ácido acético y sustancias relacionadas. | M01AB15 Ketorolaco | QUIMICA Y FARMACIA, S.A. DE C.V. | BOULEVARD INDUSTRIA AUTOMOTRIZ 3045, FRACC. II 3045 FRACC II,PARQUE INDUSTRIAL SALTILLO-RAMOS ARIZPE, C.P. 25900, RAMOS ARIZPE, COAHUILA DE ZARAGOZA, MÉXICO | QUÍMICA Y FARMACIA, S. A. DE C. V. ,Blvd. Ind. Automotriz No. 3045 Fracc. II, Parque Industrial Saltillo-Ramos Arizpe, C.P. 25900, Ramos Arizpe, Coahuila, MÉXICO | SYMED LABORATORIES LIMITED. ,Unit II, Plot No. 25/B Phase III, IDA Jeedimetla, Hyderabad, Telangana, 500055, India | PERRIGO DE MEXICO, S.A. DE C.V., AV. INDUSTRIAL AUTOMOTRIZ No. 3089, PARQUE INDUSTRIAL RAMOS ARIZPE, C.P. 25900, RAMOS ARIZPE, COAHUILA DE ZARAGOZA, MÉXICO | QUIMICA Y FARMACIA, S.A. DE C.V., Blvd. Ind. Automotriz No. 3045 Fracc. II,, Parque Industrial Saltillo-Ramos Arizpe, C.P. 25900, RAMOS ARIZPE, COAHUILA DE ZARAGOZA, MÉXICO | | QUIMICA Y FARMACIA, S.A. DE C.V. , Blvd. Ind. Automotriz No. 3045 Fracc. II, Parque Industrial Saltillo-Ramos Arizpe, C.P. 25900, RAMOS ARIZPE, Coahuila de Zaragoza, MÉXICO | Nov 29 2018 4:00AM |
| 004M2020 SSA | ELIFORE | 17 de Enero de 2020 / 17 de Enero de 2025 | 30 de Agosto de 2024 / 30 de Agosto de 2029 | CANCELADO | TABLETA | TRASTORNO DEPRESIVO MAYOR Y SÍNTOMAS VASOMOTORES ASOCIADOS CON LA MENOPAUSIA. | HIPERSENSIBILIDAD A LOS COMPONENTES DE LA FÓRMULA, NO DEBE USARSE CONJUNTAMENTE CON IMAO, EN PRESENCIA DE HIPERTENSIÓN ARTERIAL NO CONTROLADA, EMBARAZO, LACTANCIA Y EN MENORES DE 18 AÑOS. | 24 meses, debiendo expresar el año con número y el mes con letra. | IV. Medicamentos que para adquirirse requiere receta médica, pero que pueden resurtirse tantas veces como lo indique el médico | DESVENLAFAXINA / / / | ORAL | GENÉRICO | Caja de cartón con 14 o 28 tabletas de 50 mg <br> Caja de cartón con 14 o 28 tabletas de 100 mg. | Desvenlafaxina 50.000 mg <br> Desvenlafaxina 100.000 mg | N SISTEMA NERVIOSO | N06 Psicoanalépticos | N06A Antidepresivos | N06AX Otros antidepresivos | N06AX23 Desvenlafaxina | PHARMACIA & UPJOHN COMPANY LLC | 7000 PORTAGE ROAD, KALAMAZOO, MI 49001, ESTADOS UNIDOS DE AMÉRICA EUA | PFIZER IRELAND PHARMACEUTICALS. ,Little Connell, Newbridge Co., Kildare,, Irlanda | PFIZER ASIA PACIFIC PTE LTD ,31 Tuas South Avenue 6 Singapure 637578,, Singapur <br> PFIZER IRELAND PHARMACEUTICALS ,Ringaskiddy Active Pharmaceutical Ingredient Plant, P.O. Box 140, Ringaskiddy, County Cork, Irlanda. <br> SIEGFRIED AG ,Untere Brühlstrasse 4, 4800 Zofingen, Suiza | PFIZER, S.A. DE C.V., CARRETERA MEXICO-TOLUCA KM. 63, ZONA INDUSTRIAL, C.P. 50140, TOLUCA, MÉXICO, MÉXICO | | PFIZER, S.A. DE C.V. , CARRETERA MEXICO-TOLUCA KM. 63, ZONA INDUSTRIAL, C.P. 50140, TOLUCA, México, MÉXICO | PFIZER, S.A. DE C.V. , CARRETERA MEXICO-TOLUCA KM. 63, ZONA INDUSTRIAL, C.P. 50140, TOLUCA, México, MÉXICO | Jan 17 2020 10:00AM |
| 305M2018 SSA | THERAFLU THERAPILLIS | 8 de Agosto de 2018 / 9 de Agosto de 2024 | 15 de Marzo de 2024 / 15 de Marzo de 2029 | VIGENTE | TABLETA | AUXILIAR EN EL TRATAMIENTO SINTOMÁTICO DEL RESFRIADO COMÚN. | HIPERSENSIBILIDAD A LOS COMPONENTES DE LA FORMULA, HIPERTENSIÓN ARTERIAL NO CONTROLADA, ASMA, DIABETES MELLITUS DESCOMPENSADA, ENFERMEDAD GRAVE DE ARTERIAS CORONARIAS, HIPERTIROIDISMO, HIPERTROFIA PROSTÁTICA, GLAUCOMA DE ÁNGULO ESTRECHO, ADMINISTRACIÓN CONCOMITANTE CON MEDICAMENTOS DEPRESORES DEL SISTEMA NERVIOSO O CON INHIBIDORES DE LA MAO, EMBARAZO, LACTANCIA Y MENORES DE 12 AÑOS. | 24 meses, debiendo expresar el año con número y el mes con letra. | VI. Medicamentos que para adquirirse no requieren receta médica y que pueden expenderse en otros establecimientos que no sean farmacias | PARACETAMOL / FENILEFRINA / CLORFENAMINA / | ORAL | GENÉRICO | Caja de cartón con 8, 10 o 12 tabletas en sobres con 2 tabletas cada uno. Exhibidor para 25, 50 o 52 sobres con 2 tabletas cada uno. Sobre con dos tabletas. | Paracetamol 500.000 mg <br> Fenilefrina 5.001 mg <br> Clorfenamina 2.008 mg | R SISTEMA RESPIRATORIO | R01 Preparados de uso nasal | R01B Descongestivos nasales para uso sistémico. | R01BA Simpaticomiméticos. | R01BA53 Fenilefrina, combinations | GLAXOSMITHKLINE CONSUMER HEALTHCARE MEXICO, S. DE RL. DE C.V. | CALLE 21-E 104 NA,CIVAC, JIUTEPEC, MORELOS, MÉXICO | HALEONPANAMÁ, S.A. ,Corregimiento de Juan Díaz, Urbanización calle A y B, Urbanización Industrial de la Ciudad de Panamá, República de Panamá. | DIVI´S LABORATORIES LIMITED ,Unit-2, Chippada Village, Annavaram Post, Bheemunipatnam Mandal, Visakhapatnam District, Andhra Padresh 531 162, India <br> GRANULES INDIA LIMITED. ,H. No: 6-5 & 6-11, Temple Road, Bonthpally, Village Gummadidala Mandal, Sangareddy, Telangana, 502313, India. <br> KONGO CHEMICAL CO., LTD. ,Head Plant, 3, Himata, Toyama-City, Toyama, 930-0912, Japón | | GLAXOSMITHKLINE PANAMÁ, S.A ,Urbanización Industrial, calle A y B, Corregimiento de Juan Díaz, Provincia de Panamá, 0819-08530, Panamá, República de Panamá | GLAXOSMITHKLINE CONSUMER HEALTHCARE MEXICO, S. DE R.L. DE C.V. , Calle 21-E. NO. 104, CIVAC, C.P. 62578, JIUTEPEC, Morelos, MÉXICO | | Nov 9 2018 4:00AM |

De cualquier forma dentro de este proyecto hay un archivo de ejemplo descargado el 13 de Mayo de 2026 en [/info/Visor_Registros_Medicamentos.xlsx](/info/Visor_Registros_Medicamentos.xlsx)

## Instalación y ejecución (paso a paso)

Esta guía está pensada para personas con conocimientos básicos de terminal.
Sigue los pasos en orden y copia/pega los comandos tal como están.

### 1) Requisitos previos

Necesitas tener instalado:

- `git`
- `python3` (recomendado 3.12 o superior)
- `docker` y `docker compose` (si usarás la opción con contenedores)

Comandos para validar que ya los tienes:

```bash
git --version
python3 --version
docker --version
docker compose version
```

### 2) Clonar el repositorio y entrar al proyecto

```bash
git clone git@github.com:Quantium/cofepris-BRSDM-scraper.git
cd cofepris-BRSDM-scraper
```

### 3) Crear archivo de configuración local

El proyecto usa variables de entorno. Crea tu archivo local `.env`:

```bash
cp .env.example .env
```

Después abre `.env` y revisa, al menos, `DATABASE_URL`.

Audit attempts are stored in PostgreSQL using `ATTEMPTS_TABLE_NAME` (default: `scraping_attempts`).

### 3.1) Anti-bot scraping settings (optional)

The downloader now supports configurable anti-detection hardening for Playwright.
You can keep defaults, or tune these values in `.env`:

- `SCRAPER_STEALTH_ENABLED`: enables browser hardening and JS fingerprint evasions.
- `SCRAPER_HEADLESS`: run browser headless (`true`) or visible (`false`).
- `SCRAPER_USER_AGENT`: browser user agent used in context.
- `SCRAPER_VIEWPORT_WIDTH` and `SCRAPER_VIEWPORT_HEIGHT`: browser viewport profile.
- `SCRAPER_LOCALE` and `SCRAPER_TIMEZONE_ID`: locale/timezone browser signals.
- `SCRAPER_PROXY_SERVERS`: comma-separated proxy endpoints for per-attempt rotation.
- `SCRAPER_PROXY_USERNAME` and `SCRAPER_PROXY_PASSWORD`: optional proxy auth.

Example:

```bash
SCRAPER_PROXY_SERVERS=http://proxy-1:8080,http://proxy-2:8080
SCRAPER_PROXY_USERNAME=my-user
SCRAPER_PROXY_PASSWORD=my-pass
```

### 3.2) Proxy Strategy V2 (health + circuit breaker + sticky domain)

Proxy Strategy V2 is optional and disabled by default.
Enable it when you need stronger resilience against IP-level blocks.

- `SCRAPER_PROXY_V2_ENABLED`: enables persisted V2 strategy.
- `SCRAPER_PROXY_CIRCUIT_FAILURE_THRESHOLD`: failures before opening a circuit.
- `SCRAPER_PROXY_CIRCUIT_COOLDOWN_SECONDS`: cooldown window for open circuits.
- `SCRAPER_PROXY_HALF_OPEN_MAX_TRIALS`: max probe attempts in half-open state.
- `SCRAPER_PROXY_STICKY_TTL_SECONDS`: sticky proxy reuse window per domain.
- `SCRAPER_PROXY_HEALTH_DECAY_ON_SUCCESS`: health recovery on successful attempts.
- `SCRAPER_PROXY_HEALTH_PENALTY_TIMEOUT`: penalty applied on timeout/transient errors.
- `SCRAPER_PROXY_HEALTH_PENALTY_BLOCK`: penalty applied on explicit bot-block signals.
- `SCRAPER_PROXY_STRATEGY_FAILOPEN`: fallback to baseline proxy selection if strategy store fails.

Recommended starting values:

```bash
SCRAPER_PROXY_V2_ENABLED=true
SCRAPER_PROXY_CIRCUIT_FAILURE_THRESHOLD=3
SCRAPER_PROXY_CIRCUIT_COOLDOWN_SECONDS=600
SCRAPER_PROXY_STICKY_TTL_SECONDS=900
SCRAPER_PROXY_STRATEGY_FAILOPEN=true
```

---

## Opción A (recomendada para principiantes): correr con Docker

Esta opción evita instalar dependencias de Python manualmente.

### A.1 Levantar servicios

```bash
docker compose up --build
```

Qué hace este comando:

- Construye la imagen del proyecto.
- Levanta PostgreSQL.
- Starts Adminer for web-based database inspection.
- Ejecuta el pipeline una vez.

### A.2 Verificar que terminó correctamente

En la salida de terminal debe aparecer un JSON con `"status": "ok"`.

Para detener los servicios:

```bash
docker compose down
```

Adminer web UI (local):

- URL: `http://localhost:8080`
- System: `PostgreSQL`
- server: `postgres`
- Username: `postgres`
- Password: `postgres`
- Database: `cofepris`

### A.3 Modo desarrollo con volumen (sin rebuild por cada cambio)

Este modo monta tu código local dentro del contenedor para que los cambios en
`src/` se reflejen inmediatamente.

Puedes usar comandos cortos con `make`:

```bash
make dev-up
make dev-run
make dev-down
```

Equivalencias:

- `make dev-up`: levanta PostgreSQL + Adminer + contenedor de desarrollo con volúmenes.
- `make dev-run`: ejecuta `cofepris run` dentro del contenedor de desarrollo.
- `make dev-down`: baja los servicios de desarrollo.

Si prefieres ejecutarlo sin `make`, usa estos comandos directos:

1. Levanta PostgreSQL, Adminer y el contenedor de desarrollo:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d postgres adminer app-dev
```

1. Ejecuta el pipeline desde el contenedor de desarrollo:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app-dev cofepris run
```

1. Haz cambios en tu código local (por ejemplo en `src/`) y vuelve a ejecutar
el mismo comando del paso 2. No necesitas reconstruir la imagen.

1. Cuando termines:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

---

## Opción B: correr en tu máquina (sin Docker)

### B.1 Crear ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Nota: si cierras la terminal, vuelve a activar el ambiente con:

```bash
source .venv/bin/activate
```

### B.2 Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### B.3 Ejecutar el pipeline una vez

```bash
cofepris run
```

Si todo está bien, verás salida JSON con `"status": "ok"`.

### B.4 Ejecutar en modo periódico (daemon)

Ejemplo: correr todos los días a las 6:00 AM.

```bash
cofepris daemon --cron "0 6 * * *"
```

Detener el daemon: `Ctrl + C`.

---

## Comandos de validación de calidad (opcional)

```bash
ruff check .
mypy src
pytest -q
python scripts/check_story_docs.py
```

---

## Problemas comunes

- Error de conexión a base de datos:
  - Revisa `DATABASE_URL` en `.env`.
  - Si usas Docker, confirma que `postgres` esté levantado.
- Adminer is not reachable at `http://localhost:8080`:
  - Verify the `adminer` service is running.
  - Check whether port `8080` is already in use by another app.
- Adminer cannot connect to PostgreSQL:
  - Confirm Adminer uses `server: postgres` (not `localhost`).
  - Wait until `postgres` is healthy before logging in.
- Error `command not found: cofepris`:
  - Activa tu ambiente virtual (`source .venv/bin/activate`) o usa Docker.
- Error al instalar dependencias en macOS por entorno administrado:
  - Usa ambiente virtual (`python3 -m venv .venv`) en lugar de instalar globalmente.

## Comunidad y contribuciones

Si deseas aportar al proyecto, revisa primero estos archivos:

- [Guía de contribución](CONTRIBUTING.md)
- [Código de Conducta](CODE_OF_CONDUCT.md)
- [Política de Seguridad](SECURITY.md)
- [Soporte](SUPPORT.md)

Al abrir un Issue o Pull Request en GitHub, se te mostrarán plantillas en español para facilitar reportes y propuestas.
