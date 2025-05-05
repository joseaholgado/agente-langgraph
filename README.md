# Agente Inteligente con LangGraph - Documentación

Este proyecto implementa un agente inteligente utilizando LangGraph que decide automáticamente entre buscar en documentos PDF locales o realizar búsquedas web para responder preguntas.

## Estructura del Notebook

### 1. Configuración Inicial
- **Archivo**: `langgraph_agente_busqueda_explicado.ipynb`
- **Descripción**: Configura el entorno inicial cargando las variables de entorno necesarias y las dependencias básicas.
- **Componentes principales**:
  - Carga de API keys para OpenAI y Tavily
  - Inicialización del modelo ChatOpenAI

### 2. Búsqueda en PDFs
- **Descripción**: Implementa la clase `BusquedaPDF` para manejar búsquedas en documentos PDF locales.
- **Funcionalidades**:
  - Carga de documentos PDF
  - Fragmentación de texto
  - Creación de embeddings usando HuggingFace
  - Almacenamiento vectorial con FAISS
  - Sistema de preguntas y respuestas con RetrievalQA

### 3. Herramienta de Búsqueda Web
- **Descripción**: Implementa la búsqueda web usando Tavily Search.
- **Características**:
  - Búsqueda en internet en tiempo real
  - Procesamiento de resultados
  - Integración con la API de Tavily
  - Límite de 5 resultados por búsqueda

### 4. Configuración de LangGraph
- **Descripción**: Define la lógica del agente usando LangGraph.
- **Componentes**:
  - Estado del agente (`AgentState`)
  - Función de decisión para elegir herramienta
  - Nodos para búsqueda en PDF y web
  - Configuración del grafo de decisión
  - Sistema de transiciones entre estados

### 5. Interfaz Interactiva
- **Descripción**: Implementa un chatbot interactivo para interactuar con el agente.
- **Funcionalidades**:
  - Loop interactivo de preguntas y respuestas
  - Manejo de salida del programa
  - Visualización de resultados y herramienta utilizada

## Características Especiales

1. **Decisión Inteligente**: El agente decide automáticamente qué herramienta usar basándose en la pregunta.
2. **Búsqueda en PDFs Mejorada**:
   - Manejo de errores robusto
   - Información detallada de fuentes
   - Fragmentación inteligente de documentos
3. **Búsqueda Web Optimizada**:
   - Resultados filtrados y relevantes
   - Integración con Tavily para búsquedas precisas

## Requisitos
- Python 3.x
- Dependencias listadas en el notebook:
  - langchain
  - langgraph
  - PyMuPDF
  - FAISS
  - HuggingFace Transformers
  - python-dotenv

## Uso
1. Configura las variables de entorno en un archivo `.env`:
   ```
   API_KEY=tu_api_key_openai
   TAVILY_API_KEY=tu_api_key_tavily
   ```
2. Asegúrate de tener los PDFs necesarios en el directorio del proyecto
3. Ejecuta el notebook celda por celda
4. Interactúa con el chatbot en la última celda

## Notas Importantes
- El agente siempre usará la búsqueda en PDF cuando se mencione "Windsurf"
- La búsqueda web se utiliza para información general y actualizada
- Los resultados incluyen las fuentes de información utilizadas
