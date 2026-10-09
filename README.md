

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
- [Licencia y créditos](#️-licencia-y-créditos)

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

![Arquitectura Mariano LegRAG IA](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/image/arquitectura-Mariano-LegRAG-IA.jpg)

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

| Presentación Mariano IA | Subida de documentos |
|:--------------------:|:----------------:|
| ![Imagen 1](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/image/foto1.png) | ![Imagen 2](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/image/foto2.png) |

| Chat de Análisis legal | Reporte generado |
|:--------------:|:----------------:|
| ![Imagen 3](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/image/foto3.png) | ![Imagen 4](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/image/foto4.png) |

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
```
```bash
cd Mariano-LegRAG-IA
```

### 2. Crear entorno virtual e instalar dependencias

Abre **PowerShell** en la carpeta del proyecto (clic derecho dentro de la carpeta → "Abrir en Terminal"):

```bash
python -m venv venv
```
```bash
.\venv\Scripts\Activate.ps1
```
```bash
pip install -r requirements.txt
```

> **Si PowerShell bloquea el script de activación:**
> ```bash
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```
> ```bash
> .\venv\Scripts\Activate.ps1
> ```

La instalación tarda varios minutos. Descargará `torch`, `transformers` y demás dependencias (~2 GB en total).

### 3. Configurar la API key

En la raíz del proyecto existe el archivo `.env.example`, renómbralo a `.env`; posteriormente, edita el contenido con tu clave (API key):

```bash
DEEPSEEK_API_KEY=tu_api_key_aqui
```

Obtén tu clave en [platform.deepseek.com](https://platform.deepseek.com) → sección **API Keys**. Puedes realizar la recarga desde $2 dólares en la sección **Top up**.

> **Nota:** la primera vez que ejecutes la app, se descargará el modelo de embeddings legal en español (~1.2 GB). Tarda unos minutos. Después queda cacheado.

---

## 🚀 Uso

Con el entorno virtual activado:

```bash
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

## 🔑 Configuración de la API

- **Modelo:** `deepseek-reasoner` (DeepSeek R1)
- **Cliente:** `langchain-openai` con `base_url` apuntando a `https://api.deepseek.com/v1`
- **Costo:** DeepSeek cobra por uso. Consulta precios en [platform.deepseek.com](https://platform.deepseek.com).

---

## ⚠️ Limitaciones conocidas

- **Solo PDF con texto seleccionable.** Los PDFs escaneados (imágenes) requieren OCR, que Mariano no incluye.
- **Capacidad recomendada: hasta 30–40 PDFs** para uso cómodo. Con más, la indexación inicial tarda.
- **Idioma optimizado: español jurídico.** Los embeddings están ajustados para terminología legal peruana y española.
- **Requiere conexión a internet** para generar respuestas (consulta a la API de DeepSeek).
- **La primera indexación es lenta** (~10–20 min por PDF de 300 páginas). Después, los PDFs nuevos son más rápidos gracias a la indexación incremental.

---

## 📖 Documentación adicional

- 📘 [MANUAL](MANUAL.md) — Guía de usuario completa paso a paso para configurar e interactuar con Mariano.


## ⚖️ Licencia y Créditos

Bajo [Licencia MIT](LICENSE). Libertad total de uso y modificación manteniendo la atribución:

- 👤 **William Atencio Becerra** — © 2026 [Actio1680](https://github.com).
- 🔌 **Base:** Infraestructura original de **bigdata5911**.

