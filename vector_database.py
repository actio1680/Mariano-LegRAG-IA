# ============================================================
# Mariano LegRAG IA - Base de datos vectorial
# ============================================================
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from bm25_retriever import BM25Retriever
from rrf_score import reciprocal_rank_fusion
import os
from gestion_documentos import GestorIndice

# Inicializar gestor
gestor = GestorIndice()

pdfs_directory = 'pdfs/'


# ------------------------------------------------------------
# Utilidades de archivos
# ------------------------------------------------------------
def upload_pdf(file):
    if not os.path.exists(pdfs_directory):
        os.makedirs(pdfs_directory)
    file_path = os.path.join(pdfs_directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path


def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    return documents


def create_chunks(documents, file_name):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        add_start_index=True
    )
    text_chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(text_chunks):
        chunk.metadata["source"] = file_name
        chunk.metadata["chunk_id"] = i

    return text_chunks


def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name="wilfredomartel/embeddinggemma-300m-legal-spanish-200k-v2"
    )
    return embedding_model


embedding_model = get_embedding_model()
FAISS_DB_PATH = "vectorstore/db_faiss"


# ------------------------------------------------------------
# Carga y consulta interna
# ------------------------------------------------------------
def _cargar_db():
    if os.path.exists(FAISS_DB_PATH):
        return FAISS.load_local(
            FAISS_DB_PATH,
            embedding_model,
            allow_dangerous_deserialization=True,
        )
    return None


def _ids_de_pdf(faiss_db, file_name):
    ids = []
    if faiss_db is None:
        return ids
    docstore = faiss_db.docstore._dict
    for doc_id, doc in docstore.items():
        if doc.metadata.get("source") == file_name:
            ids.append(doc_id)
    return ids


# ------------------------------------------------------------
# Indexación
# ------------------------------------------------------------
def remove_pdf_from_index(file_name):
    faiss_db = _cargar_db()
    if faiss_db is None:
        return 0
    ids = _ids_de_pdf(faiss_db, file_name)
    if ids:
        faiss_db.delete(ids)
        faiss_db.save_local(FAISS_DB_PATH)
    return len(ids)


def index_pdf(file_path, progress_callback=None):
    if progress_callback:
        progress_callback(0.05, "Cargando documento...")

    documents = load_pdf(file_path)
    file_name = os.path.basename(file_path)

    if progress_callback:
        progress_callback(0.20, "Creando fragmentos...")

    text_chunks = create_chunks(documents, file_name)

    if progress_callback:
        progress_callback(
            0.35,
            f"Generando embeddings de {len(text_chunks)} fragmentos...",
        )

    faiss_db = _cargar_db()

    if faiss_db is None:
        faiss_db = FAISS.from_documents(text_chunks, embedding_model)
    else:
        ids_viejos = _ids_de_pdf(faiss_db, file_name)
        if ids_viejos:
            faiss_db.delete(ids_viejos)
        faiss_db.add_documents(text_chunks)

    if progress_callback:
        progress_callback(0.90, "Guardando índice...")

    faiss_db.save_local(FAISS_DB_PATH)
    gestor.guardar_estado()

    if progress_callback:
        progress_callback(1.0, "Listo")

    return faiss_db


# ------------------------------------------------------------
# Consulta
# ------------------------------------------------------------
def retrieve_docs(query, file_name):
    faiss_db = FAISS.load_local(
        FAISS_DB_PATH,
        embedding_model,
        allow_dangerous_deserialization=True,
    )
    retrieved_docs = faiss_db.similarity_search(query, k=15)
    filtered_docs = [
        doc for doc in retrieved_docs if doc.metadata.get("source") == file_name
    ]
    return filtered_docs


def get_all_chunks_texts():
    faiss_db = _cargar_db()
    if faiss_db is None:
        return []
    return [doc.page_content for doc in faiss_db.docstore._dict.values()]


def get_all_chunks_with_metadata():
    faiss_db = _cargar_db()
    if faiss_db is None:
        return []
    return [doc for doc in faiss_db.docstore._dict.values()]


def listar_pdfs_indexados():
    faiss_db = _cargar_db()
    if faiss_db is None:
        return []
    nombres = set()
    for doc in faiss_db.docstore._dict.values():
        src = doc.metadata.get("source")
        if src:
            nombres.add(src)
    return sorted(nombres)


# ------------------------------------------------------------
# Búsqueda híbrida
# ------------------------------------------------------------
def advanced_hybrid_search(query, k=20):
    faiss_db = _cargar_db()
    if faiss_db is None:
        return []

    all_texts = get_all_chunks_texts()
    if not all_texts:
        return []

    bm25 = BM25Retriever(all_texts)
    bm25_results = bm25.retrieve(query, k=k * 2)
    semantic_results = faiss_db.similarity_search_with_score(query, k=20)
    semantic_list = [(doc.page_content, score) for doc, score in semantic_results]
    final_results = reciprocal_rank_fusion([bm25_results, semantic_list], k=60)

    return final_results[:k]


def advanced_hybrid_search_with_filter(query, file_name, k=10):
    results = advanced_hybrid_search(query, k=k * 2)
    all_chunks = get_all_chunks_with_metadata()
    text_to_metadata = {doc.page_content: doc.metadata for doc in all_chunks}

    filtered_results = []
    for text, score in results:
        metadata = text_to_metadata.get(text, {})
        if metadata.get("source") == file_name:
            filtered_results.append((text, score, metadata))

    return filtered_results[:k]