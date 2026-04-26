from dotenv import get_key
from os import getenv
from rich import print as rprint
import pandas as pd

if not getenv("TMDB_API_KEY"):
    print("La api_key de TMDB se tomó de las variables de entorno.")
    TMDB_API_KEY = get_key(".env", "TMDB_API_KEY")
elif get_key(".env", "TMDB_API_KEY"):
    print("La api_key de TMDB se tomó del archivo .env.")
    TMDB_API_KEY = get_key(".env", "TMDB_API_KEY")
else:
    print("No se encontró clave para lena api de TMDB.")
    TMDB_API_KEY = None



class ProfileManager:
    def __init__(self):

        self.profiles = dict()

        import requests

        url = "https://api.themoviedb.org/3/genre/movie/list?language=es"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_KEY}"
        }

        response = requests.get(url, headers=headers).json()["genres"]
        response = pd.DataFrame(response)
        response.set_index("id", inplace=True)

        self.genres_df = response


    def create_profile(self, name: str):
        self.profiles[name] = {}


if __name__ == "__main__":
    manager = ProfileManager()