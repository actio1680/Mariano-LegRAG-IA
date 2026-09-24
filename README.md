## ⚖️ Mariano LegRAG IA

<div align= "center">
Mariano es un chatbot legal potenciado por inteligencia artificial que utiliza Generación Aumentada por Recuperación (RAG) con el modelo DeepSeek R1 para ofrecer razonamiento jurídico avanzado y análisis preciso de documentos legales.
</div>

## 📋 Contenido

- [¿Qué es?](#-qué-es)
- [Arquitectura](#-arquitectura)
- [Pipeline de recuperación híbrida](#-pipeline-de-recuperación-híbrida)
- [Tecnologías y conceptos](#-tecnologías-y-conceptos)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Configuración de API](#-configuración-de-api)
- [Despliegue](#-despliegue)
- [Roadmap](#-roadmap)
- [Licencia](#-licencia)

## 🎯 ¿Qué es?

**Mariano LegRAG IA** es un asistente legal que analiza documentos jurídicos en PDF y responde preguntas en lenguaje natural. A diferencia de un chatbot genérico, Mariano:

- **Recupera** fragmentos relevantes con búsqueda híbrida (léxica + semántica).
- **Razona** sobre ellos con DeepSeek R1 vía API directa.
- **Fundamenta** cada respuesta con citas verificables del documento.
- **Genera** reportes descargables en TXT/Markdown.

Todo el procesamiento de documentos ocurre en local; solo los fragmentos necesarios se envían a la API de DeepSeek sobre TLS.

## 🏗️ Arquitectura

 ![Arquitectura MARIANO LegRAG IAT](https://raw.githubusercontent.com/actio1680/Mariano-LegRAG-IA/refs/heads/main/arquitectura-Mariano-LegRAG-IA.jpg) 

## 🧠 Búsqueda híbrida: por qué mejora la precisión

La búsqueda vectorial pura falla en derecho: los embeddings **suavizan** términos exactos como `"Artículo 74"`, `"Ley 27.442"` o `"plazo perentorio"`. Un recuperador que solo usa FAISS puede inyectar al LLM fragmentos *temáticamente similares* pero *jurídicamente incorrectos* (versiones derogadas, plazos conflictivos, jurisprudencia no vinculante). Esto se conoce como **Context Poisoning**.

Mariano lo mitiga con **tres capas**:

| Capa | Herramienta | Función |
|------|-------------|---------|
| Léxica | **BM25** | Recupera términos exactos: artículos, leyes, fechas, plazos. |
| Semántica | **FAISS** | Captura intención y contexto: "¿qué pasa si no pago?" → mora, intereses, ejecución. |
| Fusión | **RRF** | Combina ambos rankings sin modelos extra ni APIs externas. |

**RRF (Reciprocal Rank Fusion)** combina rankings sumando posiciones recíprocas: RRF_score(d) = Σ 1 / (k + rank_i(d))

Penaliza documentos que solo aparecen en un ranking y eleva los que son relevantes en ambos. Se ejecuta en milisegundos en CPU. **Resultado:** menos alucinaciones, más precisión, latencia baja y trazabilidad (se puede auditar qué término activó BM25 y qué contexto aportó FAISS).

## 🛠️ Tecnologías y conceptos

| Tecnología | Qué es | Rol en Mariano |
|------------|--------|----------------|
| **DeepSeek R1** | Modelo de razonamiento con cadena de pensamiento larga. | Genera análisis jurídico, interpreta normas, evalúa riesgos. |
| **API directa DeepSeek** | Llamada a `api.deepseek.com` sin intermediarios. | Menos latencia, menos costo, control total del prompt. |
| **RAG** | *Retrieval-Augmented Generation*: inyectar contexto recuperado en el prompt del LLM. | Evita que el modelo alucine: responde sobre los documentos reales. |
| **Chunking** | División del documento en fragmentos manejables. | Se respeta la estructura legal (artículos, cláusulas, secciones). |
| **Embeddings** | Representación vectorial del texto. Textos similares → vectores cercanos. | Alimentan la búsqueda semántica. |
| **FAISS** | *Facebook AI Similarity Search*. Índice vectorial eficiente. | Búsqueda semántica sobre los chunks. |
| **BM25** | *Best Matching 25*. Algoritmo léxico con TF-IDF y normalización. | Recuperación exacta de términos jurídicos. |
| **RRF** | *Reciprocal Rank Fusion*. Fusión de rankings por posición recíproca. | Combina BM25 y FAISS sin modelos extra. |
| **Streamlit** | Framework web en Python. | Interfaz de chat, carga de PDF y descarga de reportes. |
| **pdfplumber** | Extracción de texto de PDFs. | Convierte PDFs legales en texto estructurado. |
| **Grounding** | Anclar la respuesta del LLM a fuentes verificables. | Cada respuesta cita artículo/cláusula/página. |
| **Hash + indexación incremental** | Detección de cambios por hash. | Evita reprocesar documentos sin modificaciones. |

## 📁 Estructura del proyecto

Mariano-LegRAG-IA/
├── frontend.py # Interfaz Streamlit
├── rag_pipeline.py # Pipeline RAG + DeepSeek R1
├── vector_database.py # BM25 + FAISS + RRF
├── requirements.txt # Dependencias
├── README.md
├── utils/ # Capturas y utilidades
└── .streamlit/ # Configuración (si aplica)

## ⚙️ Instalación

### Requisitos
- Python 3.8+
- API key de DeepSeek ([platform.deepseek.com](https://platform.deepseek.com))
- Git

### Pasos

```bash
git clone https://github.com/bigdata5911/Mariano-LegRAG-IA
cd Mariano-LegRAG-IA

python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt



### 🏗️ Hacia un Context Engineering Multi-Etapa (Estándar Industrial)
Para resolver esto, la ingeniería de RAG moderna exige pasar de una recuperación simple a una **arquitectura de recuperación estratificada**:
1. **🔍 Búsqueda Híbrida:** La búsqueda vectorial pura capta la intención latente, pero **BM25 es innegociable** para recuperar keywords exactos, números de artículo, fechas o etiquetas de versión que los embeddings tienden a difuminar.
2. **🔄 Reranking con Cross-Encoder:** Actúa como `"capa de decisión"`. Una segunda pasada sobre los candidatos `top-N` evalúa pares `query-documento` con atención a nivel de token, separando señal real de ruido contextual.
3. **✂️ Contextual Pruning:** Extrae solo las oraciones o párrafos verdaderamente relevantes de chunks extensos, reduciendo la `"distracción contextual"` y evitando que el LLM se pierda en información irrelevante al final de la ventana.

> 💡 *La generación en RAG se ha vuelto un commodity. La capa de recuperación es donde ocurre la ingeniería real. La precisión en la ventana de contexto es el diferenciador principal entre un experimento de IA y un activo de producción.*

---

### ✅ Lo que implementamos en Mariano LegRAG IA

Si bien el reranking con Cross-Encoder y el pruning contextual representan el estado del arte, en **Mariano LegRAG IA** hemos priorizado una arquitectura **eficiente, autocontenida y de bajo costo**, implementando una **Búsqueda Híbrida con Fusión RRF (Reciprocal Rank Fusion)**. Esta decisión equilibra precisión jurídica, velocidad de inferencia y simplicidad de despliegue, sin depender de APIs externas de reranking ni añadir latencia.

#### 🔧 Arquitectura de recuperación implementada:
| Componente | Función | Ventaja Jurídica |
|------------|---------|------------------|
| **🔍 BM25** | Búsqueda léxica con índice invertido | Garantiza recuperación exacta de artículos, leyes, plazos y terminología técnica. |
| **🧮 FAISS** | Búsqueda semántica con embeddings | Captura contexto, intención y conceptos relacionados (ej: `"¿qué pasa si no pago?"` → mora, intereses, ejecución). |
| **⚖️ RRF** | Fusión matemática de rankings | Combina ambos resultados sin modelos adicionales. Penaliza documentos que solo aparecen en una búsqueda y eleva los que son relevantes en ambas. |

#### 🎯 ¿Por qué esta combinación es ideal para el ámbito legal?
- **📉 Reducción de Context Poisoning:** Al exigir coherencia dual (keyword + semántica), se filtran automáticamente versiones derogadas, jurisprudencia no vinculante o textos con alta similitud pero distinto alcance legal.
- **⚡ Latencia optimizada:** RRF se ejecuta en milisegundos en CPU, sin necesidad de llamadas extra a APIs ni carga de modelos de reranking.
- **🔍 Trazabilidad y auditoría:** Es posible rastrear qué términos activaron BM25 y qué contexto aportó FAISS, facilitando la validación profesional y el cumplimiento de estándares de transparencia jurídica.
- **💰 Costo controlado:** Elimina la dependencia de servicios de reranking de terceros, manteniendo todo el pipeline local o con una única llamada a DeepSeek.

> ⚖️ **Conclusión técnica:** Mariano no se conforma con `"parecer relevante"`. Está diseñado para **recuperar lo correcto, en el contexto exacto, con fundamento trazable**. La capa de recuperación híbrida es el núcleo que transforma un chatbot genérico en una herramienta de apoyo jurídico confiable y lista para producción.




## 📸 Project Demo

<div align="center">

| Document Upload Interface         | AI Chat Interface                 |
| --------------------------------- | --------------------------------- |
| ![Screenshot 1](utils/photo1.png) | ![Screenshot 2](utils/photo2.png) |

| Legal Analysis Results            | Report Generation                 |
| --------------------------------- | --------------------------------- |
| ![Screenshot 3](utils/photo3.png) | ![Screenshot 4](utils/photo4.png) |

</div>

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  RAG Pipeline    │────│  DeepSeek R1    │
│   (frontend.py) │    │ (rag_pipeline.py)│    │   via Groq      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐             │
         └──────────────│ Vector Database  │─────────────┘
                        │(vector_database.py)│
                        │   FAISS Index    │
                        └──────────────────┘
```

## 📁 Project Structure

```
AI-Lawyer---RAG-with-DeepSeek-R1/
├── 📄 frontend.py              # Streamlit UI application
├── 🔧 rag_pipeline.py          # RAG implementation with DeepSeek R1
├── 🗄️ vector_database.py       # FAISS vector database management
├── 📋 requirements.txt         # Python dependencies
├── 📖 README.md               # Project documentation
├── 🖼️ utils/                   # Screenshots and utilities
│   ├── photo1.png
│   ├── photo2.png
│   ├── photo3.png
│   └── photo4.png
└── 📁 .streamlit/             # Streamlit configuration (if exists)
    └── config.toml
```

## 🛠️ Technologies Used

| Technology                | Purpose                     | Version |
| ------------------------- | --------------------------- | ------- |
| **DeepSeek R1**           | Advanced AI reasoning model | Latest  |
| **Groq API**              | High-speed LLM inference    | -       |
| **LangChain**             | LLM application framework   | 0.1+    |
| **Streamlit**             | Web application framework   | 1.28+   |
| **FAISS**                 | Vector similarity search    | Latest  |
| **pdfplumber**            | PDF text extraction         | Latest  |
| **Sentence Transformers** | Text embeddings             | Latest  |

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Groq API key
- Git

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/bigdata5911/AI-Lawyer---RAG-with-DeepSeek-R1
```

```bash
cd AI-Lawyer---RAG-with-DeepSeek-R1
```

### 2️⃣ Set Up Virtual Environment

**On macOS/Linux:**

```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```bash
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

Or set it as an environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

## 🚀 Usage

### Running Locally

1. **Start the application:**

```bash
streamlit run frontend.py
```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload a legal document** (PDF format)

4. **Ask questions** about the document using natural language

5. **Download reports** generated by the AI analysis

### Example Queries

- "What are the key terms and conditions in this contract?"
- "Summarize the main legal obligations for each party"
- "What are the potential risks mentioned in this document?"
- "Explain the termination clauses in simple terms"

## 📜 How It Works

### 1. Document Processing

- **Upload**: User uploads PDF legal documents
- **Extraction**: Text is extracted using pdfplumber
- **Chunking**: Documents are split into manageable sections

### 2. Vector Database Creation

- **Embedding**: Text chunks are converted to vector embeddings
- **Indexing**: FAISS creates searchable vector index
- **Storage**: Vectors are stored for efficient retrieval

### 3. Query Processing

- **User Input**: Legal questions are received via Streamlit interface
- **Retrieval**: Relevant document sections are found using vector similarity
- **Context**: Retrieved information provides context for AI response

### 4. AI Response Generation

- **DeepSeek R1**: Advanced reasoning model processes query and context
- **Groq API**: High-speed inference for real-time responses
- **Structured Output**: Responses are formatted for legal clarity

### 5. Report Generation

- **Analysis**: AI generates comprehensive document analysis
- **Formatting**: Results are structured in professional format
- **Download**: Users can download PDF reports

## 🔑 API Configuration

### Groq API Setup

1. **Get API Key**: Visit [Groq Console](https://console.groq.com/) and create an account
2. **Generate Key**: Create a new API key in your dashboard
3. **Configure**: Add the key to your environment variables or `.env` file

### Supported Models

- `deepseek-r1-distill-llama-70b` (Recommended)
- `deepseek-r1-distill-qwen-32b`
- Other DeepSeek R1 variants available via Groq

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub:**

```bash
git add .
```

```bash
git commit -m "Deploy AI Lawyer application"
```

```bash
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Visit [Streamlit Cloud](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Set `GROQ_API_KEY` in Streamlit Secrets
   - Click **Deploy!**

### Environment Variables for Deployment

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_groq_api_key_here"
```

### Alternative Deployment Options

- **Docker**: Containerize the application
- **Heroku**: Deploy with Procfile
- **AWS/GCP**: Cloud platform deployment
- **Local Server**: Run on dedicated hardware

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to functions
- Include unit tests for new features
- Update documentation as needed

## 🎯 Future Improvements

### Short Term

- [ ] **Multi-format Support**: Add DOCX, TXT, and HTML document support
- [ ] **Batch Processing**: Handle multiple documents simultaneously
- [ ] **Advanced Search**: Implement semantic search with filters
- [ ] **User Authentication**: Add user accounts and document history

### Medium Term

- [ ] **Legal Database Integration**: Connect to legal precedent databases
- [ ] **Citation Tracking**: Automatic legal citation generation
- [ ] **Multi-language Support**: Support for non-English legal documents
- [ ] **API Endpoints**: RESTful API for programmatic access

### Long Term

- [ ] **Real-time Collaboration**: Multi-user document analysis
- [ ] **Legal Workflow Integration**: Connect with legal practice management tools
- [ ] **Advanced Analytics**: Document comparison and trend analysis
- [ ] **Mobile Application**: Native mobile app development

## 📊 Performance Metrics

- **Response Time**: < 3 seconds for typical queries
- **Accuracy**: 90%+ for factual legal information retrieval
- **Document Size**: Supports PDFs up to 50MB
- **Concurrent Users**: Optimized for 10+ simultaneous users

## 🔒 Security & Privacy

- **Data Privacy**: Documents are processed locally and not stored permanently
- **API Security**: Secure API key management
- **No Data Retention**: User documents are not retained after session
- **Encryption**: All API communications are encrypted

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepSeek** for the advanced reasoning model
- **Groq** for high-speed inference infrastructure
- **Streamlit** for the excellent web framework
- **LangChain** for LLM application tools
- **FAISS** for efficient vector search

---
=======
# Mariano-LegRAG-IA
Mariano es un chatbot legal potenciado por inteligencia artificial que utiliza Generación Aumentada por Recuperación (RAG) con el modelo DeepSeek R1 para ofrecer razonamiento jurídico avanzado y análisis preciso de documentos legales. 
>>>>>>> e8721b74d2c25ef43d2d4cb8110b634211ea567e
