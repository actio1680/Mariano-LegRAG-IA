# ============================================================
# Mariano LegRAG IA - Interfaz Streamlit
# ============================================================
import os
import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st

from vector_database import (
    index_pdf,
    upload_pdf,
    advanced_hybrid_search,
    get_all_chunks_with_metadata,
)
from rag_pipeline import answer_query, llm_model
from gestion_documentos import GestorIndice


# ------------------------------------------------------------
# Rutas absolutas (portables)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).parent
PDFS_DIR = BASE_DIR / "pdfs"
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "db_faiss"
ESTADO_FILE = BASE_DIR / "estado_documentos.json"


# ------------------------------------------------------------
# Configuración de la página
# ------------------------------------------------------------
st.set_page_config(page_title="Mariano LegRAG IA", page_icon="⚖️", layout="centered")


# ------------------------------------------------------------
# Estilos
# ------------------------------------------------------------
st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: #E0E0E0;
            font-family: Arial, sans-serif;
        }
        .stTextArea textarea {
            font-size: 14px;
            border-radius: 10px;
            padding: 12px;
            border: 2px solid #0b5394;
            background-color: #1E1E1E;
            color: white;
        }
        .stButton button {
            background-color: #0b5394;
            color: white;
            border-radius: 12px;
            padding: 12px 25px;
            font-size: 14px;
            font-weight: bold;
            transition: 0.3s;
            box-shadow: 0px 4px 10px rgba(11, 83, 148, 0.3);
        }
        .stButton button:hover {
            background-color: #083b6b;
        }
        .stChatMessage {
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            background-color: #1E1E1E;
            box-shadow: 2px 2px 10px rgba(255, 255, 255, 0.1);
            color: #E0E0E0;
        }
        .file-name-error {
            font-size: 12px;
            color: #f44336;
            margin: 2px 0;
        }
        .file-name-success {
            font-size: 12px;
            color: #4CAF50;
            margin: 2px 0;
        }
        .file-name-pending {
            font-size: 12px;
            color: #FFC107;
            margin: 2px 0;
        }
        .progress-text {
            font-size: 12px;
            color: #81C784;
            margin-top: -8px;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Estado de sesión
# ------------------------------------------------------------
if "user_queries" not in st.session_state:
    st.session_state.user_queries = []
if "ai_responses" not in st.session_state:
    st.session_state.ai_responses = []
if "uploaded_files_list" not in st.session_state:
    st.session_state.uploaded_files_list = []
if "failed_pdfs" not in st.session_state:
    st.session_state.failed_pdfs = []
if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False
if "aviso_descartado" not in st.session_state:
    st.session_state.aviso_descartado = False


# ------------------------------------------------------------
# Gestor de índice
# ------------------------------------------------------------
gestor = GestorIndice()


# ------------------------------------------------------------
# Utilidades de detección de estado persistente
# ------------------------------------------------------------
def hay_indice_en_disco() -> bool:
    return VECTORSTORE_DIR.exists() or ESTADO_FILE.exists()


def hay_pdfs_en_disco() -> list:
    if not PDFS_DIR.exists():
        return []
    return [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]


def limpiar_todo():
    """Borra índice, estado, PDFs y limpia session_state."""
    gestor.limpiar_indice()

    if PDFS_DIR.exists():
        for pdf in os.listdir(PDFS_DIR):
            if pdf.endswith(".pdf"):
                os.remove(PDFS_DIR / pdf)

    st.session_state.uploaded_files_list = []
    st.session_state.failed_pdfs = []
    st.session_state.documents_processed = False
    st.session_state.user_queries = []
    st.session_state.ai_responses = []
    st.session_state.aviso_descartado = True


# ------------------------------------------------------------
# Utilidad: generar el historial como texto
# ------------------------------------------------------------
def generar_historial_txt() -> str:
    lineas = []
    lineas.append("=" * 70)
    lineas.append("MARIANO LEGRAG IA - HISTORIAL DE CONSULTAS")
    lineas.append("=" * 70)
    lineas.append("")
    lineas.append(f"Fecha de descarga: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lineas.append(f"Total de consultas: {len(st.session_state.user_queries)}")
    lineas.append("=" * 70)
    lineas.append("")

    for i, (pregunta, respuesta) in enumerate(
        zip(st.session_state.user_queries, st.session_state.ai_responses), 1
    ):
        lineas.append("")
        lineas.append("=" * 70)
        lineas.append(f"CONSULTA N° {i}")
        lineas.append("=" * 70)
        lineas.append("")
        lineas.append("📝 PREGUNTA:")
        lineas.append("-" * 40)
        lineas.append(str(pregunta))
        lineas.append("")
        lineas.append("⚖️ RESPUESTA:")
        lineas.append("-" * 40)
        lineas.append(str(respuesta))
        lineas.append("")
        lineas.append("~" * 70)

    lineas.append("")
    lineas.append("=" * 70)
    lineas.append("FIN DEL HISTORIAL")
    lineas.append("=" * 70)
    lineas.append("")
    return "\n".join(lineas)


# ------------------------------------------------------------
# Sidebar: gestión de documentos
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🗂️ Gestión")
    st.markdown("### 📄 Documentos")

    # --- Aviso de sesión anterior ---
    if (
        not st.session_state.aviso_descartado
        and hay_indice_en_disco()
        and not st.session_state.uploaded_files_list
    ):
        pdfs_disco = hay_pdfs_en_disco()
        st.warning(
            "⚠️ **Hay información de una sesión anterior.**\n\n"
            f"Índice vectorial: {'sí' if VECTORSTORE_DIR.exists() else 'no'}\n\n"
            f"PDFs en carpeta: {len(pdfs_disco)}\n\n"
            "Puedes continuar con esa información o limpiarla para empezar de cero."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Continuar", use_container_width=True):
                st.session_state.uploaded_files_list = pdfs_disco
                st.session_state.documents_processed = True
                st.session_state.aviso_descartado = True
                st.rerun()
        with col2:
            if st.button("🗑️ Limpiar", use_container_width=True):
                limpiar_todo()
                st.success("✅ Todo limpiado. Puedes empezar de cero.")
                st.rerun()
        st.markdown("---")

    # --- Botón limpiar todo ---
    if st.button("🗑️ Limpiar documentos cargados e índice", use_container_width=True):
        limpiar_todo()
        st.success("✅ Todo limpiado: índice y PDFs eliminados")
        st.rerun()

    # --- Botón recargar carpeta ---
    if st.button("🔄 Recargar documentos de la carpeta", use_container_width=True):
        if not PDFS_DIR.exists():
            st.error("❌ La carpeta 'pdfs' no existe")
        else:
            pdfs_disco = [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]

            if not pdfs_disco:
                st.warning("📭 No hay PDFs en la carpeta 'pdfs'")
            else:
                # Detectar huérfanos
                huerfanos = gestor.pdfs_huerfanos(pdfs_disco)
                if huerfanos:
                    st.warning(
                        f"⚠️ {len(huerfanos)} PDF(s) huérfano(s): su índice sigue vivo "
                        "aunque el archivo ya no está en disco. Pulsa **Limpiar** si "
                        "quieres eliminarlos."
                    )

                # Indexar solo los que no estén ya
                nuevos = 0
                saltados = 0

                barra = st.progress(0.0)
                texto = st.empty()
                total_pdfs = len(pdfs_disco)

                for idx_pdf, pdf in enumerate(pdfs_disco, start=1):
                    file_path = PDFS_DIR / pdf

                    if gestor.ya_indexado(str(file_path)):
                        if pdf not in st.session_state.uploaded_files_list:
                            st.session_state.uploaded_files_list.append(pdf)
                        saltados += 1
                        barra.progress(idx_pdf / total_pdfs)
                        texto.markdown(
                            f"<p class='progress-text'>📄 {pdf} (ya indexado)</p>",
                            unsafe_allow_html=True,
                        )
                    else:
                        def _cb(valor, mensaje, _pdf=pdf, _idx=idx_pdf):
                            global_val = ((_idx - 1) + valor) / total_pdfs
                            barra.progress(min(global_val, 1.0))
                            texto.markdown(
                                f"<p class='progress-text'>📄 {_pdf} — {mensaje}</p>",
                                unsafe_allow_html=True,
                            )

                        index_pdf(str(file_path), progress_callback=_cb)
                        if pdf not in st.session_state.uploaded_files_list:
                            st.session_state.uploaded_files_list.append(pdf)
                        nuevos += 1
                        barra.progress(idx_pdf / total_pdfs)

                barra.empty()
                texto.empty()

                st.session_state.documents_processed = True
                gestor.guardar_estado()

                if nuevos == 0:
                    st.info(f"📚 {saltados} documento(s) ya estaban indexados.")
                else:
                    st.success(
                        f"✅ {nuevos} nuevo(s) indexado(s), {saltados} ya existían."
                    )

                st.rerun()

    # --- Lista actual de PDFs ---
    st.markdown("#### Lista cargada:")
    if PDFS_DIR.exists():
        pdfs = [f for f in os.listdir(PDFS_DIR) if f.endswith(".pdf")]
        if pdfs:
            for pdf in pdfs:
                st.text(f"📄 {pdf}")
            st.caption(f"Total: {len(pdfs)} documento(s)")
        else:
            st.info("📭 No hay documentos en la carpeta")
    else:
        st.info("📁 Carpeta 'pdfs' no existe")

    st.markdown("---")
    st.markdown("### 📣 Historial de consultas")

    if st.session_state.user_queries and st.session_state.ai_responses:
        contenido = generar_historial_txt()
        st.download_button(
            label="📥 Descargar historial de consultas",
            data=contenido,
            file_name=f"historial_consultas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.info("📭 No hay consultas para descargar")


# ------------------------------------------------------------
# Encabezado principal
# ------------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #0b5394;'>Mariano LegRAG IA</h1>
    <p style='text-align: center; font-size: 18px; color: #E0E0E0;'>
        Un chatbot de razonamiento legal basado en RAG usando IA.
    </p>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Carga de archivos
# ------------------------------------------------------------
uploaded_files = st.file_uploader(
    "📂 Subir documentos legales (PDFs)",
    type="pdf",
    accept_multiple_files=True,
)

if uploaded_files:
    for f in uploaded_files:
        if f.name in st.session_state.failed_pdfs:
            st.markdown(
                f"<p class='file-name-error'>❌ {f.name}</p>",
                unsafe_allow_html=True,
            )
        elif f.name in st.session_state.uploaded_files_list:
            st.markdown(
                f"<p class='file-name-success'>✅ {f.name}</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<p class='file-name-pending'>🔄 {f.name}</p>",
                unsafe_allow_html=True,
            )

    new_files = [
        f for f in uploaded_files if f.name not in st.session_state.uploaded_files_list
    ]

    if new_files:
        exitosos = 0
        fallidos = 0

        total_nuevos = len(new_files)
        barra_up = st.progress(0.0)
        texto_up = st.empty()

        for idx_file, uploaded_file in enumerate(new_files, start=1):
            file_path = upload_pdf(uploaded_file)

            # Si ya estaba indexado (mismo nombre y misma fecha), no reindexar
            if gestor.ya_indexado(file_path):
                st.session_state.uploaded_files_list.append(uploaded_file.name)
                barra_up.progress(idx_file / total_nuevos)
                continue

            def _cb_subida(valor, mensaje, _name=uploaded_file.name, _idx=idx_file):
                global_val = ((_idx - 1) + valor) / total_nuevos
                barra_up.progress(min(global_val, 1.0))
                texto_up.markdown(
                    f"<p class='progress-text'>📄 {_name} — {mensaje}</p>",
                    unsafe_allow_html=True,
                )

            resultado = index_pdf(file_path, progress_callback=_cb_subida)

            if resultado is None:
                st.session_state.failed_pdfs.append(uploaded_file.name)
                fallidos += 1
            else:
                st.session_state.uploaded_files_list.append(uploaded_file.name)
                if uploaded_file.name in st.session_state.failed_pdfs:
                    st.session_state.failed_pdfs.remove(uploaded_file.name)
                exitosos += 1

            barra_up.progress(idx_file / total_nuevos)

        barra_up.empty()
        texto_up.empty()

        gestor.guardar_estado()
        st.session_state.documents_processed = True

        if fallidos > 0:
            st.warning(
                f"⚠️ Procesados: {exitosos} correctos, {fallidos} fallidos "
                "(no se pudo leer el texto)"
            )
        else:
            st.success(f"✅ {exitosos} documento(s) procesados correctamente")

        st.rerun()
    else:
        st.info("📚 Todos los documentos ya están procesados. Puedes hacer preguntas.")


# ------------------------------------------------------------
# Historial de chat (render persistente)
# ------------------------------------------------------------
for pregunta, respuesta in zip(
    st.session_state.user_queries, st.session_state.ai_responses
):
    with st.chat_message("user"):
        st.write(pregunta)
    with st.chat_message("assistant", avatar="⚖️"):
        st.write(respuesta)


# ------------------------------------------------------------
# Entrada del usuario
# ------------------------------------------------------------
user_query = st.text_area(
    "💬 Envíame tu consulta:",
    height=120,
    placeholder="Coloca tu consulta aquí...",
)

if st.button("🔍 Preguntar a Mariano"):
    if not user_query.strip():
        st.warning("⚠️ Escribe una consulta antes de preguntar.")
    elif not st.session_state.uploaded_files_list:
        st.error("❌ Sube al menos un PDF antes de preguntar.")
    else:
        with st.spinner("⚡ Analizando documentos y generando respuesta..."):
            hybrid_results = advanced_hybrid_search(user_query, k=8)

            if hybrid_results:
                from langchain_core.documents import Document

                context_docs = [
                    Document(page_content=text, metadata={"score": score})
                    for text, score in hybrid_results
                ]
                response = answer_query(
                    documents=context_docs, model=llm_model, query=user_query
                )
            else:
                response = (
                    "No se encontraron documentos relevantes para tu consulta."
                )

            st.session_state.user_queries.append(user_query)
            st.session_state.ai_responses.append(response)

        st.rerun()


# ------------------------------------------------------------
# Créditos
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 12px; padding: 10px 0;'>
        <b>Mariano LegRAG IA</b> — Proyecto desarrollado por <b>William Atencio Becerra</b>.<br>
        © 2026 Actio1680. MIT License.
    </div>
    """,
    unsafe_allow_html=True,
)
