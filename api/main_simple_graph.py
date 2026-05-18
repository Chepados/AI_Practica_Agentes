from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import operator

from tools import *

search_movie_tool                  = StructuredTool.from_function(search_movie)
get_available_modules_tool         = StructuredTool.from_function(get_available_modules)
search_torrent_with_module_tool    = StructuredTool.from_function(search_torrent_with_module)
get_torrent_from_link_with_module_tool = StructuredTool.from_function(get_torrent_from_link_with_module)
get_available_torrent_files_tool   = StructuredTool.from_function(get_available_torrent_files)
download_torrent_file_tool         = StructuredTool.from_function(download_torrent_file)
get_torrent_client_status_tool     = StructuredTool.from_function(get_torrent_client_status)
remove_torrent_file_tool           = StructuredTool.from_function(remove_torrent_file)

profile_manager = ProfileManager()
create_profile_tool  = StructuredTool.from_function(profile_manager.create_profile)
delete_profile_tool  = StructuredTool.from_function(profile_manager.delete_profile)
set_preference_tool  = StructuredTool.from_function(profile_manager.set_preference)
get_preferences_tool = StructuredTool.from_function(profile_manager.get_preferences)
del_preference_tool  = StructuredTool.from_function(profile_manager.del_preference)
get_genres_tool      = StructuredTool.from_function(profile_manager.get_genres)
recomend_movies_tool = StructuredTool.from_function(profile_manager.recomend_movies)
get_cartelera_madrid_tool = StructuredTool.from_function(get_cartelera_madrid)

tools = [
    search_movie_tool, get_available_modules_tool, search_torrent_with_module_tool,
    get_torrent_from_link_with_module_tool, get_available_torrent_files_tool,
    download_torrent_file_tool, get_torrent_client_status_tool, remove_torrent_file_tool,
    create_profile_tool, delete_profile_tool, set_preference_tool, get_preferences_tool,
    del_preference_tool, get_genres_tool, recomend_movies_tool, get_cartelera_madrid_tool,
]

OPENAI_API_KEY="aqui pones tu api key"

llm_name = "gpt-4o-mini"
# llm             = ChatGroq(model=llm_name)

llm = ChatOpenAI(model=llm_name, openai_api_key=OPENAI_API_KEY)

llm_with_tools  = llm.bind_tools(tools)

SYNTH_PROMPT = """
Eres un nodo de síntesis dentro de un pipeline de LangGraph. Tu función es ejecutar 
las herramientas necesarias y devolver datos estructurados para un nodo formateador.

## TU ROL:
- NO generes respuestas conversacionales.
- Ejecuta las herramientas necesarias y filtra los resultados antes de devolverlos.
- Output: JSON limpio y filtrado. Nunca datos en bruto sin procesar.
- Si el usuario te hace una pregunta directa, genera un json estructurado cun una respuesta clara, e informa de tus capacidades al usuario para guiarlo.

## FILTRADO DE RESULTADOS (MUY IMPORTANTE):
- Cuando el usuario busque una película concreta, devuelve SOLO la coincidencia 
  más exacta con el título buscado. Una única película principal.
- Si hay ambigüedad (remake, saga), devuelve máximo 2-3 opciones MUY relevantes.
- DESCARTA resultados que sean documentales sobre la película, making-ofs, 
  cortometrajes relacionados, o títulos que solo contengan palabras del título buscado.
- Para cartelera o recomendaciones sí puedes devolver múltiples resultados (máx 6).

## HERRAMIENTAS DISPONIBLES:

**Películas:**
- search_movie_tool: Busca en TMDB. Del resultado, incluye SIEMPRE poster_url y 
  backdrop_url — son críticos para el formateador.

**Torrents:**
- get_available_modules_tool: OBLIGATORIO llamarla antes de cualquier operación con torrents.
- search_torrent_with_module_tool: Busca torrents. Solo palabras clave en castellano.
- get_torrent_from_link_with_module_tool: Descarga .torrent desde un link.
- get_available_torrent_files_tool: Lista .torrent disponibles para iniciar descarga.
- download_torrent_file_tool: Inicia descarga dado el nombre del archivo .torrent. Asegurate de que el nombre coincida exactamente con el listado de get_available_torrent_files_tool.
- get_torrent_client_status_tool: Estado actual de descargas (progreso, velocidad, hash...).
- remove_torrent_file_tool: Elimina torrent de qBittorrent por hash.

**Perfiles:**
- create_profile_tool / delete_profile_tool: Gestión de perfiles.
- get_genres_tool: Llámala antes de set_preference_tool para saber géneros válidos.
- set_preference_tool / get_preferences_tool / del_preference_tool: Gestión de preferencias.
- recomend_movies_tool: Recomendaciones basadas en perfil.

**Cartelera:**
- get_cartelera_madrid_tool: Películas en cartelera en Madrid con datos TMDB.

## REGLAS:
- Nunca uses search_torrent ni get_torrent_from_link sin llamar antes a get_available_modules.
- Si una herramienta falla, documéntalo en error_message y continúa.

"""


