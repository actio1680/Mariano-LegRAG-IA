# 📖 Manual de Usuario — Mariano LegRAG IA

**Mariano** es un asistente legal que lee tus documentos PDF y responde preguntas sobre ellos usando inteligencia artificial.

---

## 🎯 ¿Qué puedes hacer con Mariano?

| Puedes... | Ejemplo |
|-----------|---------|
| **Consultar contratos** | "¿Cuáles son las obligaciones del arrendatario?" |
| **Analizar sentencias** | "Resume los argumentos del demandante." |
| **Revisar normas** | "¿Qué dice el Artículo 74 sobre plazos?" |
| **Identificar riesgos** | "¿Qué cláusulas podrían ser problemáticas?" |

---

## 🖥️ Cómo se ve Mariano

La pantalla tiene **tres zonas**:

- **Barra lateral (izquierda):** gestión de documentos y descarga del historial.
- **Área principal (derecha):** subir PDFs y hacer preguntas.
- **Chat:** las respuestas aparecen como burbujas de conversación.

---

## 🚀 Guía paso a paso

### Paso 1 — Subir tus documentos

1. En el área principal, haz clic en **"📂 Upload legal documents (PDFs)"**.
2. Selecciona uno o varios PDFs.
3. Mariano los procesará automáticamente. Verás una **barra de progreso**.

Iconos que verás:

| Icono | Significado |
|:-----:|-------------|
| 🔄 | Procesando... |
| ✅ | Listo para consultar |
| ❌ | No se pudo leer (PDF escaneado o dañado) |

> **⏱️ Tiempo de espera:** la primera vez que subes un PDF, la indexación tarda varios minutos. Los PDFs de 300 páginas pueden tardar 10–20 minutos. Es normal.

### Paso 2 — Hacer una pregunta

1. Escribe tu pregunta en **"💬 Realiza tú pregunta"**.
2. Pulsa **"🔍 Preguntar a Mariano"**.
3. Espera unos segundos. La respuesta aparece en el chat, citando el artículo o cláusula.

### Paso 3 — Descargar el historial

1. En la barra lateral, ve a **"📣 Historial de consultas"**.
2. Pulsa **"📥 Descargar historial de consultas"**.
3. Se descargará un `.txt` con todas tus preguntas y respuestas.

> **Consejo:** descarga el historial antes de cerrar la app, porque el chat de la sesión se pierde al cerrar la pestaña.

---

## 🗂️ Gestión de documentos: qué hace cada botón

En el panel lateral tienes **tres botones**. Aquí están explicados en detalle.

### 🔄 Recargar documentos de la carpeta

**Qué hace:** carga todos los PDFs que estén en la carpeta `pdfs/` del proyecto.

**Cuándo usarlo:**

- Si añadiste PDFs manualmente a la carpeta.
- Si borraste un PDF y quieres actualizar la lista.

**Detalle importante:** Mariano **no reindexa** los PDFs que ya estaban procesados. Solo indexa los nuevos. Por eso es rápido.

### 🗑️ Limpiar documentos cargados e índice

**Qué hace:** borra **todo**: PDFs, índice interno y el historial de la conversación.

**Cuándo usarlo:**

- Cuando quieras empezar de cero.
- Cuando cambies de caso o expediente.
- Cuando quieras liberar espacio en disco.

**⚠️ Advertencia:** esta acción es **irreversible**. Si quieres conservar el historial, descárgalo antes.

### 📥 Descargar historial de consultas

**Qué hace:** guarda tus preguntas y respuestas en un archivo `.txt` con formato legible.

**Cuándo usarlo:** cuando termines una sesión de análisis y quieras guardar el resultado.

---

## 🧠 Lo que debes saber sobre el borrado y la memoria

Mariano tiene **tres memorias** que se comportan distinto. Es importante que lo entiendas para no llevarte sorpresas.

