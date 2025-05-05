from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from typing import TypedDict
from langgraph.graph import StateGraph
from langchain.schema import SystemMessage, HumanMessage
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_tavily import TavilySearch
from langchain.tools import Tool

# Configuración inicial
load_dotenv()
api_key = os.getenv("API_KEY")
api_key_tavily = os.getenv("TAVILY_API_KEY")
model = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, temperature=0)

class AgentState(TypedDict):
    input: str
    tool_used: str
    output: str
    next_step: str
    thought_process: list  # Nuevo campo para registrar el proceso de pensamiento

def decide_tool(state: AgentState) -> AgentState:
    pregunta = state["input"]
    print("\n🤔 PROCESO DE DECISIÓN")
    print(f"Analizando la pregunta: '{pregunta}'")
    
    prompt = [
        SystemMessage(content="""Eres un asistente que elige la mejor herramienta según la consulta.
        Explica tu razonamiento paso a paso antes de decidir."""),
        HumanMessage(content=f'''
        Dada la siguiente pregunta: "{pregunta}", ¿cuál herramienta debería usar?
        
        **NOTA**
        - Siempre que hables de Windsurf me tienes que leer el pdf
        - Explica tu razonamiento
        
        Al final, responde solo con el nombre exacto de la herramienta.
        ''')
    ]
    
    respuesta_completa = model(prompt).content.strip()
    print("\n💭 Razonamiento del agente:")
    print(respuesta_completa)
    
    # Extraer la decisión final (última línea)
    decision = respuesta_completa.split('\n')[-1].lower()
    
    print(f"\n🎯 Decisión final: {decision}")
    
    if "pdf" in decision:
        return {
            "next_step": "usar_pdf",
            "thought_process": [respuesta_completa]
        }
    elif "internet" in decision:
        return {
            "next_step": "usar_web",
            "thought_process": [respuesta_completa]
        }
    else:
        return {
            "next_step": "fin",
            "thought_process": [respuesta_completa]
        }

