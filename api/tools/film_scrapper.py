import requests
import pandas as pd
from langchain.tools import tool

# Vamos a usar la api de TMDB
# AUTENTICACION

url = "https://api.themoviedb.org/3/authentication"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NmY0ZmZlODYxMGQ0NTI4OTYwYzMwNzJjYjJkMjEwOCIsIm5iZiI6MTc3NjU5MDI3Ni42OTI5OTk4LCJzdWIiOiI2OWU0OWRjNDlkNzcyYzkyYTE5NDBiNzYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.OyxOsN-7AU_LmwgfyxEgKiEeXAtwX2PiH-IMjzhmah0"
}

response = requests.get(url, headers=headers)

print(response.text)

@tool
def search_movie(string: str) -> str:
    """
    Busca una película en la base de datos de TMDB y devuelve un json con la información relevante de todas las películas que coincidan con la búsqueda. La información relevante incluye el título, la sinopsis, la fecha de lanzamiento, la valoración media, el número de valoraciones, la ruta del poster y la ruta del backdrop.
    """  

    url = f"https://api.themoviedb.org/3/search/movie?query={string}&include_adult=true&language=es-ES&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NmY0ZmZlODYxMGQ0NTI4OTYwYzMwNzJjYjJkMjEwOCIsIm5iZiI6MTc3NjU5MDI3Ni42OTI5OTk4LCJzdWIiOiI2OWU0OWRjNDlkNzcyYzkyYTE5NDBiNzYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.OyxOsN-7AU_LmwgfyxEgKiEeXAtwX2PiH-IMjzhmah0"
    }

    response = requests.get(url, headers=headers)
    response_df = pd.DataFrame(response.json()['results'])[["title", "overview", "release_date", "vote_average", "vote_count", "poster_path", "backdrop_path"]]
    return response_df.to_json(orient="records")