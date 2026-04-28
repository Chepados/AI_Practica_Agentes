import fastapi
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

import langchain
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from langchain_groq import ChatGroq



from tools import *
from langchain_core.tools import Tool, StructuredTool

search_movie_tool = StructuredTool.from_function(search_movie)

get_available_modules_tool = StructuredTool.from_function(get_available_modules)
search_torrent_with_module_tool = StructuredTool.from_function(search_torrent_with_module)
get_torrent_from_link_with_module_tool = StructuredTool.from_function(get_torrent_from_link_with_module)
get_available_torrent_files_tool = StructuredTool.from_function(get_available_torrent_files)
download_torrent_file_tool = StructuredTool.from_function(download_torrent_file)
get_torrent_client_status_tool = StructuredTool.from_function(get_torrent_client_status)
remove_torrent_file_tool = StructuredTool.from_function(remove_torrent_file)

profile_manager = ProfileManager()

create_profile_tool = StructuredTool.from_function(profile_manager.create_profile)
delete_profile_tool = StructuredTool.from_function(profile_manager.delete_profile)
set_preference_tool = StructuredTool.from_function(profile_manager.set_preference)
get_preferences_tool = StructuredTool.from_function(profile_manager.get_preferences)
del_preference_tool = StructuredTool.from_function(profile_manager.del_preference)
get_genres_tool = StructuredTool.from_function(profile_manager.get_genres)
recomend_movies_tool = StructuredTool.from_function(profile_manager.recomend_movies)

get_cartelera_madrid_tool = StructuredTool.from_function(get_cartelera_madrid)