FORMAT_PROMPT_WEB = """
Eres un nodo formateador. Recibes un JSON y generas ÚNICAMENTE un fragmento HTML 
para insertarse dentro de un div de chat bubble. Sin <html>, <head>, <body> ni div raíz.

## LAYOUT BASE (siempre respetado):
- max-width: 460px. Nunca uses scroll horizontal.
- Estilos en <style> incrustado. Sin JS salvo animaciones CSS puras.
- Cuida el estilo debe de ser atractivo, legible, organizado, cor colores oscutos y estetica de tarjetas nunca html simple.

## LAYOUT SEGÚN INTENT:

**search_movie — UNA película principal:**
Si movies tiene 1 resultado (búsqueda directa):
  - Genera una tarjeta que incluya el poster y el backdrop, no te doy muchas indicaciones te dejo libertad,
  asegurate de hacer un diseño vistoso y llamativo incluyendo toda la informacion relevante de la peli,
  las disposiciones deben de ser horizontales


Si movies tiene 2-3 resultados (ambigüedad):
  - Lista horizontal de tarjetas compactas (poster pequeño + título + año + rating).
  - Pregunta al usuario cuál quiere.

**search_torrent:**
  - Tabla compacta: Nombre | Calidad |. Sin imágenes.
  - Dale un diseño vistoso y elegante. 

**torrent_status:**
  - Tarjeta por torrent: nombre, barra de progreso CSS (width: X%), velocidad, estado.

**cartelera / recommend:**
  - Grid Max 6 items.
  - Cada poster: imagen + título debajo. 

**other / error:**
  - Texto simple estilizado.

## REGLAS ABSOLUTAS:
- Recuerda para completar el link a una imagen usar siempre el formato completo: https://image.tmdb.org/t/p/w500/{poster_path} o backdrop_path.
- Si no hay poster_url ni backdrop_url, diseña sin imágenes (no pongas img tags rotos).
- Tu output es SOLO HTML. Sin texto fuera de las etiquetas.
- Genera el HTML puro para incrustar sin la coletilla '''html''' ni nada más IMPORTANTE.
- No generes estilos que sobreescriban el layout base solo la tarjeta que generes pero nada de fuera. Ni tampoco
otras etiquetas que hayas podido generar, asi que usa si puede estilos incrustados dentro del html siempre que peudas.
"""

FORMAT_PROMPT_TELEGRAM = """Eres un nodo formateador para un bot de Telegram.
Recibes un JSON y generas ÚNICAMENTE texto conversacional listo para mostrarle al usuario.

## REGLAS DE FORMATO:
- parse_mode: HTML de Telegram. Solo estas etiquetas: <b>, <i>, <code>, <pre>, <s>, <u>
- Máximo 4096 caracteres.
- Sin URLs, sin JSON, sin técnicismos. El usuario final lee esto directamente.
- Tono natural, directo y amigable. Como si fuera un asistente hablando.
- Usa emojis con criterio para organizar, no decorar en exceso.
- No incluyas CSS de ningún tipo, ni estilos. Solo texto con formato HTML básico.

## LAYOUT SEGÚN INTENT:

**search_movie — UNA película:**
Presenta la película como si se la estuvieras recomendando a alguien.
Incluye título, año, rating, géneros, duración, director y sinopsis resumida.
Cierra con una línea de opinión breve o gancho.

**search_movie — 2 o 3 resultados (ambigüedad):**
Di que encontraste varias opciones y lista cada una con título, año y rating.
Pregunta al usuario cuál quiere con naturalidad.

**search_torrent:**
Lista los resultados disponibles de forma limpia:
calidad, tamaño y semillas por opción. Pregunta cuál prefiere descargar.

**torrent_status:**
Informa del estado de cada descarga activa de forma clara:
nombre resumido, porcentaje, velocidad y estado. Tono informativo y breve.

**cartelera / recommend:**
Presenta hasta 6 títulos como una lista recomendada.
Cada uno en una línea: emoji de género + título + año + rating.

**error / other:**
Mensaje claro explicando qué pasó o respondiendo directamente. Sin tecnicismos.

## REGLAS ABSOLUTAS:
- SOLO texto. Sin JSON, sin URLs, sin bloques de código, sin explicaciones tuyas.
- Nunca uses etiquetas HTML que Telegram no soporte.
- Tu output es exactamente lo que el usuario verá en su chat."""

class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]  
    platform: str
    response: str  

def interaction_node(state: State) -> dict:
    messages = [SystemMessage(SYNTH_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}  

def decision_node(state: State) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool"
    return "formater"

def formater(state: State) -> dict:
    
    last_synthesis = state["messages"][-1]

    match state["platform"]:
        case "web":
            prompt = FORMAT_PROMPT_WEB
        case "telegram":
            prompt = FORMAT_PROMPT_TELEGRAM

    
    response = llm.invoke([SystemMessage(prompt), last_synthesis])

    return {"response": response.content} 


checkpointer = InMemorySaver()

graph = StateGraph(State) 
graph.add_node("interaction", interaction_node)
graph.add_node("tool_node", ToolNode(tools))  
graph.add_node("formater", formater)

graph.add_edge(START, "interaction")
graph.add_conditional_edges(
    "interaction",
    decision_node,
    {"tool": "tool_node", "formater": "formater"}
)
graph.add_edge("tool_node", "interaction")
graph.add_edge("formater", END)

agent = graph.compile(checkpointer=checkpointer) 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MsgObject(BaseModel):
    content: str

@app.post("/send")
def send(msg: MsgObject, thread_id: str = "1", platform: str = "web"):
    response = agent.invoke(
        {
            "messages": [HumanMessage(content=msg.content)],
            "platform": platform
        },
        config={"configurable": {"thread_id": thread_id}}
    )

    return {
        "status": "OK",
        "response_content": response["response"]  # ✅ Campo separado
    }