# AI_Practica_Agentes
## Home_cinema_Server

### Despliegue

Para empezar debemos de configurar las api keys necesarias.

En la carpeta /api hay que crear un archivo .env con el siguiente contenido:

```
TMDB_API_KEY=tu_api_key_de_tmdb
GROQ_API_KEY=tu_api_key_de_groq
```

En esa misma carpeta, en el archivo main_simple_graph.py, hay que configurar la variable OPENAI_API_KEY con tu api key de OpenAI. On Caso contrario, quitar la parte comentada que corresponde a GROQ (gratuito) lo cual dará un funcionamiento correcto siempre y cunado no se superen los límites de uso gratuitos.

Despliegue del contenedor:

```
docker compose -f docker/docker-compose.yml up --build
```

De manerá que podremos acceder a los siguientes servicios:

- web_app_agente: http://localhost:80
- api_docs: http://localhost:8000
- Servidor_Jellyfin: http://localhost:8096
- Web QbitTorrent: http://localhost:8082

### Demo en vídeo

Se incluye una demostración funcional 

**[Ver video telegram en YouTube](https://youtu.be/pBDz8zvv5Yc)**
**[Ver video del agente en YouTube](https://youtu.be/pBDz8zvv5Yc)**
---

## Módulo de Alexa

Este módulo incluye un  **Alexa Skill** que permite consultar información de películas mediante comandos de voz.

La arquitectura se ha dividido en dos módulos principales para separar responsabilidades y hacer el código más limpio y reutilizable:

- **`scrapper_pelicula.py`**: contiene toda la lógica de extracción de datos. Dado el nombre de una película, consulta la API de TMDB y devuelve un diccionario estructurado con la información relevante, como:
  - nota
  - número de votos
  - sinopsis
  - director
  - duración
  - año de estreno
  - géneros

Además, este script puede ejecutarse directamente desde línea de comandos.


- **`lambda_function.py`**: contiene la lógica de la skill de Alexa. Este módulo se encarga de gestionar la interacción con el usuario, interpretar qué información está solicitando y utilizar el scrapper para obtener los datos necesarios antes de construir la respuesta hablada.

De esta forma, Alexa actúa como interfaz conversacional, mientras que el scrapper centraliza la lógica de acceso a datos.

### Funcionamiento de la skill

La skill se basa en el concepto de **intents** y **slots** propios de Alexa:

- Un **intent** representa la intención del usuario (por ejemplo, pedir la nota de una película o preguntar por su director).
- Un **slot** representa la información variable dentro de esa petición, en este caso el nombre de la película.

Ejemplo:

> “¿Cuál es la nota de Interstellar?”

Alexa interpreta:

- Intent: `NotaPeliculaIntent`
- Slot: `pelicula = Interstellar`

La lambda recibe esa información, llama al scrapper con el título indicado y construye la respuesta correspondiente.

### Intents implementados

La skill incorpora varios intents específicos para cubrir las principales consultas que un usuario puede realizar sobre una película:

| Intent | Función |
|------|---------|
| `NotaPeliculaIntent` | Devuelve la puntuación media de la película junto con el número de valoraciones registradas. |
| `SinopsisPeliculaIntent` | Proporciona una breve descripción o sinopsis de la película consultada. |
| `DirectorPeliculaIntent` | Indica quién dirigió la película solicitada. |
| `DuracionPeliculaIntent` | Devuelve la duración total de la película en un formato legible para Alexa. |
| `VotosPeliculaIntent` | Informa del número total de votos o valoraciones que tiene la película en TMDB. |
| `YearPeliculaIntent` | Devuelve el año de estreno de la película consultada. |
| `InfoCompletaIntent` | Ofrece un resumen completo combinando varios campos: año, director, géneros, duración y nota. |

Además, se implementan varios intents estándar proporcionados por Alexa para mejorar la experiencia conversacional y el manejo de errores:

| Intent estándar | Función |
|---------------|---------|
| `AMAZON.HelpIntent` | Explica al usuario qué tipo de preguntas puede realizar dentro de la skill. |
| `AMAZON.CancelIntent` | Permite cancelar la interacción actual con la skill. |
| `AMAZON.StopIntent` | Finaliza la conversación con Alexa de forma controlada. |
| `AMAZON.FallbackIntent` | Se activa cuando Alexa no entiende correctamente la petición del usuario y ofrece orientación para reformularla. |

### Modelo de interacción JSON

Se incluye el archivo **`json_editor.json`** que contiene el modelo de interacción completo de Alexa (intents, utterances y configuración de slots).

Esto permite que cualquier persona pueda duplicar fácilmente la skill importando directamente este archivo en el **Alexa Developer Console**, sin necesidad de configurar manualmente cada intent.

### Demo en vídeo

Se incluye una demostración funcional de la skill en vídeo, subida en modo oculto a YouTube y accesible mediante enlace:

**[Ver video en YouTube](https://youtu.be/7Y1O1onFaCA)**