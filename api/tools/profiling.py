from dotenv import get_key
from os import getenv
from rich import print as rprint
import pandas as pd
import requests


if getenv("TMDB_API_KEY"):
    print("La api_key de TMDB se tomó de las variables de entorno.")
    TMDB_API_KEY = get_key(".env", "TMDB_API_KEY")
elif get_key(".env", "TMDB_API_KEY"):
    print("La api_key de TMDB se tomó del archivo .env.")
    TMDB_API_KEY = get_key(".env", "TMDB_API_KEY")
else:
    print("No se encontró clave para lena api de TMDB.")
    TMDB_API_KEY = None


headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_KEY}"
    }




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
        """Crea un nuevo perfil con el nombre dado."""
        self.profiles[name] = {}

    def delete_profile(self, name: str):
        """Elimina el perfil con el nombre dado."""
        assert name in self.profiles.keys(), f"El perfil {name} no existe."
        del self.profiles[name]

    def set_preference(self, profile_name: str, genre_name: str, preference: int):
        """Establecer una preferencia para el recomendador. Debes especificar un perfil, un genero, y la nota mínimca que se le debe dar a una película para que se recomiende. La nota mínima debe ser un número entero entre 1 y 10."""
        assert profile_name in self.profiles.keys(), f"El perfil {profile_name} no existe."
        assert genre_name in self.genres_df["name"].values, f"El género {genre_name} no existe."
        assert preference in range(1, 11), f"La preferencia debe ser un número entero entre 1 y 10."

        self.profiles[profile_name][genre_name] = preference

    def get_preferences(self, profile_name: str) -> dict:
        """Obtener las preferencias de un perfil específico. Devuelve un diccionario con los géneros y las preferencias establecidas para ese perfil."""

        assert profile_name in self.profiles.keys(), f"El perfil {profile_name} no existe."
        return self.profiles[profile_name]
    
    def del_preference(self, profile_name: str, genre_name: str):
        """Eliminar una preferencia para el recomendador. Debes especificar un perfil y un genero."""

        assert profile_name in self.profiles.keys(), f"El perfil {profile_name} no existe."
        assert genre_name in self.genres_df["name"].values, f"El género {genre_name} no existe."

        del self.profiles[profile_name][genre_name]

    def recomend_movies(self, profile_name: str) -> list:
        """Devuelve una lista de recomendaciones de películas para un perfil específico. La recomendación se basa en las preferencias establecidas para ese perfil. Devuelve una lista de diccionarios con la información relevante de las películas recomendadas, ordenadas por popularidad de mayor a menor. La información relevante incluye el título, la sinopsis, la fecha de lanzamiento, la valoración media, el número de valoraciones, la ruta del poster y la ruta del backdrop."""


        full_recomendation_list = list()

        for genre_name, preference in self.profiles[profile_name].items():
        
            genre_id = self.genres_df[self.genres_df["name"] == genre_name].index[0]
            print(" Genre id:", genre_id)
            url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&vote_average.gte={preference}&with_genres={genre_id}"

            response = requests.get(url, headers=headers).json()["results"]
            full_recomendation_list.extend(response)

        return sorted(full_recomendation_list, key=lambda x: x["popularity"], reverse=True)[:10]

        

if __name__ == "__main__":
    manager = ProfileManager()
    manager.create_profile("Héctor")
    manager.set_preference("Héctor", "Acción", 9)
    manager.set_preference("Héctor", "Comedia", 7)
    rprint(manager.get_preferences("Héctor"))
    rprint(manager.recomend_movies("Héctor"))

    