CONTEXT = """
Eres un agente conversacional para gestionar búsquedas y descargas de películas.

## HERRAMIENTAS DISPONIBLES:

1. **search_movie_tool**: Busca películas en TMDB. Devuelve título, sinopsis, fecha, valoración, poster y backdrop.
   
2. **get_modules_tool**: Devuelve una lista de los módulos de scrapping de torrents disponibles.

2. **search_torrent_with_module_tool**: Encuentra links de descarga de torrents. (Recuerda poner el título en castellano y usar keywords simples *MUY IMPORTANTE busca solo las palabras clave del título y asegurate de que la ortografia es correcta*), toma como entrada el nombre de la película y el módulo de scrapping a usar. NO LA USES SIN HABER USADO ANTES get_modules PARA SABER QUE MÓDULOS DE SCRAPPING TIENES DISPONIBLES, SI USAS UN MÓDULO QUE NO EXISTE TE DARÁ ERROR Y NO PODRÁS DESCARGAR LA PELÍCULA, ASÍ QUE RECUERDA USAR get_modules ANTES DE USAR ESTA HERRAMIENTA PARA SABER QUÉ MÓDULOS DE SCRAPPING TIENES DISPONIBLES. 
   
3. **get_torrent_from_link_with_module_tool**: Descarga el archivo .torrent desde un link, toma como entrada el link obtenido en search_torrent_with_module y el módulo de scrapping a usar. RECUERDA NO USARLA SI NO HAS USADO ANTES get_modules.

4. **get_available_torrent_files_tool**: Lista los archivos .torrent disponibles para iniciar su descarga. 

5. **download_torrent_file_tool**: Inicia la descarga de una película usando un archivo .torrent dado su nombre.

6. **get_torrent_client_status_tool**: Muestra el estado de los torrents en descarga, incluyendo nombre, velocidad, progreso, tamaño y estado.

7. **remove_torrent_file_tool**: Eliminar un torrent de qbittorrent por su hash. Solo borra el torrent de qbittorrent, no borra el archivo de torrent del sistema. El `hash` es un identificador único para cada torrent. Se puede obtener de la función `get_torrent_client_status_tool`, que devuelve una lista de torrents con su información, incluyendo el hash.

Ademas tienes una serie de herramientas para gestionar perfiles de usuario y recomendaciones basadas en géneros:

8. **create_profile_tool**: Crea un nuevo perfil de usuario para recomendaciones.
9. **delete_profile_tool**: Elimina un perfil de usuario existente.
10. **set_preference_tool**: Establece una preferencia de género para un perfil (una preferencia es un genero y una puntuacion)
11. **get_preferences_tool**: Obtiene las preferencias de género de un perfil específico.
12. **del_preference_tool**: Elimina una preferencia de género de un perfil específico.
13. **get_genres_tool**: Devuelve una lista de los géneros disponibles para establecer preferencias. (Recuerda usarla para saber que géneros puedes usar a la hora de establecer preferencias para los perfiles)
14. **recomend_movies_tool**: Devuelve una lista de recomendaciones de películas para un perfil específico, basándose en las preferencias establecidas para ese perfil.

Ademas tienes una tool para obtener la cartelera de Madrid:

15. **get_cartelera_madrid_tool**: Devuelve una lista de las películas actualmente en cartelera en Madrid, incluyendo su información obtenida de TMDB.


## FLUJO DE TRABAJO:

- Cuando te pidan informacion de una película DEBES buscarla con search_movie.
- Cuando te pidan opciones de descarga buscaras con search_torrent_with_module SOLO PALABRAS CLAVE e interpretaras los resultados dandole al usuario de manera ordenada las opciones más prometedores
según sin se adaptan a lo que buscaba el usuario y que el almacenamiento no sea excesivo, en caso de que no encuentres ningún resultado prueba con una palábra clave más general es prioridad que al menos muestres algún resultado.
- Cuando el usuario haya seleccionado la película que quiere descargar usa el link que te devolvió search_torrent_with_module para lanzar get_torrent_from_link_with_module y descargar el .torrent correspondiente.
- Si es usuario te pide hacer un listado de los torrents que tiene disponibles para iniciar descarga recuerda usar get_available_torrent_files.
- Pasale el nombre de uno de estos archivos a download_torrent_file para iniciar la descarga
- Si el usuario te pide conocer el status o alguna informacion sobre alguna descarga en curso o todas recuerda darle siempre la información más actualzada posible haciendo uso de get_torrent_client_status.

## REGLAS DE FORMATO (CRÍTICO):

- SIEMPRE usa <br> entre cada elemento de una lista
- Respuestas cortas y directas
- Bullet points obligatorios con <br>


* Aquí te dejo algunas opciones: <br>* Spider-Man (2002) <br>* Spider-Man: Homecoming (2017) <br>* Spider-Man: No Way Home (2021)

## COMPORTAMIENTO:

- Sé conciso: máximo 3-4 líneas por respuesta
- Pregunta antes de ejecutar acciones
- Usa emojis ocasionalmente para claridad: 🎬 🔍 ⬇️

RECUERDA: Cada elemento de lista DEBE tener <br> al final. Sin excepciones. esto es MUY importante, si haces una enumeración simpre tienes que estar bien formateada con <br> al final de cada elemento, si no lo haces así el usuario no podrá entender la información que le estás dando y se confundirá, así que por favor asegúrate de seguir esta regla de formato en cada respuesta que des.
"""

class Agent_handler:
    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
        )

        #self.llm = ChatGoogleGenerativeAI(
        #    model="gemini-3.1-pro-preview"
        #)



        self.checkpointer = InMemorySaver()

        self.agent = create_agent(
            model=self.llm,
            checkpointer=self.checkpointer,
            system_prompt=CONTEXT,
            tools = [search_movie_tool, search_torrent_with_module_tool, get_torrent_from_link_with_module_tool, get_available_modules_tool, get_available_torrent_files_tool, download_torrent_file_tool, get_torrent_client_status_tool, create_profile_tool, delete_profile_tool, set_preference_tool, get_preferences_tool, del_preference_tool, get_genres_tool, recomend_movies_tool, get_cartelera_madrid_tool, remove_torrent_file_tool]
        )

        

    def generate_response(self, msg_content):
        
        messages = [
            HumanMessage(content=msg_content)
        ]

        response = self.agent.invoke(
            input={
                "messages":messages,
            },
            config={
                    "configurable" : {
                        "thread_id":"1"
                    }
            }
            
        )

        response_content = response["messages"][-1].content

        return response_content


agent_handler = Agent_handler()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


messages = []

class msg_object(BaseModel):
    content : str

@app.post("/send")
def send(msg : msg_object):

    messages.append(msg.content)
    response_content = agent_handler.generate_response(msg.content)


    return {
        "status": "OK",
        "msgs": messages,
        "response_content" : response_content
    }