| Memoria | Qué guarda | ¿Se borra al cerrar? |
|---------|-----------|----------------------|
| **Chat de la sesión** | Tus preguntas y respuestas actuales | ✅ **Sí** — se pierde al cerrar la pestaña |
| **Índice de documentos** | El "conocimiento" extraído de tus PDFs | ❌ **No** — sigue en disco |
| **Registro de PDFs procesados** | Qué documentos ya fueron leídos | ❌ **No** — sigue en disco |

### Preguntas frecuentes

**¿Si cierro la app, pierdo todo?**

**No.** Los PDFs y el índice siguen guardados en tu computadora. Solo se borra la conversación actual. Cuando vuelvas a abrir la app, Mariano te avisará: *"Hay información de una sesión anterior"*.

**¿Qué pasa al reabrir la app?**

Verás un aviso con dos opciones:

- **▶️ Continuar** → reutiliza los documentos que ya están indexados. Puedes preguntar de inmediato sin volver a procesar.
- **🗑️ Limpiar** → borra todo y empieza de cero.

**¿Si subo el mismo PDF dos veces?**

Mariano lo detecta por el hash del archivo. **No lo reprocesa.** Ahorra tiempo y evita duplicados en el índice.

**¿Si borro un PDF de la carpeta `pdfs/`?**

Pasa algo importante: **el índice sigue teniendo su contenido**. Mariano puede seguir respondiendo con fragmentos de ese PDF aunque el archivo ya no esté. Te avisará:

> *"PDF huérfano: su índice sigue vivo aunque el archivo ya no está en disco."*

Para eliminarlo de verdad, pulsa **"🗑️ Limpiar documentos cargados e índice"**.

**¿Qué pasa cuando pulso "Limpiar"?**

Se borran **los PDFs, el índice y el historial**. Es la única forma de eliminar completamente un documento del sistema.

---

## 🆘 Si algo no funciona

| Problema | Qué hacer |
|----------|-----------|
| ❌ "No se pudo leer el PDF" | Es un PDF escaneado (imagen). Mariano no tiene OCR. Prueba con uno que tenga texto seleccionable. |
| ⏱️ Tarda mucho al subir | Es normal con documentos grandes. Mira la barra de progreso; el proceso sigue avanzando. |
| 🤔 "No se encontraron documentos relevantes" | Reformula la pregunta con términos del documento. Por ejemplo, si el contrato dice "arrendatario", no preguntes por "inquilino". |
| 💤 La app no responde | Revisa la ventana de PowerShell donde arrancaste Streamlit. Anota el error y repórtalo. |
| 🔄 "Todos los documentos ya están procesados" | Mariano detectó que los PDFs ya están en el índice. Puedes preguntar sin más. |

---

## 💡 Consejos para mejores respuestas

1. **Sé específico.** En lugar de "háblame del contrato", pregunta "¿cuál es el plazo de pago de la cláusula quinta?".
2. **Usa los términos del documento.** Si el contrato dice "arrendatario", no preguntes por "inquilino".
3. **Cita artículos o cláusulas** si los conoces. "¿Qué dice el Artículo 74?" funciona mejor que "¿qué dice sobre plazos?".
4. **Haz preguntas de seguimiento.** Mariano mantiene el contexto de la conversación.
5. **Sube solo lo necesario.** Un expediente específico da mejores respuestas que 20 PDFs mezclados.

---

## 🔒 Privacidad

- Tus PDFs se procesan **en tu computadora**.
- Solo los fragmentos **estrictamente necesarios** se envían al modelo.
- La comunicación va **cifrada** (TLS).
- Tus documentos **no se almacenan** en servidores externos.

---

## ⚙️ Requisitos técnicos

- **Sistema operativo:** Windows, macOS o Linux.
- **Python 3.10 o superior.**
- **RAM:** 8 GB recomendados.
- **Espacio en disco:** ~2 GB para el proyecto + espacio para tus PDFs.
- **Conexión a internet:** necesaria para consultar el modelo.

---

## 👤 Autor

**William Atencio Becerra** — © 2026 Actio1680. Todos los derechos liberados.
