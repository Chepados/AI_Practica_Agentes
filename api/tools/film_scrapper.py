import os

import requests

from dotenv import get_key
from os import getenv
import pandas as pd
from langchain.tools import tool
from rich import print as rprint



if getenv("TMDB_API_KEY"):
    print("La api_key de TMDB se tomó de las variables de entorno.")
    TMDB_API_KEY = getenv("TMDB_API_KEY")
elif get_key(".env", "TMDB_API_KEY"):
    print("La api_key de TMDB se tomó del archivo .env.")
    TMDB_API_KEY = get_key(".env", "TMDB_API_KEY")
else:
    print("No se encontró clave para lena api de TMDB.")
    TMDB_API_KEY = None



def search_movie(string: str) -> str:
    """
    Busca una película en la base de datos de TMDB y devuelve un diccionario de python con la información relevante de todas las películas que coincidan con la búsqueda. La información relevante incluye el título, la sinopsis, la fecha de lanzamiento, la valoración media, el número de valoraciones, la ruta del poster y la ruta del backdrop.
    """  

    url = f"https://api.themoviedb.org/3/search/movie?query={string}&include_adult=true&language=es-ES&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    response_df = pd.DataFrame(response.json()['results'])[["title", "overview", "release_date", "vote_average", "vote_count", "poster_path", "backdrop_path"]]
    return response_df.to_dict(orient="records")


if __name__ == "__main__":
    entrada = input("Introudce el nombre de una película para buscar: ")
    rprint(search_movie(entrada))

