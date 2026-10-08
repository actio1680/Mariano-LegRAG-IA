# ============================================================
# Mariano LegRAG IA - Pipeline de razonamiento (DeepSeek)
# ============================================================
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit


# ------------------------------------------------------------
# Variables de entorno
# ------------------------------------------------------------
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")


# ------------------------------------------------------------
# Modelo de razonamiento (DeepSeek vía cliente OpenAI-compatible)
# ------------------------------------------------------------
llm_model = ChatOpenAI(
    model="deepseek-reasoner",
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0.3,
    max_tokens=8000,
)


# ------------------------------------------------------------
# Utilidad: unir documentos en un solo bloque de contexto
# ------------------------------------------------------------
def get_context(documents):
    return "\n\n".join([doc.page_content for doc in documents])


# ------------------------------------------------------------
# Prompt especializado en derecho peruano
# ------------------------------------------------------------
custom_prompt_template = """
Eres un asistente legal experto en derecho peruano.
Tu tarea es responder preguntas basándote estrictamente en el contexto proporcionado.

INSTRUCCIONES IMPORTANTES:
1. Tu respuesta debe ser COMPLETA y DETALLADA. No te cortes.
2. Si la pregunta tiene MÚLTIPLES aspectos (varios plazos,subtipos, varios requisitos), enumera TODOS.
3. Usa una lista numerada o viñetas para organizar la información.
4. No inventes información que no esté en el contexto.
5. Cuando cites el documento, menciona el artículo, cláusula o página si están disponibles.

Contexto legal:
{context}

Historial de la conversación:
{history}

Pregunta del usuario:
{question}
"""


# ------------------------------------------------------------
# Respuesta a una consulta
# ------------------------------------------------------------
def answer_query(documents, model, query, history=""):
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    response = chain.invoke(
        {"question": query, "context": context, "history": history}
    )

    if hasattr(response, "content"):
        return response.content
    elif isinstance(response, dict) and "content" in response:
        return response["content"]
    else:
        return str(response)


# ------------------------------------------------------------
# Reporte PDF descargable
# ------------------------------------------------------------
def generate_report(user_queries, ai_responses, pdf_path="MarianoAI_Reporte.pdf"):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Mariano LegRAG IA - Reporte de consultas")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, "Registro de la conversación con Mariano LegRAG IA.")

    y = 700
    max_width = 450
    line_height = 15

    for question, answer in zip(user_queries, ai_responses):
        c.setFont("Helvetica-Bold", 12)
        q_lines = simpleSplit(f"P: {question}", "Helvetica-Bold", 12, max_width)
        a_lines = simpleSplit(f"R: {answer}", "Helvetica", 12, max_width)

        for line in q_lines:
            c.drawString(100, y, line)
            y -= line_height

        c.setFont("Helvetica", 12)
        for line in a_lines:
            c.drawString(100, y, line)
            y -= line_height

        y -= 20

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750

    c.save()
    return pdf_path