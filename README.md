# ⚖️ Mariano LegRAG IA

<div align="center">

**Mariano es un chatbot legal potenciado por inteligencia artificial que utiliza Generación Aumentada por Recuperación (RAG) con el modelo DeepSeek R1 para ofrecer razonamiento jurídico avanzado y análisis preciso de documentos legales.**

</div>

---

## 📋 Contenido

- [¿Qué es?](#-qué-es)
- [Arquitectura](#-arquitectura)
- [Búsqueda híbrida](#-búsqueda-híbrida)
- [Tecnologías y conceptos](#-tecnologías-y-conceptos)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Gestión de documentos](#-gestión-de-documentos)
- [¿Qué se guarda y qué se borra?](#-qué-se-guarda-y-qué-se-borra)
- [Configuración de la API](#-configuración-de-la-api)
- [Despliegue](#-despliegue)
- [Limitaciones conocidas](#-limitaciones-conocidas)
- [Documentación adicional](#-documentación-adicional)
- [Licencia](#-licencia)
- [Autor](#-autor)

---

## 🎯 ¿Qué es?

**Mariano LegRAG IA** es un asistente legal que analiza documentos jurídicos en PDF y responde preguntas en lenguaje natural. A diferencia de un chatbot genérico, Mariano:

- **Recupera** fragmentos relevantes con búsqueda híbrida (léxica + semántica).
- **Razona** sobre ellos con DeepSeek R1 vía API directa.
- **Fundamenta** cada respuesta con citas verificables del documento.
- **Genera** reportes descargables en TXT.

Todo el procesamiento de documentos ocurre en local; solo los fragmentos necesarios se envían a la API de DeepSeek sobre TLS.

---

## 🏗️ Arquitectura

![Arquitectura Mariano LegRAG IA](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/arquitectura-Mariano-LegRAG-IA.jpg)

---

## 🧠 Búsqueda híbrida

En el dominio jurídico, la búsqueda vectorial por sí sola resulta insuficiente. Los embeddings **suavizan** identificadores normativos exactos —`Artículo 74`, `Ley 27.442`, `plazo perentorio`— y pueden devolver fragmentos *temáticamente próximos* pero *jurídicamente inexactos*: versiones derogadas, plazos incompatibles o jurisprudencia no vinculante.

Mariano resuelve esta limitación combinando **tres capas de recuperación**:

| Capa | Herramienta | Función |
|------|-------------|---------|
| **Léxica** | BM25 | Recupera términos exactos: artículos, leyes, fechas y plazos. |
| **Semántica** | FAISS | Captura intención y contexto: *"¿qué ocurre si no se paga?"* → mora, intereses, ejecución. |
| **Fusión** | RRF | Combina ambos rankings sin depender de modelos adicionales ni servicios externos. |

La fusión se realiza mediante **Reciprocal Rank Fusion**, un mecanismo matemático que pondera la posición de cada fragmento en ambos rankings y favorece aquellos que resultan relevantes en las dos búsquedas simultáneamente. El proceso se ejecuta en milisegundos sobre CPU.

El resultado es un pipeline de recuperación **más preciso, más trazable y menos propenso a alucinaciones**: es posible auditar qué término activó la capa léxica y qué contexto aportó la capa semántica.

---

## 🛠️ Tecnologías y conceptos

| Tecnología | Qué es | Rol en Mariano |
|------------|--------|----------------|
| **DeepSeek R1** | Modelo de razonamiento con cadena de pensamiento extensa. | Genera análisis jurídico, interpreta normas y evalúa riesgos. |
| **API directa de DeepSeek** | Conexión a `api.deepseek.com` sin intermediarios. | Menor latencia, menor costo y control total del prompt. |
| **RAG** | *Retrieval-Augmented Generation*: inyección de contexto recuperado en el prompt del modelo. | Ancla las respuestas a los documentos reales del usuario. |
| **Chunking contextual** | División del documento en fragmentos coherentes. | Respeta la estructura jurídica (artículos, cláusulas, secciones). |
| **Embeddings** | Representación vectorial del texto. | Alimenta la búsqueda semántica sobre los fragmentos indexados. |
| **FAISS** | *Facebook AI Similarity Search*. | Índice vectorial para recuperación semántica de alta velocidad. |
| **BM25** | *Best Matching 25*. Algoritmo léxico con TF-IDF. | Garantiza recuperación exacta de terminología jurídica. |
| **RRF** | *Reciprocal Rank Fusion*. | Combina BM25 y FAISS preservando lo mejor de cada ranking. |
| **Streamlit** | Framework web en Python. | Interfaz de chat, carga de documentos y descarga de resultados. |
| **pdfplumber** | Extracción de texto de PDFs. | Convierte documentos legales en texto estructurado. |
| **Grounding** | Anclaje de la respuesta del modelo a fuentes verificables. | Cada respuesta cita el artículo, cláusula o página correspondiente. |
| **Indexación incremental** | Detección de cambios mediante hash. | Evita reprocesar documentos que no han sido modificados. |

---

## 📁 Estructura del proyecto

```
Mariano-LegRAG-IA/
├── frontend.py                # Interfaz Streamlit
├── vector_database.py         # BM25 + FAISS + RRF
├── rag_pipeline.py            # DeepSeek R1
├── gestion_documentos.py      # Estado e indexación incremental
├── bm25_retriever.py          # Búsqueda léxica
├── rrf_score.py               # Fusión de rankings
├── requirements.txt           # Dependencias
├── README.md                  # Este archivo
├── MANUAL.md                  # Guía de usuario completa
├── LICENSE
├── .gitignore
├── .env.example
├── pdfs/                      # (se crea al usar) PDFs subidos
└── vectorstore/               # (se crea al usar) Índice FAISS
```

---

## 📸 Capturas

<div align="center">

| Subida de documentos | Chat con Mariano |
|:--------------------:|:----------------:|
| ![Screenshot 1](utils/photo1.png) | ![Screenshot 2](utils/photo2.png) |

| Análisis legal | Reporte generado |
|:--------------:|:----------------:|
| ![Screenshot 3](utils/photo3.png) | ![Screenshot 4](utils/photo4.png) |

</div>

---

## ⚙️ Instalación

### Requisitos

- **Python 3.10** o superior
- **8 GB de RAM** recomendados
- **Conexión a internet** (solo para consultar el modelo)
- **API key de DeepSeek** ([platform.deepseek.com](https://platform.deepseek.com))
- **~2 GB de espacio libre** en disco (el modelo de embeddings ocupa ~1.2 GB)

### 1. Descargar el proyecto

**Opción A — Descargar ZIP:**

En la página de GitHub, pulsa el botón verde **`< > Code`** → **Download ZIP**. Descomprime en una carpeta, por ejemplo `C:\Mariano`.

**Opción B — Con Git:**

```bash
git clone https://github.com/actio1680/Mariano-LegRAG-IA
cd Mariano-LegRAG-IA
```

### 2. Crear entorno virtual e instalar dependencias

Abre **PowerShell** en la carpeta del proyecto (clic derecho dentro de la carpeta → "Abrir en Terminal"):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Si PowerShell bloquea el script de activación:**
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> .\venv\Scripts\Activate.ps1
> ```

La instalación tarda varios minutos. Descargará `torch`, `transformers` y demás dependencias (~2 GB en total).

### 3. Configurar la API key

Crea un archivo llamado `.env` en la raíz del proyecto (copia `.env.example` y renómbralo) con:

```
DEEPSEEK_API_KEY=tu_api_key_aqui
```

Obtén tu clave en [platform.deepseek.com](https://platform.deepseek.com) → sección **API Keys**.

> **Nota:** la primera vez que ejecutes la app, se descargará el modelo de embeddings legal en español (~1.2 GB). Tarda unos minutos. Después queda cacheado.

---

## 🚀 Uso

Con el entorno virtual activado:

```powershell
streamlit run frontend.py
```

Se abrirá tu navegador en `http://localhost:8501`.

**Flujo básico:**

1. **Sube uno o varios PDFs** desde el área principal. Verás una barra de progreso.
2. **Escribe tu pregunta** en el cuadro de texto.
3. **Pulsa "🔍 Preguntar a Mariano"**.
4. **Descarga el historial** desde el panel lateral si lo necesitas.

**Ejemplos de preguntas:**

- ¿Cuáles son las obligaciones de cada parte?
- ¿Qué dice el Artículo 74 sobre plazos?
- Resume las cláusulas de terminación.
- ¿Qué riesgos se mencionan en el documento?

---

## 🗂️ Gestión de documentos

En el **panel lateral** tienes estos botones:

| Botón | Qué hace |
|-------|----------|
| **🔄 Recargar documentos de la carpeta** | Carga los PDFs que estén en `pdfs/`. **No reindexa** los que ya estaban. |
| **🗑️ Limpiar documentos cargados e índice** | Borra **todo**: PDFs, índice, historial. **Irreversible.** |
| **📥 Descargar historial de consultas** | Guarda tus preguntas y respuestas en un archivo `.txt`. |

---

## 🧠 ¿Qué se guarda y qué se borra?

Mariano tiene **tres memorias** que se comportan distinto. Es importante que lo sepas para no llevarte sorpresas.

| Memoria | Qué guarda | ¿Se borra al cerrar? |
|---------|-----------|----------------------|
| **Chat de la sesión** | Tus preguntas y respuestas actuales | ✅ **Sí** — se pierde al cerrar la pestaña |
| **Índice de documentos** | El "conocimiento" extraído de tus PDFs | ❌ **No** — sigue en disco |
| **Registro de PDFs procesados** | Qué documentos ya fueron leídos | ❌ **No** — sigue en disco |

### ¿Qué significa esto en la práctica?

**Cuando cierras la app y la vuelves a abrir:**

- Tu conversación anterior **se ha ido**.
- Pero los PDFs siguen cargados y disponibles para consulta.
- Mariano te avisa: *"Hay información de una sesión anterior"*. Elige:
  - **▶️ Continuar** → reutiliza los documentos ya indexados.
  - **🗑️ Limpiar** → empieza de cero.

**Cuando borras un PDF de la carpeta `pdfs/` manualmente:**

- El índice **sigue teniendo su contenido**.
- Mariano te avisa: *"PDF huérfano: su índice sigue vivo"*.
- Pulsa **Limpiar** si quieres eliminarlo de verdad.

**Cuando subes el mismo PDF dos veces:**

- Mariano lo detecta por el hash del archivo.
- **No lo reprocesa.** Ahorra tiempo.

**Cuando pulsas "Limpiar documentos cargados e índice":**

- Se borran **los PDFs, el índice y el historial**.
- Es la forma limpia de empezar de cero.

---

## 🔑 Configuración de la API

- **Modelo:** `deepseek-reasoner` (DeepSeek R1)
- **Cliente:** `langchain-openai` con `base_url` apuntando a `https://api.deepseek.com/v1`
- **Costo:** DeepSeek cobra por uso. Consulta precios en [platform.deepseek.com](https://platform.deepseek.com).

---

## 🌐 Despliegue

### Streamlit Cloud (recomendado)

1. Sube el proyecto a GitHub:

```bash
git add .
git commit -m "Deploy Mariano LegRAG IA"
git push origin main
```

2. Entra en [share.streamlit.io](https://share.streamlit.io/).
3. Conecta tu repositorio.
4. Añade `DEEPSEEK_API_KEY` en **Secrets**.
5. Haz clic en **Deploy**.

### Alternativas

- **Docker:** contenerizar la aplicación.
- **Heroku / Render:** despliegue con `Procfile`.
- **AWS / GCP:** despliegue en instancias o servicios gestionados.
- **Servidor local:** ejecución en hardware dedicado.

---

## ⚠️ Limitaciones conocidas

- **Solo PDF con texto seleccionable.** Los PDFs escaneados (imágenes) requieren OCR, que Mariano no incluye.
- **Capacidad recomendada: hasta 30–40 PDFs** para uso cómodo. Con más, la indexación inicial tarda.
- **Idioma optimizado: español jurídico.** Los embeddings están ajustados para terminología legal peruana y española.
- **Requiere conexión a internet** para generar respuestas (consulta a la API de DeepSeek).
- **La primera indexación es lenta** (~10–20 min por PDF de 300 páginas). Después, los PDFs nuevos son más rápidos gracias a la indexación incremental.

---

## 📖 Documentación adicional

- **[MANUAL.md](MANUAL.md)** — Guía de usuario completa paso a paso.

---

## 📄 Licencia

MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**William Atencio Becerra** — © 2026 Actio1680. Todos los derechos liberados.
