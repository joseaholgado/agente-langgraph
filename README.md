# Agente Inteligente con LangGraph

Este repositorio contiene un **agente inteligente** desarrollado con LangGraph y LangChain que decide dinámicamente entre:

* **Búsqueda en PDFs locales**
* **Análisis de AST en formato JSON**
* **Búsquedas web en tiempo real**

---

## Estructura del Notebook

Archivo principal: `langgraph_agente_busqueda_explicado.ipynb`

### 1. Configuración Inicial

* Carga de variables de entorno (`.env`).
* Inicialización de la LLM de OpenAI (`ChatOpenAI`).

### 2. Búsqueda en PDFs (`BusquedaPDF`)

* **Carga**: `PyMuPDFLoader` para extraer texto de PDFs.
* **Fragmentación**: `RecursiveCharacterTextSplitter` divide el contenido en chunks.
* **Embeddings**: `HuggingFaceEmbeddings` crea vectores semánticos.
* **Vectorstore**: `FAISS` almacena y recupera vectores.
* **QA**: `RetrievalQA` responde consultas e incluye las fuentes.

### 3. Análisis de AST JSON (`BusquedaJSON`)

* Lee uno o varios archivos JSON que representan un AST.
* Construye un prompt que incluye el AST completo.
* El modelo lista las funciones (nombre y parámetros) y explica su propósito.

### 4. Búsqueda en Internet (`busqueda_internet`)

* Integra `TavilySearch` para obtener hasta 5 resultados.
* Procesa y formatea contenido relevante.

### 5. Agente LangGraph

* **Estado**: `AgentState` con campos `input`, `tool_used`, `output`, `next_step`.
* **Decisión**: regla por palabras clave para elegir PDF, JSON o web.
* **Nodos**: `decision`, `usar_pdf`, `usar_json`, `usar_web`, `fin`.
* **Ejecución**: invocación del `AgentExecutor` para respuestas interactivas.

---

## Requisitos

* Python 3.7+
* Dependencias (instalar con `pip install -r requirements.txt`):

  * langchain
  * langgraph
  * PyMuPDF
  * faiss-cpu
  * transformers
  * python-dotenv

---

## Uso

1. Crea un fichero `.env` con:

   ```bash
   API_KEY=tu_api_key_openai
   TAVILY_API_KEY=tu_api_key_tavily
   ```
2. Añade tus archivos PDF y el JSON del AST en el directorio del proyecto.
3. Abre el notebook `langgraph_agente_busqueda_explicado.ipynb` en Jupyter.
4. Ejecuta celda por celda y, al final, interactúa con el agente.

---

## Características Clave

* **Selección automática** de la herramienta adecuada.
* **Respuestas basadas en contexto**: muestra siempre las fuentes (PDF, ruta JSON o web).
* **Explicación de AST**: identifica y describe funciones en tu código.


