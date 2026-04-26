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



from tools import search_movie, search_torrent, get_torrent_from_link, get_available_torrent_files, download_torrent_file, get_torrent_client_status

CONTEXT = """
Eres un agente conversacional para gestionar búsquedas y descargas de películas.

## HERRAMIENTAS DISPONIBLES:

1. **search_movie**: Busca películas en TMDB. Devuelve título, sinopsis, fecha, valoración, poster y backdrop.
   
2. **search_torrent**: Encuentra links de descarga de torrents. (Recuerda poner el título en castellano y usar keywords simples *MUY IMPORTANTE busca solo las palabras clave del título y asegurate de que la ortografia es correcta*).
   
3. **get_torrent_from_link**: Descarga el archivo .torrent desde un link.

4. **get_available_torrent_files**: Lista los archivos .torrent disponibles para iniciar su descarga.

5. **download_torrent_file**: Inicia la descarga de una película usando un archivo .torrent dado su nombre.

6. **get_torrent_client_status**: Muestra el estado de los torrents en descarga, incluyendo nombre, velocidad, progreso, tamaño y estado.


## FLUJO DE TRABAJO:

- Cuando te pidan informacion de una película DEBES buscarla con search_movie.
- Cuando te pidan opciones de descarga buscaras con search_torrent SOLO PALABRAS CLAVE e interpretaras los resultados dandole al usuario de manera ordenada las opciones más prometedores
según sin se adaptan a lo que buscaba el usuario y que el almacenamiento no sea excesivo, en caso de que no encuentres ningún resultado prueba con una palábra clave más general es prioridad que al menos muestres algún resultado.
- Cuando el usuario haya seleccionado la película que quiere descargar usa el link que te devolvió search_torrent para lanzar get_torrent_from_link y descargar el .torrent correspondiente.
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
            model="qwen/qwen3-32b",
        )

        #self.llm = ChatGoogleGenerativeAI(
        #    model="gemini-3.1-pro-preview"
        #)



        self.checkpointer = InMemorySaver()

        self.agent = create_agent(
            model=self.llm,
            checkpointer=self.checkpointer,
            system_prompt=CONTEXT,
            tools = [search_movie, search_torrent, get_torrent_from_link, get_available_torrent_files, download_torrent_file, get_torrent_client_status]
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