class BusquedaPDF:
    def __init__(self, pdf_paths):
        print("\n📚 INICIALIZANDO BÚSQUEDA EN PDF")
        try:
            docs = []
            for path in pdf_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Archivo no encontrado: {path}")
                loader = PyMuPDFLoader(path)
                docs.extend(loader.load())
                print(f"✅ Cargado: {path}")
            
            print("\n🔄 Procesando documentos...")
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            self.docs_fragmentados = splitter.split_documents(docs)
            print(f"📝 Fragmentos creados: {len(self.docs_fragmentados)}")
            
            print("\n🧠 Creando embeddings...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            print("🔍 Construyendo índice FAISS...")
            self.vectorstore = FAISS.from_documents(self.docs_fragmentados, self.embeddings)
            
            print("⚙️ Configurando cadena de QA...")
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=model,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            print("✨ Sistema de búsqueda PDF listo!")
            
        except Exception as e:
            print(f"❌ Error en inicialización: {str(e)}")
            raise

    def run(self, query: str) -> str:
        print(f"\n🔎 BÚSQUEDA EN PDF")
        print(f"Consulta: '{query}'")
        try:
            print("⏳ Buscando documentos relevantes...")
            result = self.qa_chain.invoke({"query": query})
            
            if not result["source_documents"]:
                print("❌ No se encontraron documentos relevantes")
                return "No se encontró información relevante en los documentos."
            
            print("\n📑 Documentos encontrados:")
            sources = []
            for doc in result["source_documents"]:
                source = f"- {doc.metadata['source']} (página {doc.metadata.get('page', 'N/A')})"
                sources.append(source)
                print(source)
            
            return f"{result['result']}\n\nFuentes:\n" + "\n".join(sources)
            
        except Exception as e:
            print(f"⚠️ Error en búsqueda: {str(e)}")
            return "Error al consultar los documentos."

def usar_pdf(state: AgentState) -> AgentState:
    print("\n📖 EJECUTANDO BÚSQUEDA EN PDF")
    query = state["input"]
    resultado = tool_pdf.run(query)
    return {
        "input": query,
        "tool_used": "busqueda_pdf",
        "output": resultado,
        "thought_process": state.get("thought_process", []) + ["Realizando búsqueda en PDF"]
    }

def busqueda_internet(query: str) -> str:
    print(f"\n🌐 BÚSQUEDA EN INTERNET")
    print(f"Consulta: '{query}'")
    
    print("⏳ Consultando Tavily...")
    output = tavily_tool.invoke({"query": query})
    resultados = output.get("results", [])
    
    if not resultados:
        print("❌ No se encontraron resultados")
        return "No se encontraron resultados relevantes en la búsqueda en línea."
    
    print(f"✅ Encontrados {len(resultados)} resultados")
    contenido = "\n\n".join([res["content"] for res in resultados[:3] if "content" in res])
    return contenido

def usar_web(state: AgentState) -> AgentState:
    print("\n🔍 EJECUTANDO BÚSQUEDA WEB")
    query = state["input"]
    resultado = tool_web.run(query)
    return {
        "input": query,
        "tool_used": "busqueda_internet",
        "output": resultado,
        "thought_process": state.get("thought_process", []) + ["Realizando búsqueda en Internet"]
    }

# Configuración de herramientas
print("\n🛠️ CONFIGURANDO HERRAMIENTAS")
rutas_pdfs = ["Investigación de WindSurf.pdf", "nke-10k-2023.pdf"]
print(f"📚 PDFs configurados: {rutas_pdfs}")
buscador_pdf = BusquedaPDF(rutas_pdfs)

print("\n🌐 Configurando búsqueda web...")
tavily_tool = TavilySearch(max_results=5, topic="general")

tool_pdf = Tool(
    name="busqueda_pdf",
    func=buscador_pdf.run,
    description="Busca información en los documentos PDF cargados."
)

tool_web = Tool(
    name="busqueda_internet",
    func=busqueda_internet,
    description="Realiza búsquedas en Internet para información actualizada."
)

# Configuración del grafo
print("\n🔄 CONFIGURANDO GRAFO DE DECISIÓN")
graph = StateGraph(AgentState)

print("➕ Añadiendo nodos...")
graph.add_node("decision", decide_tool)
graph.add_node("usar_pdf", usar_pdf)
graph.add_node("usar_web", usar_web)
graph.add_node("fin", lambda state: state)

print("🎯 Configurando punto de entrada...")
graph.set_entry_point("decision")

print("🔀 Configurando transiciones...")
graph.add_conditional_edges(
    "decision",
    lambda state: state.get("next_step", "fin"),
    {
        "usar_pdf": "usar_pdf",
        "usar_web": "usar_web",
        "fin": "fin"
    }
)

graph.add_edge("usar_pdf", "fin")
graph.add_edge("usar_web", "fin")

print("🔄 Compilando grafo...")
agent_executor = graph.compile()

# Interfaz de usuario
print("\n🤖 CHATBOT DE LANGGRAPH")
print("Escriba 'salir' para terminar.")

while True:
    pregunta = input("\n👤 Usuario: ")
    
    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("\n👋 Fin de la conversación.")
        break
    
    print("\n🤖 Procesando...")
    entrada_agente = {
        "input": pregunta,
        "tool_used": "none",
        "output": "",
        "thought_process": []
    }
    
    resultado = agent_executor.invoke(entrada_agente)
    
    print("\n🎯 RESULTADO FINAL")
    print("=" * 50)
    print("💭 Proceso de pensamiento:")
    for thought in resultado.get("thought_process", []):
        print(thought)
    print("\n📝 Respuesta:")
    print(resultado["output"])
    print(f"\n🔧 Herramienta usada: {resultado['tool_used']}")
    print("=" * 50)
